import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.venv/Lib/site-packages')))
import csv

# Funktion zum Lesen der Use Cases aus der CSV-Datei
def read_use_cases(csv_file):
    use_cases = []
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            use_cases.append(row)
    return use_cases

# Funktion zum Generieren des Prompts
def generate_prompt(use_case):
    prompt_template = f"""
### Prompt:

You are a skilled software developer responsible for translating a use case into a complete set of user stories. Each user story should be in the format commonly used in agile software development, specifically:

- **As a [type of user]**
- **I want [some goal]**
- **So that [some reason]**

Your task is to generate user stories based on the following use case:

**Use Case:**
{use_case['Use Case']}

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

### Finished Example (based on a hypothetical use case):

**Use Case:** A mobile banking app that allows users to check their account balance, transfer money, and view transaction history.

1. **User Story:**
   - **As a registered user**
   - **I want to log into the mobile banking app**
   - **So that I can securely access my banking features**
   - **Acceptance Criteria:**
     - User must enter a valid username and password
     - System must display an error message for invalid login attempts

2. **User Story:**
   - **As a registered user**
   - **I want to check my account balance**
   - **So that I know how much money I have available**
   - **Acceptance Criteria:**
     - User must be able to select an account to view the balance
     - System must display the current balance accurately

3. **User Story:**
   - **As a registered user**
   - **I want to transfer money to another account**
   - **So that I can pay bills or send money to others**
   - **Acceptance Criteria:**
     - User must enter recipient account details and transfer amount
     - System must confirm the transfer and update the balance accordingly

4. **User Story:**
   - **As a registered user**
   - **I want to view my transaction history**
   - **So that I can track my spending and verify transactions**
   - **Acceptance Criteria:**
     - User must be able to select a date range for viewing transactions
     - System must display a list of transactions within the selected date range

### Task:

Now, using the provided use case, generate a complete set of user stories following the outlined format. Ensure each user story includes clear goals, reasons, and acceptance criteria.
"""
    return prompt_template

# Hauptfunktion zum Generieren der Prompts und Speichern in einer CSV-Datei
def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../../data/generated')
    os.makedirs(data_dir, exist_ok=True)

    csv_file = os.path.join(data_dir, "generated_use_cases.csv")
    output_file = os.path.join(data_dir, "generated_prompts.csv")

    use_cases = read_use_cases(csv_file)
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Industry', 'Title', 'Prompt'])

        for use_case in use_cases:
            prompt = generate_prompt(use_case)
            writer.writerow([use_case['Industry'], use_case['Title'], prompt])

    print(f"Prompts have been saved to {output_file}")

if __name__ == "__main__":
    main()
