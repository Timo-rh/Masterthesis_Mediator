from __future__ import annotations
from utils.pddl_parser import *

# =============================================================================
# Initialisierung
# =============================================================================

#Initalisierung des Mediator-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
mediator_llm = chat_models.init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0, timeout=300)

#Initalisierung des Feedback-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
feedback_llm = chat_models.init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0, timeout=300)


# =============================================================================
# Type-Extraction Schritt
# =============================================================================

def regular_type_extraction(state: NL2PlanState):
    """Führt Type_Extraction-Generierung aus."""
    with open(os.path.join(type_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = mediator_llm.with_structured_output(Type_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n## Task\n{task}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    type_extraction_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task})
    #Gibt Liste an types zurück
    return {"types": type_extraction_call.types}


def give_type_extraction_feedback(state: NL2PlanState):
    """Führt Feedback für Type_Extraction aus."""
    with open(os.path.join(type_extraction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = feedback_llm#.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n## Task\n{task}\n## Types\n{first_solution}")])
    feedback_chain = input_prompt | type_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types})

    #Gibt Feedback für Schritt "0" zurück
    return {"feedback": [feedback_call.content]}


def type_extraction_with_feedback(state:NL2PlanState):
    """Führt Type_Extraction-Generierung mit Feedback aus."""
    with open(os.path.join(type_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = mediator_llm.with_structured_output(Type_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n## Task\n{task}## Types\n{first_solution}\n## Feedback\n{feedback}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    feedback = state.feedback[0]
    type_extraction_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types,
         "feedback": feedback})

    #Gibt Liste an types zurück
    return {"types": type_extraction_call.types}


# =============================================================================
# Hierarchy-Construction Schritt
# =============================================================================

def regular_hierarchy_construction(state: NL2PlanState):
    """Führt Hierarchie-Generierung aus."""
    with open(os.path.join(type_hierarchy_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    hierarchy_construction_llm = mediator_llm.with_structured_output(Hierarchy)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n## Task\n{task}\n## Types\nThe types are:\n{types}")])
    hierarchy_construction_chain = input_prompt | hierarchy_construction_llm
    hierarchy_construction_call = hierarchy_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "types": state.types})

    #Gibt Hierarchie zurück
    return {"type_hierarchy": hierarchy_construction_call.hierarchy}



def give_hierarchy_construction_feedback(state: NL2PlanState):
    """Führt Feedback für Hierarchie-Construction aus."""
    with open(os.path.join(type_hierarchy_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    hierarchy_construction_llm = feedback_llm#.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Types\n{types}\n ## Hierarchy\n{first_solution}")])
    feedback_chain = input_prompt | hierarchy_construction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "types": state.types,
         "first_solution": state.type_hierarchy})

    #Gibt Feedback für Schritt "1" zurück
    return {"feedback": [feedback_call.content]}


def hierarchy_construction_with_feedback(state: NL2PlanState):
    """Führt Hierarchie-Generierung mit Feedback aus."""
    with open(os.path.join(type_hierarchy_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    hierarchy_construction_llm = mediator_llm.with_structured_output(Hierarchy)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n## Task\n{task}\n## Types\n{types}\n ## Hierarchy\n{first_solution} ## Feedback\n{feedback}")])
    hierarchy_construction_chain = input_prompt | hierarchy_construction_llm
    feedback = state.feedback[1]
    hierarchy_construction_call = hierarchy_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "types": state.types,
         "first_solution": state.type_hierarchy,
         "feedback": feedback})

    #Gibt Hierarchie zurück
    return {"type_hierarchy": hierarchy_construction_call.hierarchy}

# =============================================================================
# Action-Extraction Schritt
# =============================================================================

def regular_action_extraction(state: NL2PlanState):
    """Führt Aktionsgenerierung aus."""
    with open(os.path.join(action_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_extraction_llm = mediator_llm.with_structured_output(Nominated_Action_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}")])
    action_extraction_chain = input_prompt | action_extraction_llm
    action_extraction_call = action_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy})

    # Gibt Liste an benötigten Aktionen zurück
    return {"nominated_actions": action_extraction_call.actions}


def give_action_extraction_feedback(state: NL2PlanState):
    """Führt Feedback für Aktionsgenerierung aus."""
    with open(os.path.join(action_extraction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    action_extraction_llm = feedback_llm#.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\n## Actions\n{first_solution}")])
    feedback_chain = input_prompt | action_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "first_solution": state.nominated_actions})

    #Gibt Feedback für Schritt "2" zurück
    return {"feedback": [feedback_call.content]}


def action_extraction_with_feedback(state: NL2PlanState):
    """Führt Aktionsgenerierung aus."""
    with open(os.path.join(action_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_extraction_llm = mediator_llm.with_structured_output(Nominated_Action_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\n## Actions\n{first_solution}\n{feedback}")])
    action_extraction_chain = input_prompt | action_extraction_llm
    feedback = state.feedback[2]
    action_extraction_call = action_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "first_solution": state.nominated_actions,
         "feedback": feedback})

    # Gibt Liste an benötigten Aktionen zurück
    return {"nominated_actions": action_extraction_call.actions}

# =============================================================================
# Action-Construction Schritt
# =============================================================================

def construct_predicates_for_one_action(state: NL2PlanState, action: Nominated_Action):
    """Konstruirert in einem Call alle benötigten Prädikate für eine Aktion."""
    with open(os.path.join(action_construction_prompts, "predicate_generation.txt")) as f:
        system_message = f.read().strip()
    predicate_construction_llm = mediator_llm.with_structured_output(Predicate_Defintion_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human",
                                                                        "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:\n{nominated_actions}\n ## Action {action_to_create}\n ### Already defined predicates {predicates}")])
    predicate_construction_chain = input_prompt | predicate_construction_llm
    predicate_construction_call = predicate_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "nominated_actions": state.nominated_actions,
         "action_to_create": action,
         "predicates": state.predicates})

    # Gibt eine Liste an Prädikaten zurück
    return predicate_construction_call


def construct_one_action(state: NL2PlanState, action: Nominated_Action):
    """Generiert eine Aktion."""
    with open(os.path.join(action_construction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = mediator_llm.with_structured_output(Action_)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:\n{nominated_actions}\n ## Action {action_to_create}\n ### Available Predicates {predicates}")])
    action_construction_chain = input_prompt | action_construction_llm
    action_construction_call = action_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "nominated_actions": state.nominated_actions,
         "action_to_create": action,
         "predicates": state.predicates})

    # Gibt eine Aktion zurück
    return action_construction_call

def action_construction(state: NL2PlanState):
    """Konstruiert alle nominierten Aktionen."""
    constructed_actions = []
    all_predicates = []

    for action in state.nominated_actions:
        # Konstruiere die benötigten Prädikate für die Aktion
        predicates_list = construct_predicates_for_one_action(state, action)

        # Zugriff auf die predicates-Liste des zurückgegebenen Objekts
        predicates = predicates_list.predicates

        # Konstruiere die Aktion mit construct_one_action
        constructed_action = construct_one_action(state, action)

        # Füge die konstruierte Aktion zur Liste hinzu
        constructed_actions.append(constructed_action)

        # Füge nur neue, einzigartige Prädikate hinzu
        for new_pred in predicates:
            if not any(pred.name == new_pred.name for pred in all_predicates):
                all_predicates.append(new_pred)

    # Gib alle erfolgreich konstruierten Aktionen zurück
    return {"actions": constructed_actions,
            "predicates": all_predicates}


def give_action_construction_feedback(state: NL2PlanState):
    """Führt Feedback für die Aktionsgenerierung aus."""
    with open(os.path.join(action_construction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = feedback_llm#.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\n## Actions\n{generated_actions}\n## Available Predicates\nThe following are the predicates which could be used:\n{generated_predicates}")])
    feedback_chain = input_prompt | action_construction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "generated_actions": state.actions,
         "generated_predicates": state.predicates})

    # Gibt Feedback für Schritt "3" zurück
    return {"feedback": [feedback_call.content]}


def construct_predicates_for_one_action_with_feedback(state: NL2PlanState, action: Nominated_Action):
    """Konstruirert in einem Call alle benötigten Prädikate für alle Aktionen."""
    with open(os.path.join(action_construction_prompts, "predicate_generation.txt")) as f:
        system_message = f.read().strip()
    predicate_construction_llm = mediator_llm.with_structured_output(Predicate_Defintion_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human",
                                                                        "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:\n{nominated_actions}\n ## Action {action_to_create}\n ### Already defined predicates {predicates}\n## Feedback\n{feedback}")])
    predicate_construction_chain = input_prompt | predicate_construction_llm
    feedback = state.feedback[3]
    predicate_construction_call = predicate_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "nominated_actions": state.nominated_actions,
         "action_to_create": action,
         "predicates": state.predicates,
         "feedback": feedback})

    # Gibt eine Liste an Prädikaten zurück
    return predicate_construction_call


