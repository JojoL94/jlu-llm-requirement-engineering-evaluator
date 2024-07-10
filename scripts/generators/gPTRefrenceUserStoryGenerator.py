import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.venv/Lib/site-packages')))

import csv
import os
import time
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

    # Entfernen von Anfragen, die älter als eine Minute sind, aus der Warteschlange
    while request_queue and (current_time - request_queue[0]).total_seconds() > 60:
        request_queue.popleft()

    # Überprüfen, ob die Anzahl der Anfragen in der letzten Minute das Limit überschreitet
    if len(request_queue) >= REQUESTS_PER_MINUTE:
        time_to_wait = 60 - (current_time - request_queue[0]).total_seconds()
        print(f"Rate limit reached. Waiting for {time_to_wait} seconds.")
        time.sleep(time_to_wait)
        rate_limit_check()  # Nach dem Warten erneut prüfen

    # Überprüfen, ob die Anzahl der verwendeten Tokens in der letzten Minute das Limit überschreitet
    if token_usage >= TOKENS_PER_MINUTE:
        print("Token limit reached. Waiting for 60 seconds.")
        time.sleep(60)
        token_usage = 0  # Token-Nutzung nach dem Warten zurücksetzen

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

def generate_user_stories(use_case):
    global token_usage
    prompt = f"""
### Prompt:

You are a skilled software developer responsible for translating a use case into a complete set of user stories. Each user story should be in the format commonly used in agile software development, specifically:

- **As a [type of user]**
- **I want [some goal]**
- **So that [some reason]**

Your task is to generate user stories based on the following use case:

**Use Case:**
{use_case}

### Requirements for the User Stories:

1. **Clarity and Specificity:** Each user story should be clear and specific, outlining the type of user, their goal, and the reason behind the goal.
2. **Completeness:** Ensure the set of user stories covers all aspects of the given use case, addressing various functionalities, user interactions, and system responses.
3. **Prioritization:** Organize the user stories in a logical sequence, starting with the most critical features and progressing to less critical ones.
4. **Acceptance Criteria:** Include acceptance criteria for each user story, specifying the conditions that must be met for the story to be considered complete.

### Example Format:

1. **User Story:**
   - **As a [type of user]**
   - **I want [some goal]**
   - **So that [some reason]**
   - **Acceptance Criteria:**
     - [Criterion 1]
     - [Criterion 2]

2. **User Story:**
   - **As a [type of user]**
   - **I want [some goal]**
   - **So that [some reason]**
   - **Acceptance Criteria:**
     - [Criterion 1]
     - [Criterion 2]

(... Rest of User Stories)
### Task:

Now, using the provided use case, generate a complete set of user stories following the outlined format. Ensure each user story includes clear goals, reasons, and acceptance criteria (if necessary). I only need the set of user stories. No explanation or other information about the set of user stories is required.
"""

    rate_limit_check()
    check_daily_limits()

    response = chat_completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates software development user stories."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    token_usage += response.usage.total_tokens
    request_queue.append(datetime.datetime.now())

    message = response.choices[0].message.content
    print(f"Generated user stories for use case:\n{message}")
    return message

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_use_cases_file = os.path.join(current_dir, '../../data/generated', "generated_use_cases.csv")

    output_dir = os.path.join(current_dir, '../../data/generated')
    os.makedirs(output_dir, exist_ok=True)

    csv_file = os.path.join(output_dir, "generated_reference_user_stories.csv")
    with open(input_use_cases_file, mode='r', encoding='utf-8') as infile, \
            open(csv_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        headers = next(reader)
        writer.writerow(["Industry", "Title", "Model", "User Stories"])

        for row in reader:
            industry, title, description, actor, preconditions, trigger, use_case = row
            reference_user_stories = generate_user_stories(use_case)
            writer.writerow([industry, title, "Reference Model", reference_user_stories])

    print(f"Reference user stories have been saved to {csv_file}")

if __name__ == "__main__":
    main()
