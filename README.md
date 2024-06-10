### README.md

```markdown
# jlu-llm-requirement-engineering-evaluator

## Projektbeschreibung

Dieses Projekt generiert Use Cases und User Stories für verschiedene Branchen unter Verwendung von Sprachmodellen (LLMs) und LM Studio.

## Installation

### Voraussetzungen

- [Python 3.x](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/en/download/) (empfohlen Version 16 oder höher)
- [LM Studio](https://www.lmstudio.com/)

### Schritte

1. **Repository klonen**:

   ```sh
   git clone https://github.com/dein-benutzername/jlu-llm-requirement-engineering-evaluator.git
   cd jlu-llm-requirement-engineering-evaluator
   ```

2. **Virtuelle Umgebung für Python erstellen und aktivieren**:

   ```sh
   python -m venv .venv
   source .venv/bin/activate  # Für Windows: .venv\Scripts\activate
   ```

3. **Python-Abhängigkeiten installieren**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Node.js-Abhängigkeiten installieren**:

   ```sh
   npm install
   ```

5. **LM Studio CLI installieren**:

   ```sh
   npx lmstudio install-cli
   ```

## Verwendung

### Use Cases generieren

Der `UseCaseGenerator.py` erstellt eine Reihe von Use Cases für verschiedene Branchen und speichert sie in einer CSV-Datei.

1. **Use Cases generieren**:

   ```sh
   python UseCaseGenerator.py
   ```

   Diese Datei liest die Brancheninformationen und generiert die entsprechenden Use Cases, die in der Datei `generated_use_cases.csv` gespeichert werden.

### Prompts generieren

Der `PromptGenerator.py` erstellt Prompts basierend auf den generierten Use Cases und speichert sie in einer CSV-Datei.

1. **Prompts generieren**:

   ```sh
   python PromptGenerator.py
   ```

   Diese Datei liest die `generated_use_cases.csv` und erstellt die entsprechenden Prompts, die in der Datei `generated_prompts.csv` gespeichert werden.

### User Stories generieren

Die `index.js`-Datei verwendet LM Studio, um basierend auf den generierten Prompts User Stories zu erstellen und speichert sie in einer CSV-Datei.

1. **User Stories generieren**:

   ```sh
   node index.js
   ```

   Diese Datei liest die `generated_prompts.csv`, generiert die User Stories mithilfe von verschiedenen Modellen und speichert sie in der Datei `generated_user_stories.csv`.

Die generierten User Stories werden in der Datei `generated_user_stories.csv` gespeichert, mit einer klaren Trennung zwischen den Modellen und den Use Cases.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE.txt](LICENSE.txt) Datei für weitere Details.

## Autoren

- [Dein Name](https://github.com/dein-benutzername)

## Danksagungen

- Danke an [LM Studio](https://www.lmstudio.com/) für die Bereitstellung der LLMs.
- Danke an [OpenAI](https://www.openai.com/) für die API.
```