def construct_one_action_with_feedback(state: NL2PlanState, action: Nominated_Action):
    """Generiert eine Aktion,"""
    with open(os.path.join(action_construction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = mediator_llm.with_structured_output(Action_)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n## Task\n{task}\n## Available Types\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:\n{nominated_actions}\n ## Action {action_to_create}\n ### Available Predicates {predicates}\n ## Feedback\n{feedback}")])
    action_construction_chain = input_prompt | action_construction_llm
    feedback = state.feedback[3]
    # Bereits generierte Aktionen werden nicht als Input verwendet, da sie über das Context Window hinaus gehen würden.
    action_construction_call = action_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "nominated_actions": state.nominated_actions,
         "action_to_create": action,
         "predicates": state.predicates,
         "feedback": feedback})

    # Gibt konstruierte Aktion zurück
    return action_construction_call


def action_construction_with_feedback(state: NL2PlanState):
    """Konstruiert alle nominierten Aktionen."""
    constructed_actions = []
    all_predicates = []

    for action in state.nominated_actions:
        # Konstruiere die benötigten Prädikate für die Aktion
        predicates_list = construct_predicates_for_one_action_with_feedback(state, action)

        # Zugriff auf die predicates-Liste des zurückgegebenen Objekts
        predicates = predicates_list.predicates

        # Konstruiere die Aktion mit construct_one_action
        constructed_action = construct_one_action_with_feedback(state, action)

        # Füge die konstruierte Aktion zur Liste hinzu
        constructed_actions.append(constructed_action)

        # Füge nur neue, einzigartige Prädikate hinzu
        for new_pred in predicates:
            if not any(pred.name == new_pred.name for pred in all_predicates):
                all_predicates.append(new_pred)

    # Gib alle erfolgreich konstruierten Aktionen zurück
    return {"actions": constructed_actions,
            "predicates": all_predicates}


