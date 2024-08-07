import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.venv/Lib/site-packages')))
import pandas as pd
import re

# Liste der bekannten Kriterien und ihre Erklärungen
criteria = [
    "Atomic: A user story expresses a requirement for exactly one feature.",
    "Minimal: A user story contains nothing more than role, means and ends",
    "Well-formed: A user story includes at least a role and a means.",
    "Conflict-free: A user story should not be inconsistent with any other user story.",
    "Conceptually sound: The means expresses a feature and the ends expresses a rationale, not something else.",
    "Problem-oriented: A user story only specifies the problem, not the solution to it.",
    "Unambiguous: A user story avoids terms or abstractions that may lead to multiple interpretations.",
    "Complete: Implementing a set of user stories creates a feature-complete application, no steps are missing.",
    "Explicit dependencies: Link all unavoidable, non-obvious dependencies on user stories.",
    "Full sentence: A user story is a well-formed full sentence.",
    "Independent: The user story is self-contained, avoiding inherent dependencies on other user stories.",
    "Scalable: User stories do not denote too coarse-grained requirements that are difficult to plan and prioritize.",
    "Uniform: All user stories follow roughly the same template.",
    "Unique: Every user story is unique, duplicates are avoided."
]

# Funktion zum Bereinigen der Kriterien-Namen und zur Zuordnung zu den bekannten Kriterien
def clean_criterion_name(name):
    match = re.match(r"([A-Za-z\s-]+):?.*", name)
    if match:
        cleaned_name = match.group(1).strip()
    else:
        cleaned_name = name.strip()

    for criterion in criteria:
        if cleaned_name in criterion or criterion.startswith(cleaned_name):
            return criterion.split(":")[0]

    return cleaned_name

# Funktion zum Parsen der Evaluation
def parse_evaluation(evaluation):
    criteria_results = {}
    lines = evaluation.split('\n')
    current_criterion = None
    inside_format_block = False

    for line in lines:
        if re.match(r"Criterion: \[Name of Criterion\]", line):
            inside_format_block = True

        if any(end_condition in line for end_condition in ["-------End of format-------", "End of Evaluation", "Explanation: [Short Explanation of the overall result if necessary. Max 3 sentences]"]):
            inside_format_block = False
            continue

        if inside_format_block:
            continue

        if line.startswith("Criterion:"):
            current_criterion_raw = line.split("Criterion:")[1].strip()
            current_criterion = clean_criterion_name(current_criterion_raw)
            criteria_results[current_criterion] = {'Yes': 0, 'No': 0}
        elif line.startswith("User Story"):
            result = line.split(":")[1].strip().split(' ')[0]  # Extrahiere "Yes" oder "No"
            if result in ['Yes', 'No']:
                criteria_results[current_criterion][result] += 1
                continue  # Überspringe den Rest der Zeile nach dem ersten "Yes" oder "No"

    return criteria_results

# Setze den Pfad zu den Evaluierungsergebnissen
input_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/evaluated/evaluated_by_GPT-3.5-Turbo_user_stories.csv'))

# Laden der Evaluierungsergebnisse von GPT-3.5
gpt_3_5_evaluations = pd.read_csv(input_file_path)

# Anzeigen der ersten Zeilen, um einen Überblick über die Struktur zu erhalten
print(gpt_3_5_evaluations.head())

# Analysieren aller Evaluierungen und Erstellen einer Übersicht
all_results = []

for index, row in gpt_3_5_evaluations.iterrows():
    industry = row['Industry']
    title = row['Title']
    model = row['Model']
    user_stories = row['User Stories']
    evaluation = row['Evaluation']

    parsed_evaluation = parse_evaluation(evaluation)

    for criterion, results in parsed_evaluation.items():
        total_yes = results['Yes']
        total_no = results['No']
        all_results.append({
            'Industry': industry,
            'Title': title,
            'Model': model,
            'Criterion': criterion,
            'Yes': total_yes,
            'No': total_no,
            'Total': total_yes + total_no  # Neue Spalte für die Gesamtanzahl
        })

results_df = pd.DataFrame(all_results)
print(results_df.head())

# Speichern der Ergebnisse in einer neuen CSV-Datei
parsed_evaluations_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/parsed/gpt_3_5_parsed_evaluations.csv'))
results_df.to_csv(parsed_evaluations_output_path, index=False)

# Aggregieren der Ergebnisse nach Modell und Kriterium
aggregated_results = results_df.groupby(['Model', 'Criterion']).agg({
    'Yes': 'sum',
    'No': 'sum',
    'Total': 'sum'  # Aggregieren der Gesamtanzahl
}).reset_index()

# Berechnung des Qualitätsindexes
aggregated_results['Quality Index'] = aggregated_results['Yes'] / aggregated_results['Total']

# Speichern der aggregierten Ergebnisse in einer neuen CSV-Datei
aggregated_results_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/aggregated/aggregated_results.csv'))
aggregated_results.to_csv(aggregated_results_output_path, index=False)

# Erstellen eines Leaderboards
leaderboard = aggregated_results.groupby('Model')['Quality Index'].mean().reset_index()
leaderboard = leaderboard.sort_values(by='Quality Index', ascending=False)

# Speichern des Leaderboards in einer neuen CSV-Datei
leaderboard_output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/leaderboard/leaderboard.csv'))
leaderboard.to_csv(leaderboard_output_path, index=False)

print("Leaderboard erstellt und Ergebnisse gespeichert.")
