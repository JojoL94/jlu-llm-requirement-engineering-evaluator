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

def generate_use_case(industry, title, description, actor, preconditions, trigger):
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates software development use cases."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extrahiere die Antwortnachricht
    message = response.choices[0].message.content
    return message

# Liste der Branchen und dazugehörige Beschreibungen
industries = [
    {"industry": "Automotive", "title": "Vehicle Maintenance", "description": "track vehicle maintenance schedules", "actor": "Mechanic", "preconditions": "Mechanic is logged into the system", "trigger": "Mechanic selects a vehicle"},
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
    {"industry": "Life Science & Chemicals", "title": "Lab Experiment Recording", "description": "record lab experiment results", "actor": "Lab Technician", "preconditions": "Technician is on the lab results page", "trigger": "Experiment is completed"},
    {"industry": "Food", "title": "Food Inventory Management", "description": "manage a food inventory", "actor": "Inventory Manager", "preconditions": "Manager is logged into the inventory system", "trigger": "Inventory levels are updated"}
]

# CSV-Datei erstellen und die Daten speichern
csv_file = 'generated_use_cases.csv'
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