# =============================================================================
# Task - Extraction Schritt
# =============================================================================

def regular_objects_extraction(state: NL2PlanState):
    """Führt die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "objects_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(ObjectInstances)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}")])
    object_extraction_chain = input_prompt | task_extraction_llm
    object_extraction_call = object_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates})


    # Gibt Objektinstanzen zurück
    return {"object_instances": object_extraction_call}


def regular_initial_state_extraction(state: NL2PlanState):
    """Generiert Ausgangszustand für die Task-Extraction."""
    with open(os.path.join(state_goal_extraction_prompts, "initial_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(InitialState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n## Object Instances\n{object_instances}")])
    initial_state_chain = input_prompt | task_extraction_llm
    initial_state_call = initial_state_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances})
    # Gibt Zielzustand zurück
    return {"initial_state": initial_state_call}


def regular_goal_state_extraction(state: NL2PlanState):
    """Generiert Ausgangszustand für die Task-Extraction."""
    with open(os.path.join(state_goal_extraction_prompts, "goal_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(GoalState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n## Objects\n{object_instances}")])
    goal_state_chain = input_prompt | task_extraction_llm
    goal_state_call = goal_state_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances})

    # Gibt Zielzustand zurück
    return {"goal_state": goal_state_call}


def give_task_extraction_feedback(state: NL2PlanState):
    """Führt Feedback für die Taskgenerierung aus."""
    with open(os.path.join(state_goal_extraction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"),
         ("human", "## Domain\n{domain_desc}\n## Task\n{task}\n## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Object Instances\n{object_instances}\n## Initial State\n{initial_state}\n## Goal State\n{goal_state}")])
    feedback_chain = input_prompt | task_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances,
         "initial_state": state.initial_state,
         "goal_state": state.goal_state})

    # Gibt Feedback für Schritt "4" zurück
    return {"feedback": [feedback_call.feedback]}


def objects_extraction_with_feedback(state: NL2PlanState):
    """Führt erneut die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "objects_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(ObjectInstances)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n##Objects\n{object_instances}\n## Feedback\n{feedback}")])
    object_extraction_chain = input_prompt | task_extraction_llm
    object_extraction_call = object_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances,
         "feedback": state.feedback[0]})

    # Gibt Objektinstanzen zurück
    return {"object_instances": object_extraction_call}


