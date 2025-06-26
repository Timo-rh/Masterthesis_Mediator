from __future__ import annotations
import os
from utils.paths import *
from langchain import chat_models
from langchain_core.prompts import ChatPromptTemplate
from pddl.core import Problem, Domain
from pddl.requirements import Requirements
from src.pddl_parser import *

# class Config_Schema(TypedDict): #TODO: aus Obsidian übernehmen & Config festlegen für init_chat_model (.with_config-Methode?)
#     """Configurable parameters for the agent.
#
#     Set these when creating assistants OR when invoking the graph.
#     See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
#     https://langchain-ai.github.io/langgraph/concepts/low_level/#graph-migrations
#     """
#
#     mediator_llm: Literal["anthropic:claude-4", "deepseek:deepseek-r-1", "openai:gpt-4o"] #TODO: neue Integrationspakete in die requirements packen
#     feedback_llm: Literal["anthropic:claude-4", "deepseek:deepseek-r-1", "openai:gpt-4o"]
#
# #Config-Defaults
#
#
#
# # Initialisiere das Mediator-LLM direkt aus der config
# mediator_llm = init_chat_model(config["configurable"]["mediator_llm"])
#
# # Initialisiere das Feedback-LLM direkt aus der config
# feedback_llm = init_chat_model(config["configurable"]["feedback_llm"])

# =============================================================================
# Initialisierung
# =============================================================================

#https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html#langchain.chat_models.base.init_chat_model
#Initalisierung des Mediator-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
mediator_llm = chat_models.init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0, timeout=300)
#mediator_llm = chat_models.init_chat_model("gpt-4o", temperature=0, timeout=300)
#mediator_llm = chat_models.init_chat_model("gemini-1.5-flash", temperature=0, timeout=300)
#mediator_llm = chat_models.init_chat_model("deepseek:deepseek-r-1", temperature=0, timeout=300)

#Initalisierung des Feedback-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
feedback_llm = chat_models.init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0, timeout=300)
#feedback_llm = chat_models.init_chat_model("gpt-4o", temperature=0, timeout=300)


# =============================================================================
# Type-Extraction Schritt
# =============================================================================
#TODO: Few_shot_prompt - Beispiele für structured_output erzeugen (siehe :https://python.langchain.com/docs/how_to/structured_output/)

#Type Extraction - Node
def regular_type_extraction(state: NL2PlanState):  #TODO: domain_and_task ist variabel und wird bei Start angegeben
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


# def validate_hierarchy(state: NL2PlanState):
#     """Validiert die Hierarchie auf Vollständigkeit und Duplikate der Typen."""
#     # Sammle alle Typnamen aus der Hierarchie
#     hierarchy_type_names = []
#     for h_obj in state.type_hierarchy:
#         hierarchy_type_names.append(h_obj.parent_type.name)
#         if h_obj.child_types:
#             for child in h_obj.child_types:
#                 hierarchy_type_names.append(child.name)
#
#     # Prüfe, ob alle Typen aus state.types in der Hierarchie vorkommen
#     for type_obj in state.types:
#         if type_obj.name not in hierarchy_type_names:
#             raise KeyError(f"Type '{type_obj.name}' is not in the hierarchy.")
#
#     # Prüfe auf Duplikate in der Hierarchie
#     for type_name in hierarchy_type_names:
#         if hierarchy_type_names.count(type_name) > 1:
#             raise ValueError(f"Type '{type_name}' appears multiple times in the hierarchy.")
#
#     # Gibt den unveränderten State zurück
#     return state


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

