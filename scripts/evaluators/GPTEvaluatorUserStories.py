import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.venv/Lib/site-packages')))
import csv
import time
import random
import datetime
import openai
import backoff
from dotenv import load_dotenv
from collections import deque

# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv()

# Setze den OpenAI API-Schlüssel
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("OPENAI_API_KEY not set in environment")

client = openai.OpenAI(api_key=api_key)

# Kriterienliste
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

# Prompt Template zur Evaluierung mit Chain-of-Thought
initial_prompt_template = """
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
"""

follow_up_prompt_template = """
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
"""

# Rate limiting
request_queue = deque()
token_usage = 0
REQUESTS_PER_MINUTE = 3500
REQUESTS_PER_DAY = 10000
TOKENS_PER_MINUTE = 60000
DAILY_REQUEST_LIMIT = 10000
DAILY_TOKEN_LIMIT = 200000

def rate_limit_check():
    global token_usage
    current_time = datetime.datetime.now()

    # Remove requests older than a minute from the queue
    while request_queue and (current_time - request_queue[0]).total_seconds() > 60:
        request_queue.popleft()

    # Check if the number of requests in the last minute exceeds the limit
    if len(request_queue) >= REQUESTS_PER_MINUTE:
        time_to_wait = 60 - (current_time - request_queue[0]).total_seconds()
        print(f"Rate limit reached. Waiting for {time_to_wait} seconds.")
        time.sleep(time_to_wait)
        rate_limit_check()  # Recheck after waiting

    # Check if the number of tokens used in the last minute exceeds the limit
    if token_usage >= TOKENS_PER_MINUTE:
        print("Token limit reached. Waiting for 60 seconds.")
        time.sleep(60)
        token_usage = 0  # Reset token usage after waiting

def check_daily_limits():
    if len(request_queue) >= DAILY_REQUEST_LIMIT:
        print("Daily request limit exceeded. Exiting.")
        exit()
    if token_usage >= DAILY_TOKEN_LIMIT:
        print("Daily token limit exceeded. Exiting.")
        exit()

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def chat_completions_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

def start_evaluation(use_case, user_stories, criterion):
    global token_usage
    print(f"Starting initial evaluation with criterion: {criterion}...")
    start_time = time.time()
    rate_limit_check()
    check_daily_limits()
    response = chat_completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that evaluates software development user stories."},
            {"role": "user", "content": initial_prompt_template.format(use_case=use_case, user_stories=user_stories, criterion=criterion)}
        ],
        max_tokens=1500,
        temperature=0.2
    )
    end_time = time.time()
    print(f"Initial evaluation complete. Time taken: {end_time - start_time} seconds")
    token_usage += response.usage.total_tokens
    request_queue.append(datetime.datetime.now())
    return response.choices[0].message.content

def continue_evaluation(use_case, user_stories, previous_evaluation, criterion):
    global token_usage
    print(f"Continuing evaluation with criterion: {criterion}")
    start_time = time.time()
    rate_limit_check()
    check_daily_limits()
    response = chat_completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that evaluates software development user stories."},
            {"role": "assistant", "content": previous_evaluation},
            {"role": "user", "content": follow_up_prompt_template.format(use_case=use_case, user_stories=user_stories, criterion=criterion)}
        ],
        max_tokens=1500,
        temperature=0.2
    )
    end_time = time.time()
    print(f"Evaluation for criterion '{criterion}' complete. Time taken: {end_time - start_time} seconds")
    token_usage += response.usage.total_tokens
    request_queue.append(datetime.datetime.now())
    return response.choices[0].message.content

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_use_cases_file = os.path.join(current_dir, '../../data/generated', "generated_use_cases.csv")
    input_user_stories_file = os.path.join(current_dir, '../../data/generated', "generated_user_stories.csv")

    data_dir = os.path.join(current_dir, '../../data/evaluated')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, "evaluated_by_GPT-3.5-Turbo_user_stories.csv")

    use_cases_dict = {}
    with open(input_use_cases_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            industry, title, description, actor, preconditions, trigger, use_case = row
            use_cases_dict[title] = use_case

    with open(input_user_stories_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)

        if len(headers) < 4:
            raise ValueError("The CSV file does not have the expected number of columns.")

        rows = [row for row in reader if len(row[3]) > 10]  # Skip rows with user stories shorter than 10 characters

    evaluations = []

    for idx, row in enumerate(rows):
        if len(row) < 4:
            print(f"Warning: Row does not have enough values: {row}")
            continue

        industry, title, model, user_stories = row
        use_case = use_cases_dict.get(title, "No use case found for this title")
        print(f"Evaluating user stories for {title} in {industry} (Model: {model})... ({idx + 1}/{len(rows)})")

        try:
            evaluation = start_evaluation(use_case, user_stories, criteria[0])
        except ValueError as e:
            print(f"Error: {e}")
            break

        full_evaluation = evaluation  # Start collecting the full evaluation
        print(f"Intermediate result after initial evaluation for {title}:\n", evaluation)

        for criterion in criteria[1:]:
            try:
                evaluation = continue_evaluation(use_case, user_stories, full_evaluation, criterion)
            except ValueError as e:
                print(f"Error: {e}")
                break

            full_evaluation += "\n" + evaluation  # Append each criterion evaluation to the full evaluation
            print(f"Intermediate result after evaluating {criterion.split(':')[0]} for {title}:\n", evaluation)

        print(f"Finished evaluating {title} in {industry} (Model: {model}).")
        print("Final Evaluation result:\n", full_evaluation)
        evaluations.append([industry, title, model, user_stories, full_evaluation])  # Save the full evaluation

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers + ["Evaluation"])
        writer.writerows(evaluations)

    print(f"User stories have been evaluated and saved to {output_file}")

if __name__ == "__main__":
    main()
