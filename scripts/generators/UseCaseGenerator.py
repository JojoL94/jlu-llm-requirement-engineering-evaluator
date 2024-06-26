import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.venv/Lib/site-packages')))

import csv
import os
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

def generate_use_case(industry, title, description, actor, preconditions, trigger):
    global token_usage
    prompt = f"""
    Generate a high-quality use case for the {industry} industry.

    Title: {title}
    Actor: {actor}
    Description: {description}
    Preconditions: {preconditions}
    Trigger: {trigger}

    Main Flow:
    1. [Actor] logs into the system.
    2. [Actor] navigates to the {title} page.
    3. [Actor] performs {description}.
    4. The system validates the input.
    5. The system displays the {title} confirmation.

    Alternative Flows:
    1a. If [Actor] provides invalid input, the system displays an error message.

    Postconditions: The {title} is successfully {description}.
    Exceptions: If the system is unavailable, [Actor] is notified.
    """

    rate_limit_check()
    check_daily_limits()

    response = chat_completions_with_backoff(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates software development use cases."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2
    )

    token_usage += response.usage.total_tokens
    request_queue.append(datetime.datetime.now())

    # Extrahiere die Antwortnachricht
    message = response.choices[0].message.content
    print(f"Generated use case for {title}:\n{message}")  # Echtzeit-Ausgabe in die Konsole
    return message

def main():
    industries = [
        {"industry": "Automotive", "title": "Parts Supplier Management", "description": "manage parts supply for automotive manufacturers", "actor": "Supply Chain Manager", "preconditions": "Supply Chain Manager is logged into the supplier management system", "trigger": "New parts order is placed by the manufacturer"},
        {"industry": "Food", "title": "Production Line Monitoring", "description": "monitor and manage production lines in a food manufacturing facility", "actor": "Production Supervisor", "preconditions": "Production Supervisor is logged into the production monitoring system", "trigger": "Production line status update or alert"},
        {"industry": "Banking", "title": "Loan Processing", "description": "process a loan application", "actor": "Bank Officer", "preconditions": "Bank Officer is logged into the loan processing system", "trigger": "Customer submits a loan application"},
        {"industry": "Insurance", "title": "Claim Filing", "description": "file an insurance claim", "actor": "Insurance Agent", "preconditions": "Insurance Agent is on the claims page", "trigger": "Customer reports an incident"},
        {"industry": "Healthcare", "title": "Patient Appointment", "description": "schedule a patient appointment", "actor": "Receptionist", "preconditions": "Receptionist is logged into the appointment system", "trigger": "Patient requests an appointment"},
        {"industry": "Public Sector", "title": "Voter Registration", "description": "register a new voter", "actor": "Government Official", "preconditions": "Official is on the voter registration page", "trigger": "Citizen requests to register as a voter"},
        {"industry": "Travel & Logistics", "title": "Shipment Tracking", "description": "track a shipment", "actor": "Logistics Coordinator", "preconditions": "Coordinator is logged into the tracking system", "trigger": "Shipment status is updated"},
        {"industry": "Telecommunications", "title": "Service Ticket Resolution", "description": "resolve a customer service ticket", "actor": "Customer Service Agent", "preconditions": "Agent is on the support ticket page", "trigger": "Customer submits a service ticket"},
        {"industry": "Corporate IT", "title": "Software Update Deployment", "description": "deploy a new software update", "actor": "IT Administrator", "preconditions": "Administrator is on the update deployment page", "trigger": "Update is ready for deployment"},
        {"industry": "Consumer Products | New Data Solutions", "title": "Purchase Data Analysis", "description": "analyze consumer purchase data", "actor": "Data Analyst", "preconditions": "Analyst is logged into the data analysis tool", "trigger": "New purchase data is available"},
        {"industry": "Cyber Security", "title": "Security Audit", "description": "conduct a security audit", "actor": "Security Auditor", "preconditions": "Auditor is on the audit page", "trigger": "Audit is scheduled"},
        {"industry": "Test & Quality Management", "title": "Quality Assurance Test", "description": "execute a quality assurance test", "actor": "QA Engineer", "preconditions": "Engineer is logged into the QA system", "trigger": "Test is scheduled"},
        {"industry": "Life Science & Chemicals", "title": "Lab Experiment Recording", "description": "record lab experiment results", "actor": "Lab Technician", "preconditions": "Technician is on the lab results page", "trigger": "Experiment is completed"}
    ]

    # Erstelle das Verzeichnis für die generierten Dateien, falls es noch nicht existiert
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '../../data/generated')
    os.makedirs(output_dir, exist_ok=True)

    # CSV-Datei erstellen und die Daten speichern
    csv_file = os.path.join(output_dir, "generated_use_cases.csv")
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Industry", "Title", "Description", "Actor", "Preconditions", "Trigger", "Use Case"])

        for industry in industries:
            use_case = generate_use_case(
                industry=industry["industry"],
                title=industry["title"],
                description=industry["description"],
                actor=industry["actor"],
                preconditions=industry["preconditions"],
                trigger=industry["trigger"]
            )
            writer.writerow([
                industry["industry"],
                industry["title"],
                industry["description"],
                industry["actor"],
                industry["preconditions"],
                industry["trigger"],
                use_case
            ])

    print(f"Use cases have been saved to {csv_file}")

if __name__ == "__main__":
    main()
