const { LMStudioClient } = require("@lmstudio/sdk");
const fs = require("fs");
const path = require("path");

async function main() {
    // Create a client to connect to LM Studio, then load a model
    const client = new LMStudioClient();
    const model = await client.llm.load("lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF");

    // Read the generated prompts from file
    const promptsFile = path.join(__dirname, "generated_prompts.txt");
    const prompts = fs.readFileSync(promptsFile, "utf-8").split("\n" + "=".repeat(80) + "\n");

    // File to save the generated user stories
    const outputFile = path.join(__dirname, "generated_user_stories.txt");
    const output = fs.createWriteStream(outputFile, { flags: 'a' });

    // Process each prompt and get user stories
    for (const prompt of prompts) {
        console.log(`Processing prompt:\n${prompt}`);

        const prediction = model.respond([
            { role: "system", content: "You are a skilled software developer responsible for translating a use case into a complete set of user stories." },
            { role: "user", content: prompt },
        ]);

        let userStories = "";
        for await (const text of prediction) {
            process.stdout.write(text);
            userStories += text;
        }

        output.write(`Prompt:\n${prompt}\nUser Stories:\n${userStories}\n${"=".repeat(80)}\n`);
    }

    output.end();
    console.log("All prompts have been processed and user stories saved.");
}

main();
