# Manuelles Generieren von Domain und Problem
from src.agent.nodes_and_edges import save_complete_state
from src.agent.pddl_creation import create_domain, create_problem
import os
import json

from src.agent.states import NL2PlanState
import json
import os


def create_pddl_from_state_json(state_json_path: str):
    """
    Liest einen State aus einer JSON-Datei und erzeugt die entsprechenden PDDL-Dateien.

    Args:
        state_json_path: Pfad zur state.json Datei
    """
    # State aus JSON laden
    with open(state_json_path, 'r') as f:
        state_dict = json.load(f)

    # State-Objekt erstellen
    state = NL2PlanState.model_validate(state_dict)

    # Zielordner ist der gleiche wie der der JSON
    target_dir = os.path.dirname(state_json_path)

    try:
        # Domain und Problem mit existierenden Funktionen generieren
        domain = create_domain(state)
        problem = create_problem(state)

        # Dateipfade erstellen
        domain_path = os.path.join(target_dir, f'{state.domain_name}.pddl')
        problem_path = os.path.join(target_dir, f'{state.domain_name}-{state.task_name}.pddl')

        # PDDL-Dateien speichern
        with open(domain_path, 'w') as f:
            f.write(str(domain))
        with open(problem_path, 'w') as f:
            f.write(str(problem))

        print(f"PDDL-Dateien wurden erstellt in:\n{domain_path}\n{problem_path}")

        return domain_path, problem_path

    except Exception as e:
        print(f"Fehler beim Erstellen der PDDL-Dateien: {str(e)}")
        raise