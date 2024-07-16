const { LMStudioClient } = require("@lmstudio/sdk");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify");

const models = [
    "MaziyarPanahi/Llama-3-8B-Instruct-32k-v0.1-GGUF/Llama-3-8B-Instruct-32k-v0.1.Q5_K_M.gguf",
    "NousResearch/Nous-Hermes-2-Mistral-7B-DPO-GGUF/Nous-Hermes-2-Mistral-7B-DPO.Q6_K.gguf",
    "microsoft/Phi-3-mini-4k-instruct-gguf/Phi-3-mini-4k-instruct-q4.gguf",
    // Neues Modell hinzufügen
];

const TOKEN_LIMIT = 5600;
const REPEATED_CHAR_LIMIT = 7;

async function generateUserStoriesForModel(modelPath, prompts, writer, startIndex = 0) {
    const client = new LMStudioClient();
    const model = await client.llm.load(modelPath, {
        acceleration: "auto"
    });

    for (let i = startIndex; i < prompts.length; i++) {
        const prompt = prompts[i];
        console.log(`Processing prompt for ${prompt.Title} in ${prompt.Industry} using model ${modelPath}`);

        let userStories = "";
        let tokenCount = 0;
        let endlessLoopDetected = false;
        let repeatedCharDetected = false;

        try {
            const prediction = model.respond([
                { role: "system", content: "You are a skilled software developer responsible for translating a use case into a complete set of user stories." },
                { role: "user", content: prompt.Prompt },
            ]);

            for await (const text of prediction) {
                const tokens = text.split(/\s+/).length;
                tokenCount += tokens;
                userStories += text;
                process.stdout.write(text);

                // Check for repeated characters
                if (/(\w)\1{6,}/.test(text)) {
                    console.log('Repeated character detected. Aborting current generation.');
                    repeatedCharDetected = true;
                    break;
                }

                if (tokenCount > TOKEN_LIMIT) {
                    console.log('Endless loop detected. Aborting current generation.');
                    endlessLoopDetected = true;
                    break;
                }
            }

            if (!endlessLoopDetected && !repeatedCharDetected) {
                writer.write([prompt.Industry, prompt.Title, modelPath, userStories]);
            } else {
                console.log(`Retrying generation for ${prompt.Title} in ${prompt.Industry}`);
                await generateUserStoriesForModel(modelPath, [prompt], writer);
            }

        } catch (error) {
            console.error(`Error generating user stories for ${prompt.Title}: ${error}`);
        }
    }
}

async function main() {
    const promptsFile = path.join(__dirname, "..", "..", "data", "generated", "generated_prompts.csv");
    const prompts = [];

    fs.createReadStream(promptsFile)
        .pipe(csv())
        .on("data", (row) => {
            prompts.push(row);
        })
        .on("end", async () => {
            console.log("CSV file successfully processed");

            const outputDir = path.join(__dirname, "../../data", "generated");
            const outputFile = path.join(outputDir, "generated_user_stories.csv");
            if (!fs.existsSync(outputDir)) {
                fs.mkdirSync(outputDir, { recursive: true });
            }

            let lastRow = null;
            if (fs.existsSync(outputFile)) {
                const rows = [];
                fs.createReadStream(outputFile)
                    .pipe(csv())
                    .on('data', (row) => {
                        rows.push(row);
                    })
                    .on('end', async () => {
                        if (rows.length > 0) {
                            lastRow = rows[rows.length - 1];
                            console.log('Last row:', lastRow);
                        } else {
                            console.log('Empty CSV file or error reading rows.');
                        }
                        await processPrompts(lastRow, prompts, outputFile);
                    });
            } else {
                await processPrompts(lastRow, prompts, outputFile);
            }
        });
}

async function processPrompts(lastRow, prompts, outputFile) {
    let industry, title, model;
    let startIndex = 0;

    const output = fs.createWriteStream(outputFile, { flags: "a" });

    const writer = stringify({
        header: !fs.existsSync(outputFile) || !lastRow,
        columns: ["Industry", "Title", "Model", "User Stories"]
    });
    writer.pipe(output);

    if (lastRow) {
        [industry, title, model] = [lastRow.Industry, lastRow.Title, lastRow.Model];
        console.log(`Resuming from last entry - Industry: ${industry}, Title: ${title}, Model: ${model}`);
        if (!models.includes(model)) {
            console.log("Model not in the list. Starting from the beginning.");
            lastRow = null;
        } else {
            startIndex = prompts.findIndex(prompt => prompt.Industry === industry && prompt.Title === title);
            startIndex = startIndex === -1 ? 0 : startIndex + 1;

            // Überprüfe, ob die letzte Industry in beiden Dateien übereinstimmt
            if (prompts.length > 0 && prompts[prompts.length - 1].Industry === industry) {
                console.log("Last Industry matches. Starting from the beginning with the next model.");
                startIndex = 0;
                // Wechsele zum nächsten Modell und setze die Generierung fort
                const nextModelIndex = (models.indexOf(model) + 1) % models.length;
                for (const modelPath of models.slice(nextModelIndex)) {
                    await generateUserStoriesForModel(modelPath, prompts, writer, startIndex);
                }
                writer.end();
                return;
            }

            // Find the index of the next industry
            const currentIndustry = prompts[startIndex - 1].Industry;
            const nextIndustryIndex = prompts.findIndex((prompt, index) => index >= startIndex && prompt.Industry !== currentIndustry);
            if (nextIndustryIndex !== -1) {
                startIndex = nextIndustryIndex;
            } else {
                startIndex = prompts.length;  // Keine weitere Industry gefunden, alle Prompts wurden verarbeitet
            }

            console.log(`Resuming from index ${startIndex}`);
        }
    }

    if (startIndex < prompts.length) {
        for (const modelPath of models) {
            await generateUserStoriesForModel(modelPath, prompts.slice(startIndex), writer);
        }
    }

    writer.end();
    console.log("All prompts have been processed and user stories saved.");
}

main();
