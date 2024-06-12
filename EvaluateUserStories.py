import csv
import os
from openai import OpenAI
from dotenv import load_dotenv

# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv()

# Setze den OpenAI API-Schlüssel
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY not set in environment")

client = OpenAI(api_key=api_key)

# Prompt Template zur Evaluierung
evaluation_prompt_template = """
### Prompt:

You are a skilled software developer responsible for evaluating the quality of user stories. Evaluate the following user stories based on the 13 criteria described by Lucassen et al.:

User Stories: {user_stories}

The criteria are:
1. Well-formed: The user story must include at least one role and one means.
2. Atomic: The user story should express exactly one requirement.
3. Minimal: The user story should contain only the role, means, and ends, with no additional information.
4. Conceptually sound: The means should express concrete functionality and the ends should justify the need for this functionality.
5. Problem-oriented: The user story should specify only the problem and not the solution.
6. Unambiguous: The user story should not contain terms or abstractions that lead to multiple interpretations.
7. Conflict-free: The user story should not contradict other user stories.
8. Full sentence: The user story should be formulated as a complete sentence.
9. Estimatable: The user story should not be so vaguely formulated that it is difficult to plan and prioritize.
10. Unique: Each user story should be unique, avoiding duplicates.
11. Uniform: All user stories in a specification should use the same format.
12. Independent: The user story should be self-contained and not have inherent dependencies on other user stories.
13. Complete: The implementation of a set of user stories should lead to a working application without missing essential steps.

Evaluate each user story individually within the context of the entire use case. Provide a score from 0 to 3 for each criterion and a brief explanation for each score. Then provide an overall evaluation summary for the entire set of user stories. Use the following format:

Overall Evaluation for User Stories:
1. Well-formed: [Total Score] - [Average Score(Total Score divided by total count of user stories] - [Brief explanation]
2. Atomic: [Total Score] - [Average Score] - [Brief explanation]
3. Minimal: [Total Score] - [Average Score] - [Brief explanation]
...
13. Complete: [Total Score] - [Average Score] - [Brief explanation]

Evaluation Summary:
[Overall explanation summarizing the strengths and weaknesses of the user stories]
"""

def evaluate_user_stories(user_stories):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that evaluates software development user stories."},
            {"role": "user", "content": evaluation_prompt_template.format(user_stories=user_stories)}
        ],
        max_tokens=4000,
        temperature=0.2
    )

    return response.choices[0].message.content

def main():
    input_file = 'generated_user_stories.csv'
    output_file = 'evaluated_user_stories.csv'

    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)

        if len(headers) < 4:
            raise ValueError("Die CSV-Datei hat nicht die erwartete Anzahl von Spalten.")

        rows = [row for row in reader if row[0] != "Industry"]

    evaluations = []
    for idx, row in enumerate(rows):
        if len(row) < 4 or len(row[3]) < 10:  # Überprüfen Sie, ob die User Stories-Zelle weniger als 10 Zeichen enthält
            print(f"Warnung: Zeile hat nicht genügend Werte oder die User Stories sind zu kurz: {row}")
            continue

        industry, title, model, user_stories = row
        print(f"Evaluating user stories for {title} in {industry} (Model: {model})... ({idx + 1}/{len(rows)})")
        evaluation = evaluate_user_stories(user_stories)
        print(f"Finished evaluating {title} in {industry} (Model: {model}).")
        print("Evaluation result:\n", evaluation)
        evaluations.append([industry, title, model, user_stories, evaluation])

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers + ["Evaluation"])
        writer.writerows(evaluations)

    print(f"User stories have been evaluated and saved to {output_file}")

if __name__ == "__main__":
    main()
