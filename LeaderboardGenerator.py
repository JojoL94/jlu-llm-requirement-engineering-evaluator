import pandas as pd
import os
import re

# Funktion zum Bereinigen der Kriterien-Namen
def clean_criterion_name(name):
    match = re.match(r"([A-Za-z\s-]+):?.*", name)
    if match:
        return match.group(1).strip()
    return name.strip()

# Funktion zum Parsen der Evaluation
def parse_evaluation(evaluation):
    criteria_results = {}
    lines = evaluation.split('\n')
    current_criterion = None

    for line in lines:
        if line.startswith("Criterion:"):
            current_criterion_raw = line.split("Criterion:")[1].strip()
            current_criterion = clean_criterion_name(current_criterion_raw)
            criteria_results[current_criterion] = {'Yes': 0, 'No': 0}
        elif line.startswith("User Story"):
            result = line.split(":")[1].strip().split(' ')[0]  # Extrahiere "Yes" oder "No"
            if result in ['Yes', 'No']:
                criteria_results[current_criterion][result] += 1

    return criteria_results

# Setze den Pfad zu den Evaluierungsergebnissen
file_path = 'evaluated_by_GPT-3.5-Turbo_user_stories.csv'

# Laden der Evaluierungsergebnisse von GPT-3.5
gpt_3_5_evaluations = pd.read_csv(file_path)

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
        all_results.append({
            'Industry': industry,
            'Title': title,
            'Model': model,
            'Criterion': criterion,
            'Yes': results['Yes'],
            'No': results['No']
        })

results_df = pd.DataFrame(all_results)
print(results_df.head())

# Speichern der Ergebnisse in einer neuen CSV-Datei
results_df.to_csv('gpt_3_5_parsed_evaluations.csv', index=False)

# Aggregieren der Ergebnisse nach Modell und Kriterium
aggregated_results = results_df.groupby(['Model', 'Criterion']).agg({
    'Yes': 'sum',
    'No': 'sum'
}).reset_index()

# Berechnung des Qualitätsindexes
aggregated_results['Quality Index'] = aggregated_results['Yes'] / (aggregated_results['Yes'] + aggregated_results['No'])

# Speichern der aggregierten Ergebnisse in einer neuen CSV-Datei
aggregated_results.to_csv('aggregated_results.csv', index=False)

# Erstellen eines Leaderboards
leaderboard = aggregated_results.groupby('Model')['Quality Index'].mean().reset_index()
leaderboard = leaderboard.sort_values(by='Quality Index', ascending=False)

# Speichern des Leaderboards in einer neuen CSV-Datei
leaderboard.to_csv('leaderboard.csv', index=False)

print("Leaderboard erstellt und Ergebnisse gespeichert.")
