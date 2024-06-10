const { LMStudioClient } = require("@lmstudio/sdk");
const fs = require("fs");
const path = require("path");
const csv = require("csv-parser");
const { stringify } = require("csv-stringify");

// Liste der Modelle, die verwendet werden sollen
const models = [
    "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
    "RichardErkhov/google_-_gemma-1.1-7b-it-gguf/gemma-1.1-7b-it.Q2_K.gguf",
    "TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_S.gguf",
    "Qwen/Qwen2-7B-Instruct-GGUF/qwen2-7b-instruct-q5_0.gguf",
    // Füge hier weitere Modelle hinzu
    // "another-model-path",
];

async function generateUserStoriesForModel(modelPath, prompts) {
    // Create a client to connect to LM Studio, then load a model
    const client = new LMStudioClient();
    const model = await client.llm.load(modelPath, {
        acceleration: "auto"
    });

    // File to save the generated user stories
    const outputFile = path.join(__dirname, "generated_user_stories.csv");
    const output = fs.createWriteStream(outputFile, { flags: "a" });

    // Initialize CSV writer with columns
    const writer = stringify({
        header: true,
        columns: ["Industry", "Title", "Model", "User Stories"]
    });
    writer.pipe(output);

    for (const prompt of prompts) {
        console.log(`Processing prompt for ${prompt.Title} in ${prompt.Industry} using model ${modelPath}`);

        const prediction = model.respond([
            { role: "system", content: "You are a skilled software developer responsible for translating a use case into a complete set of user stories." },
            { role: "user", content: prompt.Prompt },
        ]);

        let userStories = "";
        for await (const text of prediction) {
            process.stdout.write(text);
            userStories += text;
        }

        writer.write([prompt.Industry, prompt.Title, modelPath, userStories]);
    }

    writer.end();
    console.log(`All prompts have been processed and user stories saved for model ${modelPath}.`);
}

async function main() {
    // Read the generated prompts from the CSV file
    const promptsFile = path.join(__dirname, "generated_prompts.csv");
    const prompts = [];

    fs.createReadStream(promptsFile)
        .pipe(csv())
        .on("data", (row) => {
            prompts.push(row);
        })
        .on("end", async () => {
            console.log("CSV file successfully processed");

            // Loop through each model and generate user stories
            for (const modelPath of models) {
                await generateUserStoriesForModel(modelPath, prompts);
            }
        });
}

main();
