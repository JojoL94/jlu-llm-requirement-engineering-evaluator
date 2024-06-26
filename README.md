# jlu-llm-requirement-engineering-evaluator

## Projektbeschreibung

Dieses Projekt generiert Use Cases und User Stories für verschiedene Branchen unter Verwendung von Sprachmodellen (LLMs) und LM Studio. Zudem werden die generierten User Stories auf 13 Qualitätskriterien von Lucassen et al., 2015 evaluiert und ein Leaderboard erstellt, das die Leistung der verschiedenen Modelle vergleicht.

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

### Kompletten Prozess ausführen

Der `run_all.py`-Skript steuert den gesamten Prozess vom Generieren der Use Cases bis zur Erstellung des Leaderboards.

1. **Gesamten Prozess ausführen**:

   ```sh
   python scripts/run_all.py
   ```

   Dieses Skript führt die folgenden Schritte aus:
   - Generiert Use Cases (`UseCaseGenerator.py`)
   - Generiert Prompts (`PromptGenerator.py`)
   - Startet den LM Studio-Server
   - Generiert User Stories (`UserStoryGenerator.js`)
   - Evaluiert die User Stories (`GPTEvaluatorUserStories.py`)
   - Erstellt ein Leaderboard (`LeaderboardGenerator.py`)

### Einzelschritte ausführen

Sie können auch jeden Schritt des Prozesses einzeln ausführen, wie unten beschrieben.

### Use Cases generieren

Der `UseCaseGenerator.py` erstellt eine Reihe von Use Cases für verschiedene Branchen und speichert sie in einer CSV-Datei.

1. **Use Cases generieren**:

   ```sh
   python scripts/generators/UseCaseGenerator.py
   ```

   Diese Datei liest die Brancheninformationen und generiert die entsprechenden Use Cases, die in der Datei `data/generated/generated_use_cases.csv` gespeichert werden.

#### Änderung der Branche im `UseCaseGenerator.py`

Um die Branche zu ändern oder neue Branchen hinzuzufügen, kannst du die Liste `industries` im `UseCaseGenerator.py` bearbeiten. Hier ist ein Beispiel, wie du eine neue Branche hinzufügen kannst:

```python
industries = [
   {"industry": "Automotive", "title": "Vehicle Maintenance", "description": "track vehicle maintenance schedules", "actor": "Mechanic", "preconditions": "Mechanic is logged into the system", "trigger": "Mechanic selects a vehicle"},
   {"industry": "Banking", "title": "Loan Processing", "description": "process a loan application", "actor": "Bank Officer", "preconditions": "Bank Officer is logged into the loan processing system", "trigger": "Customer submits a loan application"},
   # Neue Branche hinzufügen
   {"industry": "E-Commerce", "title": "Order Processing", "description": "process an order", "actor": "Sales Agent", "preconditions": "Sales Agent is logged into the order system", "trigger": "Customer places an order"}
]
```

### Prompts generieren

Der `PromptGenerator.py` erstellt Prompts basierend auf den generierten Use Cases und speichert sie in einer CSV-Datei.

1. **Prompts generieren**:

   ```sh
   python scripts/generators/PromptGenerator.py
   ```

   Diese Datei liest die `data/generated/generated_use_cases.csv` und erstellt die entsprechenden Prompts, die in der Datei `data/generated/generated_prompts.csv` gespeichert werden.

#### Änderung des Prompts im `PromptGenerator.py`

Um den Prompt anzupassen, kannst du den `prompt_template` im `PromptGenerator.py` bearbeiten. Hier ist ein Beispiel:

```python
prompt_template = """
### Prompt:

You are a skilled software developer responsible for translating a use case into a complete set of user stories. Each user story should be in the format commonly used in agile software development, specifically:

- **As a [type of user]**
- **I want [some goal]**
- **So that [some reason]**

Your task is to generate user stories based on the following use case:

**Use Case:**
[Insert detailed use case description here]

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
"""

# Anpassungen können hier vorgenommen werden
```

### User Stories generieren

Bevor die User Stories generiert werden können, muss der LM Studio-Server gestartet werden.

1. **LM Studio-Server starten**:

   ```sh
   lms server start
   ```

   Dies startet den lokalen LM Studio-Server, der für die Verarbeitung der User Stories benötigt wird.

2. **User Stories generieren**:

   ```sh
   node scripts/generators/UserStoryGenerator.js
   ```

   Diese Datei liest die `data/generated/generated_prompts.csv`, generiert die User Stories mithilfe von verschiedenen Modellen und speichert sie in der Datei `data/generated/generated_user_stories.csv`.

#### Änderung der LLMs im `UserStoryGenerator.js`

Um die Modelle zu ändern, die für die Generierung der User Stories verwendet werden, kannst du die `models`-Liste im `UserStoryGenerator.js` bearbeiten. Hier ist ein Beispiel:

```javascript
const models = [
   "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
   "Qwen/Qwen2-7B-Instruct-GGUF/qwen2-7b-instruct-q5_0.gguf",
   // Neues Modell hinzufügen
   "lmstudio-community/New-Model-Name"
];
```

Die generierten User Stories werden in der Datei `data/generated/generated_user_stories.csv` gespeichert, mit einer klaren Trennung zwischen den Modellen und den Use Cases.

### User Stories evaluieren

1. **Evaluation der User Stories durchführen**:

   ```sh
   python scripts/evaluators/GPTEvaluatorUserStories.py
   ```

   Diese Datei liest die `data/generated/generated_user_stories.csv`, evaluiert die User Stories auf 13 Qualitätskriterien von Lucassen et al., 2015 mithilfe des ausgewählten Modells und speichert die Ergebnisse in der Datei `data/evaluated/evaluated_by_GPT-3.5-Turbo_user_stories.csv`.

### Ergebnisse analysieren und ein Leaderboard erstellen

Das Skript `LeaderboardGenerator.py` analysiert die Evaluationsergebnisse und erstellt ein Leaderboard.

1. **Ergebnisse analysieren und ein Leaderboard erstellen**:

   ```sh
   python scripts/analytics/LeaderboardGenerator.py
   ```

   Diese Datei liest die `data/evaluated/evaluated_by_GPT-3.5-Turbo_user_stories.csv`, analysiert die Ergebnisse und erstellt ein Leaderboard, das in der Datei `data/leaderboard/leaderboard.csv` gespeichert wird.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die [LICENSE.txt](LICENSE.txt) Datei für weitere Details.

## Autor

- [JojoL94](https://github.com/JojoL94)