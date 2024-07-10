import pandas as pd

# Pfad zur hochgeladenen Datei
file_path = 'data/generated/generated_user_stories.csv'

# Datei laden
df = pd.read_csv(file_path)

# Anzeige der ersten Zeilen der Datei
print("Erste Zeilen der Datei:")
print(df.head())

# Letzte Zeile der Datei extrahieren
last_row = df.iloc[-1]
print("\nLetzte Zeile der Datei:")
print(last_row)

# Werte der letzten Zeile extrahieren
last_industry = last_row['Industry']
last_title = last_row['Title']
last_model = last_row['Model']

print(f"\nIndustry der letzten Zeile: {last_industry}")
print(f"Title der letzten Zeile: {last_title}")
print(f"Model der letzten Zeile: {last_model}")
