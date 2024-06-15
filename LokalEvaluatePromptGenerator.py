import csv
import os

# Kriterien nach Lucassen et al.
criteria = [
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
]

# Pfade zu den CSV-Dateien
input_use_cases_file = 'generated_use_cases.csv'
input_user_stories_file = 'generated_user_stories.csv'
output_prompts_file = 'generated_evaluation_prompts.csv'

# Lesen der Use Cases
use_cases_dict = {}
with open(input_use_cases_file, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    headers = next(reader)
    for row in reader:
        industry, title, description, actor, preconditions, trigger, use_case = row
        use_cases_dict[title] = use_case

# Generieren der Prompts
prompts = []
with open(input_user_stories_file, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    headers = next(reader)
    for row in reader:
        if len(row[3]) > 10:
            industry, title, model, user_stories = row
            use_case = use_cases_dict.get(title, "No use case found for this title")
            for criterion in criteria:
                prompt = f"""
### Prompt:

You are a skilled software developer responsible for evaluating the quality of user stories. Evaluate the following user stories based on the given criterion.

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

Evaluate each user story individually within the context of the entire use case and the set of user stories. For the criterion, provide a Yes or No response and if necessary a short explanation for the response. Use the following format and stay in this format:
------Start of format------
Criterion: [Name of Criterion]
User Story [Number of User Story]: [Yes/No] - [Explanation if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation if necessary]
User Story [Number of User Story]: [Yes/No] - [Explanation if necessary]
(...rest of user stories with their evaluation in the same format as before)

Overall Result: [Yes/No]
Explanation: [Short Explanation if necessary. Max 3 Sentence]
End of Evaluation
-------End of format-------

Scores:
Yes - Criterion met
No - Criterion not met or partially met

Please evaluate the user stories based on the given criterion. Provide the evaluation for each user story in the same format as described and dont make your own format. Very Important: If you are finished with the format, write "End of Evaluation", as described.
"""
                prompts.append([industry, title, model, criterion, prompt])

# Schreiben der Prompts in eine CSV-Datei
with open(output_prompts_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Industry", "Title", "Model", "Criterion", "Prompt"])
    writer.writerows(prompts)

print(f"Prompts have been generated and saved to {output_prompts_file}")
