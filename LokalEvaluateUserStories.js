const { LMStudioClient } = require("@lmstudio/sdk");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify");

// Das Modell für die Evaluierung
const evaluationModel = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf";

// Funktion zur Ausführung eines Prompts
async function evaluatePrompt(loadedModel, prompt) {
    const prediction = loadedModel.respond([
        { role: "system", content: "You are a helpful assistant that evaluates software development user stories." },
        { role: "user", content: prompt },
    ], {
        stop: ["## End of Evaluation", "End of Evaluation"],
    });

    let evaluation = "";
    for await (const text of prediction) {
        process.stdout.write(text);
        evaluation += text;
    }

    return evaluation.split("## End Evaluation")[0]; // Nur die erste Antwort zurückgeben
}

async function main() {
    const inputPromptsFile = path.join(__dirname, 'generated_evaluation_prompts.csv');
    const outputFile = path.join(__dirname, 'evaluated_user_stories.csv');

    const headers = ["Industry", "Title", "Model", "Criterion", "Evaluation"];
    const evaluatedData = [];

    // Laden Sie das Modell einmal zu Beginn
    const client = new LMStudioClient();
    const loadedModel = await client.llm.load(evaluationModel, { acceleration: "auto" });

    console.log(`Model ${evaluationModel} has been successfully loaded.`);

    fs.createReadStream(inputPromptsFile)
        .pipe(csv())
        .on("data", (row) => {
            if (row.Prompt && row.Prompt.replace(/\s/g, '').length > 10) {
                evaluatedData.push(row);
            } else {
                console.log(`Skipping row with insufficient Prompt: ${JSON.stringify(row)}`);
            }
        })
        .on("end", async () => {
            if (evaluatedData.length === 0) {
                console.log("No valid rows found in the input file.");
                return;
            }

            for (const [idx, row] of evaluatedData.entries()) {
                const { Industry, Title, Model, Criterion, Prompt } = row;

                console.log(`Evaluating user stories for ${Title} in ${Industry} (Model: ${Model}) using criterion: ${Criterion}... (${idx + 1}/${evaluatedData.length})`);

                let evaluation = await evaluatePrompt(loadedModel, Prompt);
                console.log(`Evaluation result for ${Title} using criterion: ${Criterion}:\n`, evaluation);

                evaluatedData[idx].Evaluation = evaluation;
            }

            // Write the evaluated data to the output CSV file
            const output = fs.createWriteStream(outputFile, { flags: "w" });
            const writer = stringify({ header: true, columns: headers });
            writer.pipe(output);
            evaluatedData.forEach(data => writer.write(data));
            writer.end();
            console.log(`User stories have been evaluated and saved to ${outputFile}`);
        });
}

main();
