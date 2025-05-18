from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import re

# LLM initialisieren
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Funktion zum Laden von Prompts
def load_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Parse-Funktionen aus NL2Plan
def combine_blocks(text):
    """
    Extrahiert und kombiniert Codeblöcke, die mit ``` gekennzeichnet sind
    """
    code_blocks = re.findall(r'```(?:\w*\n)?(.*?)```', text, re.DOTALL)
    return "\n".join(code_blocks)

def parse_types(llm_output):
    """
    Extrahiert Typen aus dem LLM-Output im Format 'typname: beschreibung'
    """
    if "## Types" in llm_output:
        header = llm_output.split("## Types")[1].split("## ")[0]
    else:
        header = llm_output

    dot_list = combine_blocks(header)

    if len(dot_list) == 0:
        dot_list = "\n".join([l for l in header.split("\n") if l.strip().startswith("-")])

    if dot_list.count("-") == 0:  # Keine Typen gefunden
        return {}

    types = dot_list.split('\n')
    types = [t.strip("- \n") for t in types if t.strip("- \n")]  # Leere Strings und Bindestriche entfernen

    return {
        t.split(":")[0].strip().replace(" ", "_"):
            t.split(":")[0].strip().replace(" ", "_") + ": " + t.split(":")[1].strip()
        for t in types if ":" in t
    }

def parse_hierarchy(llm_output):
    """
    Extrahiert Hierarchien aus dem LLM-Output
    """
    if "## Hierarchy" in llm_output:
        header = llm_output.split("## Hierarchy")[1].split("## ")[0]
    else:
        header = llm_output

    # Ähnlich wie bei parse_types implementieren...
    # Für den Prototyp vereinfacht
    return header

# Weitere Parse-Funktionen für andere Schritte hier hinzufügen...

# Schritte definieren mit entsprechenden Parse-Funktionen
steps = [
    {"name": "type_extraction", "dir": "prompts/1_type_extraction", "parser": parse_types},
    {"name": "hierarchy_construction", "dir": "prompts/2_hierarchy_construction", "parser": parse_hierarchy},
    # Weitere Schritte mit entsprechenden Parsern...
]

def run_nl2plan_chain(natural_language_input, feedback_iterations=1):
    results = {}
    context = {"original_input": natural_language_input, "domain_desc": natural_language_input}

    for step in steps:
        step_name = step["name"]
        step_dir = step["dir"]
        parser = step["parser"]

        # Prompts laden
        main_prompt_template = load_prompt(os.path.join(step_dir, "main.txt"))
        feedback_prompt_template = load_prompt(os.path.join(step_dir, "feedback.txt"))

        # Hauptprompt formatieren
        main_prompt = ChatPromptTemplate.from_template(main_prompt_template)
        main_input = {**context, "step": step_name}
        main_messages = main_prompt.format_messages(**main_input)

        # Initialer Output des Haupt-LLMs
        current_output = llm.invoke(main_messages).content

        # Output parsen
        parsed_output = parser(current_output)

        # Bei type_extraction: Parsed Types in eine Liste umwandeln für Feedback
        if step_name == "type_extraction":
            type_str = "\n".join([f"- {v}" for v in parsed_output.values()])
            context["type_list"] = type_str

        # Speichern der initialen Ergebnisse
        current_result = {
            "step": step_name,
            "input_context": context.copy(),
            "iterations": [
                {
                    "iteration": 0,
                    "main_prompt": main_prompt_template,
                    "main_output": current_output,
                    "parsed_output": parsed_output,
                    "feedback": None
                }
            ]
        }

        # Feedback-Schleife
        for i in range(feedback_iterations):
            # Feedback-Prompt formatieren und ausführen
            feedback_prompt = ChatPromptTemplate.from_template(feedback_prompt_template)

            # Spezifische Anpassung für jeden Schritt
            feedback_input = {**context, "main_output": current_output, "step": step_name}

            feedback_messages = feedback_prompt.format_messages(**feedback_input)
            feedback_output = llm.invoke(feedback_messages).content

            # Überprüfen, ob Feedback leer ist
            if "no feedback" in feedback_output.lower() or len(feedback_output.strip()) == 0:
                print(f"Schritt {step_name}: Kein Feedback erhalten.")
                continue

            # Feedback formatieren wie im Originalcode
            formatted_feedback = "## Feedback\n" + feedback_output
            formatted_feedback += "\n\nStart with a \"## Response\" header, then re-iterate an updated version of the \"## Types\" header."
            formatted_feedback += "\n\n## Response\n"

            # Kombinierter Prompt für den nächsten Durchlauf erstellen
            combined_input = f"""
# Original Task
{natural_language_input}

# Previous Output
{current_output}

# Feedback
{formatted_feedback}

Please provide an improved response based on the feedback.
"""

            # Durchlauf mit kombiniertem Input
            combined_prompt = ChatPromptTemplate.from_template(main_prompt_template + "\n\n{combined_input}")
            combined_messages = combined_prompt.format_messages(combined_input=combined_input, **context)

            # Neuen Output erhalten
            current_output = llm.invoke(combined_messages).content

            # Neuen Output parsen
            parsed_output = parser(current_output)

            # Aktualisierung des Kontexts bei type_extraction
            if step_name == "type_extraction":
                type_str = "\n".join([f"- {v}" for v in parsed_output.values()])
                context["type_list"] = type_str

            # Iteration speichern
            current_result["iterations"].append({
                "iteration": i+1,
                "feedback_prompt": feedback_prompt_template,
                "feedback_output": feedback_output,
                "main_output_after_feedback": current_output,
                "parsed_output": parsed_output
            })

        # Finales Ergebnis speichern
        results[step_name] = current_result

        # Kontext für den nächsten Schritt aktualisieren
        context[step_name + "_result"] = current_output
        context[step_name + "_parsed"] = parsed_output

    return results

# Ausführungsfunktion
def execute_nl2plan(input_text, feedback_iterations=1):
    results = run_nl2plan_chain(input_text, feedback_iterations)

    # Übersichtliche Zusammenfassung ausgeben
    print(f"NL2Plan Chain mit {feedback_iterations} Feedback-Iterationen abgeschlossen\n")

    for step_name, result in results.items():
        print(f"\n--- {step_name.upper()} ---")

        # Initiale Ausgabe und geparste Daten
        initial_output = result["iterations"][0]["main_output"]
        parsed_output = result["iterations"][0]["parsed_output"]

        print(f"Initiale Ausgabe: {initial_output[:100]}...")
        print(f"Geparste Daten: {parsed_output}")

        # Feedback-Iterationen
        for iteration in result["iterations"][1:]:
            print(f"\nIteration {iteration['iteration']}:")
            print(f"  Feedback: {iteration['feedback_output'][:100]}...")
            print(f"  Verbesserte Ausgabe: {iteration['main_output_after_feedback'][:100]}...")
            print(f"  Geparste Daten nach Feedback: {iteration['parsed_output']}")

        print("\n" + "-"*50)

    return results

# Beispiel
test_input = "Erstelle eine Logistik-Planung für den Transport von Paketen zwischen München und Berlin mit Lastwagen und Flugzeugen."
nl2plan_results = execute_nl2plan(test_input, feedback_iterations=2)