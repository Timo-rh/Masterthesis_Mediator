from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import get_openai_callback
import os
import re

# Import der human_feedback-Funktion aus dem utils-Ordner
from utils.human_feedback import human_feedback

# Import der Pfade aus paths.py
from utils.paths import (
    type_extraction_prompts,
    type_hierarchy_prompts,
    action_extraction_prompts,
    action_construction_prompts,
    state_goal_extraction_prompts
)

# Hilfsfunktion für Textblöcke
def combine_blocks(text):
    """
    Extrahiert und kombiniert Codeblöcke, die mit ``` gekennzeichnet sind
    """
    code_blocks = re.findall(r'```(?:\w*\n)?(.*?)```', text, re.DOTALL)
    return "\n".join(code_blocks)

# Parse-Funktionen
def parse_types(llm_output):
    """
    Extrahiert Typen aus dem LLM-Output
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

# LLM-Feedback
def get_llm_feedback(llm, feedback_prompt):
    print("FEEDBACK PROMPT:\n", feedback_prompt)
    
    with get_openai_callback() as cb:
        feedback_messages = ChatPromptTemplate.from_template(feedback_prompt).format_messages()
        feedback_output = llm.invoke(feedback_messages).content
        feedback_token_usage = {
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_cost": cb.total_cost
        }
    
    if "no feedback" in feedback_output.lower() or len(feedback_output.strip()) == 0:
        print("FEEDBACK:\n", "Kein Feedback.")
        print(feedback_output)
        return None, feedback_token_usage
    else:
        print("FEEDBACK:\n", feedback_output)
        formatted_feedback = "## Feedback\n" + feedback_output
        formatted_feedback += "\n\nStart with a \"## Response\" header, then re-iterate an updated version of the \"## Types\" header."
        formatted_feedback += "\n\n## Response\n"
        return formatted_feedback, feedback_token_usage

# LLM-Klasse mit Token-Zähler
class LLMWithTokenCounter:
    def __init__(self, model="gpt-3.5-turbo", temperature=0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.reset_token_usage()
        
    def reset_token_usage(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        
    def get_response(self, input_text_or_messages):
        with get_openai_callback() as cb:
            if isinstance(input_text_or_messages, str):
                messages = ChatPromptTemplate.from_template(input_text_or_messages).format_messages()
                response = self.llm.invoke(messages).content
            else:  # Bereits formatierte Nachrichten
                response = self.llm.invoke(input_text_or_messages).content
                
            # Token-Nutzung aktualisieren
            self.total_prompt_tokens += cb.prompt_tokens
            self.total_completion_tokens += cb.completion_tokens
            self.total_cost += cb.total_cost
            
            return response
    
    def token_usage(self):
        return (self.total_prompt_tokens, self.total_completion_tokens)

# Hauptfunktion für jeden Schritt
def run_step(llm_conn, domain_desc_str, step_name, step_dir, parser_func, feedback_type=None):
    llm_conn.reset_token_usage()
    
    # Prompts laden
    with open(os.path.join(step_dir, "main.txt"), 'r', encoding='utf-8') as f:
        main_template = f.read().strip()
    main_prompt = main_template.replace('{domain_desc}', domain_desc_str)
    print("PROMPT:\n", main_prompt)

    # Initialer LLM-Output
    llm_output = llm_conn.get_response(main_prompt)
    print("LLM Output:\n", llm_output)

    # Output parsen
    parsed_output = parser_func(llm_output)
    
    # Ergebnisse formatieren (für type_extraction)
    if step_name == "type_extraction":
        parsed_str = "\n".join([f"- {v}" for v in parsed_output.values()])
    else:
        parsed_str = str(parsed_output)

    # Feedback-Prompt laden
    with open(os.path.join(step_dir, "feedback.txt"), 'r', encoding='utf-8') as f:
        feedback_template = f.read().strip()
    feedback_prompt = feedback_template.replace('{domain_desc}', domain_desc_str)
    
    # Platzhalter für verschiedene Schritte ersetzen
    if step_name == "type_extraction":
        feedback_prompt = feedback_prompt.replace('{type_list}', parsed_str)
    # Weitere Platzhalter für andere Schritte hier hinzufügen...

    # Feedback verarbeiten
    feedback_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_cost": 0}
    if feedback_type is not None:
        if feedback_type.lower() == "human":
            feedback_msg = human_feedback(f"\n\nDie extrahierten Daten sind:\n{parsed_str}\n")
            feedback_token_usage = None  # Kein Token-Verbrauch bei menschlichem Feedback
        else:
            feedback_msg, feedback_token_usage = get_llm_feedback(llm_conn.llm, feedback_prompt)
        
        if feedback_msg is not None:
            messages = [
                {'role': 'user', 'content': main_prompt},
                {'role': 'assistant', 'content': llm_output},
                {'role': 'user', 'content': feedback_msg}
            ]
            llm_response = llm_conn.get_response(messages)
            print("LLM Response nach Feedback:\n", llm_response)
            parsed_output = parser_func(llm_response)
            
            if step_name == "type_extraction":
                parsed_str = "\n".join([f"- {v}" for v in parsed_output.values()])
            else:
                parsed_str = str(parsed_output)

    # Ergebnisse ausgeben
    print(f"Extrahierte Daten für {step_name}:", parsed_str)

    # Token-Nutzung protokollieren
    in_tokens, out_tokens = llm_conn.token_usage()
    print(f"Token-Nutzung für {step_name}: {in_tokens} Input, {out_tokens} Output")
    
    # Ergebnisse zurückgeben
    return {
        "step_name": step_name,
        "main_prompt": main_prompt,
        "llm_output": llm_output,
        "parsed_output": parsed_output,
        "parsed_str": parsed_str,
        "feedback_prompt": feedback_prompt if feedback_type is not None else None,
        "feedback_msg": feedback_msg if feedback_type is not None and feedback_msg is not None else None,
        "llm_response_after_feedback": llm_response if feedback_type is not None and feedback_msg is not None else None,
        "token_usage": {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "feedback_tokens": feedback_token_usage
        }
    }

# Hauptfunktion für die gesamte Pipeline
def run_nl2plan_pipeline(domain_desc, feedback_type=None):
    # LLM initialisieren
    llm_conn = LLMWithTokenCounter(model="gpt-3.5-turbo", temperature=0)
    
    # Schritte definieren mit den importierten Pfaden
    steps = [
        {"name": "type_extraction", "dir": type_extraction_prompts, "parser": parse_types},
        {"name": "hierarchy_construction", "dir": type_hierarchy_prompts, "parser": parse_types},  # Hier müsste ein eigener Parser verwendet werden
        {"name": "action_extraction", "dir": action_extraction_prompts, "parser": parse_types},  # Hier müsste ein eigener Parser verwendet werden
        {"name": "action_construction", "dir": action_construction_prompts, "parser": parse_types},  # Hier müsste ein eigener Parser verwendet werden
        {"name": "task_extraction", "dir": state_goal_extraction_prompts, "parser": parse_types}  # Hier müsste ein eigener Parser verwendet werden
    ]
    
    results = {}
    context = {"domain_desc": domain_desc}
    
    # Jeden Schritt ausführen
    for step in steps:
        step_name = step["name"]
        step_dir = step["dir"]
        parser = step["parser"]
        
        step_result = run_step(llm_conn, domain_desc, step_name, step_dir, parser, feedback_type)
        results[step_name] = step_result
        
        # Kontext für den nächsten Schritt aktualisieren
        context[step_name + "_result"] = step_result["parsed_output"]
    
    # Gesamtergebnisse zurückgeben
    return results

# Ausführungsfunktion
def execute_nl2plan(input_text, feedback_type=None):
    """
    Führt die NL2Plan-Pipeline aus
    
    Args:
        input_text (str): Die zu verarbeitende Domänenbeschreibung
        feedback_type (str, optional): Art des Feedbacks ('llm', 'human' oder None)
    """
    print("\n" + "="*50)
    print(f"AUSFÜHRUNG VON NL2PLAN MIT FEEDBACK-TYP: {feedback_type}")
    print("="*50)
    
    results = run_nl2plan_pipeline(input_text, feedback_type)
    
    # Zusammenfassung ausgeben
    print("\n" + "="*50)
    print("ZUSAMMENFASSUNG")
    print("="*50)
    
    total_in_tokens = 0
    total_out_tokens = 0
    
    for step_name, result in results.items():
        print(f"\n--- {step_name.upper()} ---")
        print(f"Extrahierte Daten: {result['parsed_str'][:200]}...")
        
        # Token-Nutzung
        in_tokens = result["token_usage"]["input_tokens"]
        out_tokens = result["token_usage"]["output_tokens"]
        total_in_tokens += in_tokens
        total_out_tokens += out_tokens
        
        print(f"Token-Nutzung: {in_tokens} Input, {out_tokens} Output")
        
        # Feedback-Informationen
        if result.get("feedback_msg"):
            print(f"Feedback wurde angewendet.")
    
    print("\n" + "="*50)
    print(f"GESAMTE TOKEN-NUTZUNG: {total_in_tokens} Input, {total_out_tokens} Output")
    print("="*50)
    
    return results

# Beispielausführung
if __name__ == "__main__":
    domain_desc = "The AI agent here is a logistics planner that has to plan to transport packages within the locations in a city through a truck and between cities through an airplane. Within a city, the locations are directly linked, allowing trucks to travel between any two of these locations. Similarly, cities are directly connected to each other allowing airplanes to travel between any two cities. Also, there is no limit to how many packages a truck or plane can carry (so in theory a truck or plane can carry an infinite number of packages)."
    
    # Mit LLM-Feedback ausführen
    nl2plan_results = execute_nl2plan(domain_desc, feedback_type="llm")
    
    # Optional: Mit menschlichem Feedback ausführen
    # nl2plan_results = execute_nl2plan(domain_desc, feedback_type="human")