def initial_state_extraction_with_feedback(state: NL2PlanState):
    """Führt erneut die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "initial_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(InitialState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n##Objects\n{object_instances}\n## Feedback\n{feedback}")])
    state_extraction_chain = input_prompt | task_extraction_llm
    state_extraction_call = state_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances,
         "feedback": state.feedback[1]})

    # Gibt Objektinstanzen zurück
    return {"initial_state": state_extraction_call}


def goal_state_extraction_with_feedback(state: NL2PlanState):
    """Führt erneut die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "objects_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(GoalState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n##Objects\n{object_instances}\n## Feedback\n{feedback}")])
    goal_extraction_chain = input_prompt | task_extraction_llm
    goal_extraction_call = goal_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "object_instances": state.object_instances,
         "feedback": state.feedback[2]})

    # Gibt Objektinstanzen zurück
    return {"goal_state": goal_extraction_call}


# =============================================================================
# Planning Schritt
# =============================================================================

def domain_to_state(state: NL2PlanState):
    domain = create_domain(state)
    pddl_domain=str(domain)
    return {"pddl_domain": pddl_domain}


def problem_to_state(state: NL2PlanState):
    problem = create_problem(state)
    pddl_problem = str(problem)
    return {"pddl_problem": pddl_problem}


# =============================================================================
# Speichern des States und der PDDL
# =============================================================================

def save_complete_state(state: NL2PlanState):
    """
    Speichert den kompletten State als JSON.

    Args:
        state (NL2PlanState): Der aktuelle State mit allen Komponenten.

    Returns:
        dict: Dictionary mit dem kompletten State.
    """
    # Erstelle Ordnername nach Schema DDMMYYYY-domain-task
    from datetime import datetime
    timestamp = datetime.now().strftime("%d%m%Y")
    folder_name = f"{timestamp}-{state.domain_name}-{state.task_name}"

    # Bestimme den Basispfad basierend auf Feedback
    base_dir = 'results/mit_feedback' if state.feedback else 'results/ohne_feedback'
    target_dir = os.path.join(base_dir, folder_name)

    # Erstelle Ordner falls nicht vorhanden
    os.makedirs(target_dir, exist_ok=True)

    # Speichere den State als JSON
    state_path = os.path.join(target_dir, 'state.json')
    with open(state_path, 'w') as f:
        f.write(state.model_dump_json(indent=2))

    print(f"Kompletter State wurde in {state_path} gespeichert.")
    return {"complete_state": state}


def save_pddl_files(state: NL2PlanState):
    """
    Speichert die PDDL-Domain und das PDDL-Problem als separate Dateien im gleichen Verzeichnis
    wie die state.json-Datei.
    """
    # Bestimme den Ordnerpfad, der bereits von save_complete_state erstellt wurde
    timestamp = datetime.now().strftime("%d%m%Y")
    folder_name = f"{timestamp}-{state.domain_name}-{state.task_name}"

    # Basispfad basierend auf Feedback
    base_dir = 'results/mit_feedback' if state.feedback else 'results/ohne_feedback'
    target_dir = os.path.join(base_dir, folder_name)

    # Speichere PDDL-Domain
    domain_path = os.path.join(target_dir, 'domain.pddl')
    # with open(domain_path, 'w') as f:
    #     f.write(state.pddl_domain)
    with open(domain_path, 'w', encoding='utf-8') as f:
        f.write(state.pddl_domain.replace('−', '-').replace('–', '-').replace('—', '-'))

    # Speichere PDDL-Problem
    problem_path = os.path.join(target_dir, 'problem.pddl')
    # with open(problem_path, 'w') as f:
    #     f.write(state.pddl_problem)
    with open(problem_path, 'w', encoding='utf-8') as f:
        f.write(state.pddl_problem.replace('−', '-').replace('–', '-').replace('—', '-'))

    print(f"PDDL-Domain wurde in {domain_path} gespeichert")
    print(f"PDDL-Problem wurde in {problem_path} gespeichert")

    return {"domain_path": domain_path, "problem_path": problem_path}