def action_construction(state: NL2PlanState):
    """Konstruiert alle nominierten Aktionen."""
    constructed_actions = []
    all_predicates = []

    for action in state.nominated_actions:
        # Konstruiere die Aktion mit construct_one_action
        constructed_action, predicates = construct_one_action(state, action)

        # Füge die konstruierte Aktion zur Liste hinzu
        constructed_actions.append(constructed_action)

        # Füge die extrahierten Prädikate zur Liste hinzu
        all_predicates.extend(predicates)

    # Gib alle erfolgreich konstruierten Aktionen zurück
    return {"actions": constructed_actions,
            "predicates": all_predicates}


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

    extracted_predicates = []
    # Alle Predicates aus preconditions zusammenfassen
    for predicate_list in action_construction_call.preconditions.values():
        extracted_predicates.extend(predicate_list)
    # Alle Predicates aus effects zusammenfassen
    for predicate_list in action_construction_call.effects.values():
        extracted_predicates.extend(predicate_list)


    # Gibt eine Aktion zurück
    return action_construction_call, extracted_predicates


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
    """Konstruiert alle nominierten Aktionen und validiert sie."""
    constructed_actions = []

    for action in state.nominated_actions:
        # Konstruiere die Aktion mit construct_one_action
        constructed_action = construct_one_action_with_feedback(state, action)

        # Füge die konstruierte Aktion zur Liste hinzu
        constructed_actions.append(constructed_action)

    # Gib alle erfolgreich konstruierten Aktionen zurück
    return {"actions": constructed_actions}

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
    return {"object_instances": object_extraction_call.objects}


def regular_initial_state_extraction(state: NL2PlanState):
    """Generiert Ausgangszustand für die Task-Extraction."""
    with open(os.path.join(state_goal_extraction_prompts, "initial_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(InitialState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}")])
    initial_state_chain = input_prompt | task_extraction_llm
    initial_state_call = initial_state_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates})
    print(initial_state_call) #TODO: Überprüfen, ob der Fehler noch einmal auftritt
    # Gibt Zielzustand zurück
    return {"initial_state": initial_state_call.initial_state_predicates}


def regular_goal_state_extraction(state: NL2PlanState):
    """Generiert Ausgangszustand für die Task-Extraction."""
    with open(os.path.join(state_goal_extraction_prompts, "goal_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(GoalState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}")])
    goal_state_chain = input_prompt | task_extraction_llm
    goal_state_call = goal_state_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates})

    # Gibt Zielzustand zurück
    return {"goal_state": goal_state_call.goal_state_predicates}


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
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n## Feedback\n{feedback}")])
    object_extraction_chain = input_prompt | task_extraction_llm
    object_extraction_call = object_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "feedback": state.feedback[0]})

    # Gibt Objektinstanzen zurück
    return {"object_instances": object_extraction_call.objects}


def initial_state_extraction_with_feedback(state: NL2PlanState):
    """Führt erneut die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "initial_state_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(InitialState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n## Feedback\n{feedback}")])
    state_extraction_chain = input_prompt | task_extraction_llm
    state_extraction_call = state_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "feedback": state.feedback[1]})

    # Gibt Objektinstanzen zurück
    return {"initial_state": state_extraction_call.initial_state_predicates}


def goal_state_extraction_with_feedback(state: NL2PlanState):
    """Führt erneut die Objektgenerierung für die Task-Extraction aus."""
    with open(os.path.join(state_goal_extraction_prompts, "objects_main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(GoalState)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "## Types\n{type_hierarchy}\n ## Predicates\n{predicates}\n## Domain\n{domain_desc}\n## Task\n{task}\n## Feedback\n{feedback}")])
    goal_extraction_chain = input_prompt | task_extraction_llm
    goal_extraction_call = goal_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "feedback": state.feedback[2]})

    # Gibt Objektinstanzen zurück
    return {"goal_state": goal_extraction_call.goal_state_predicates}



# =============================================================================
# Planning Schritt
# =============================================================================

# Requirements setzen
requirements = [
        Requirements.STRIPS,
        Requirements.TYPING,
        Requirements.EQUALITY,
        Requirements.NEG_PRECONDITION,
        Requirements.DIS_PRECONDITION,
        Requirements.UNIVERSAL_PRECONDITION,
        Requirements.CONDITIONAL_EFFECTS,
    ]


# Domain erzeugen
def create_domain(state: NL2PlanState):
    domain = Domain(
        name=state.domain_name,
        requirements=requirements,
        types=create_types(state),
        predicates=create_predicates(state),
        actions=create_actions(state),
    )
    # Domäne im State speichern
    return domain

def domain_to_state(domain: Domain):
    return {"pddl_domain": domain}

#Problem erzeugen
def create_problem(state: NL2PlanState):
    problem = Problem(
        state.task_name,
        requirements=requirements,
        domain=state.pddl_domain,
        objects=create_objects(state),
        # init=create_initial_state(state),
        # goal=create_goal_state(state)
    )