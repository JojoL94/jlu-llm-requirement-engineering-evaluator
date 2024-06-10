# jlu-llm-requirement-engineering-evaluator

Dieses Projekt generiert Use Cases und formatiert sie zu Prompts für die Erstellung von User Stories. Es verwendet OpenAI für die Erstellung von Use Cases und LM Studio für die Generierung von User Stories.

## Installation

### Python-Umgebung

1. Klone das Repository:
    ```sh
    git clone https://github.com/DeinBenutzername/jlu-llm-requirement-engineering-evaluator.git
    cd jlu-llm-requirement-engineering-evaluator
    ```

2. Erstelle eine virtuelle Umgebung und aktiviere sie:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # Für Windows: .venv\Scripts\activate
    ```

3. Installiere die Python-Abhängigkeiten:
    ```sh
    pip install -r requirements.txt
    ```

4. Erstelle eine `.env` Datei im Projektverzeichnis mit folgendem Inhalt:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Node.js-Umgebung

1. Installiere die Node.js-Abhängigkeiten:
    ```sh
    npm install
    ```

## Nutzung

### Use Case Generator

Führe das Skript `UseCaseGenerator.py` aus, um Use Cases zu generieren und in einer CSV-Datei zu speichern:
```sh
python UseCaseGenerator.py
