const { LMStudioClient } = require("@lmstudio/sdk");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify");

// Modell, das verwendet werden soll
const modelPath = "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct.Q5_1.gguf";

// Kriterienliste
const criteria = [
    "Well-formed: The user story must include at least one role and one means.",
    "Atomic: The user story should express exactly one requirement.",
    "Minimal: The user story should contain only the role, means, and ends, with no additional information.",
    "Conceptually sound: The means should express concrete functionality and the ends should justify the need for this functionality.",
    "Problem-oriented: The user story should specify only the problem and not the solution.",
    "Unambiguous: The user story should not contain terms or abstractions that lead to multiple interpretations.",
    "Conflict-free: The user story should not contradict other user stories.",
    "Full sentence: The user story should be formulated as a complete sentence.",
    "Estimatable: The user story should not be so vaguely formulated that it is difficult to plan and prioritize.",
    "Unique: Each user story should be unique, avoiding duplicates.",
    "Uniform: All user stories in a specification should use the same format.",
    "Independent: The user story should be self-contained and not have inherent dependencies on other user stories.",
    "Complete: The implementation of a set of user stories should lead to a working application without missing essential steps."
];

const initialPromptTemplate = `
### Prompt:

You are a skilled software developer responsible for evaluating the quality of user stories. Evaluate the following user stories based on the given criterion, and explain your thought process step by step.

Use Case Context:
------Start of Use Case------
{use_case}
-------End of Use Case-------

User Stories:
------Start of User Stories------
{user_stories}
-------End of User Stories-------

Criterion: 
------Start of criterion------
{criterion}
-------End of criterion-------

Evaluate each user story individually within the context of the entire use case and the set of user stories. Provide a Yes or No response for each criterion and a short explanation if necessary of your reasoning for each response. Use the following format and stay in this format:
------Start of format------
Criterion: [Name of Criterion]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
(...rest of user stories with their evaluation in the same format as before)

Overall Result: [Yes/No]
Explanation: [Short Explanation of the overall result if necessary. Max 3 sentences]
End of Evaluation
-------End of format-------

Scores:
Yes - Criterion met
No - Criterion not met or partially met

Please evaluate the user stories based on the given criterion. Provide the evaluation for each user story in the same format as described and explain your thought process if necessary. Very Important: If you are finished with the format, write "End of Evaluation", as described and stay in the described Format.
`;

const followUpPromptTemplate = `
### Follow-Up:

Based on the previous evaluation, let's continue with the next criterion.

Use Case Context: {use_case}

User Stories: {user_stories}

The next criterion is: {criterion}

Please evaluate the user stories based on this criterion. Provide the evaluation for each user story in the same format as described and stay in this format.
------Start of format------
Criterion: [Name of Criterion]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation and thought process if necessary]
(...rest of user stories with their evaluation in the same format as before)

Overall Result: [Yes/No]
Explanation: [Short Explanation of the overall result if necessary. Max 3 sentences]
End of Evaluation
-------End of format-------
`;

function detectLoop(text) {
    const pattern = /(.)\1{4,}/; // Detect 5 or more consecutive repeating characters
    return pattern.test(text);
}

async function evaluateUseCase(model, useCase, userStories) {
    // Datei zum Speichern der generierten Bewertungen
    const outputFile = path.join(__dirname, "evaluated_by_Meta-Llama-3-8B-Instruct_user_stories.csv");
    const output = fs.createWriteStream(outputFile, { flags: "a" });

    // Initialize CSV writer with columns
    const writer = stringify({
        header: true,
        columns: ["Use Case", "User Stories", "Evaluation"]
    });
    writer.pipe(output);

    // Initiale Bewertung
    const initialPrompt = initialPromptTemplate
        .replace("{use_case}", useCase)
        .replace("{user_stories}", userStories)
        .replace("{criterion}", criteria[0]);

    const initialResponse = model.respond([
        { role: "system", content: "You are a helpful assistant that evaluates software development user stories." },
        { role: "user", content: initialPrompt }
    ]);

    let fullEvaluation = "";
    for await (const text of initialResponse) {
        process.stdout.write(text); // Echtzeit-Ausgabe in die Konsole
        fullEvaluation += text;
    }

    for (const criterion of criteria.slice(1)) {
        const followUpPrompt = followUpPromptTemplate
            .replace("{use_case}", useCase)
            .replace("{user_stories}", userStories)
            .replace("{criterion}", criterion);

        const followUpResponse = model.respond([
            { role: "system", content: "You are a helpful assistant that evaluates software development user stories." },
            { role: "assistant", content: fullEvaluation },
            { role: "user", content: followUpPrompt }
        ]);

        for await (const text of followUpResponse) {
            process.stdout.write(text); // Echtzeit-Ausgabe in die Konsole
            fullEvaluation += text;
        }
    }

    writer.write([useCase, userStories, fullEvaluation]);
    writer.end();
    console.log(`Evaluation complete and saved for use case: ${useCase}.`);
}

async function main() {
    const client = new LMStudioClient(); // Initialisierung des Clients

    const useCasesFile = path.join(__dirname, "generated_use_cases.csv");
    const userStoriesFile = path.join(__dirname, "generated_user_stories.csv");

    const useCasesDict = {};
    const rows = [];

    fs.createReadStream(useCasesFile)
        .pipe(csv())
        .on("data", (row) => {
            const { industry, title, description, actor, preconditions, trigger, use_case } = row;
            useCasesDict[title] = use_case;
        })
        .on("end", async () => {
            fs.createReadStream(userStoriesFile)
                .pipe(csv())
                .on("data", (row) => {
                    // Überprüfen, ob die Zeile Spaltenüberschriften enthält
                    if (row["Industry"] === "Industry" && row["Title"] === "Title" && row["Model"] === "Model" && row["User Stories"] === "User Stories") {
                        return; // Zeile überspringen
                    }
                    if (row["User Stories"].length > 10) {
                        rows.push(row);
                    }
                })
                .on("end", async () => {
                    console.log(`Loading model: ${modelPath}`);
                    const model = await client.llm.load(modelPath, {
                        acceleration: "auto"
                    });

                    for (const row of rows) {
                        const { Industry, Title, Model, "User Stories": userStories } = row;
                        const useCase = useCasesDict[Title] || "No use case found for this title";
                        console.log(`Evaluating user stories for ${Title} in ${Industry} (Model: ${modelPath})...`);

                        await evaluateUseCase(model, useCase, userStories);
                    }

                    console.log("Evaluation complete for all rows.");
                });
        });
}

main().catch(console.error);
