from __future__ import annotations
from typing import Dict, Any
from langchain import chat_models
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from utils.paths import *
from src.agent.states import *
import os
from operator import add

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

#Initalisierung des Feedback-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
feedback_llm = chat_models.init_chat_model("gpt-4o", temperature=0, timeout=300)

#TODO: llms in initialisierungsfunktion aufnehmen
def initialize_mediator(state: NL2PlanState, domain_name: str, task_name, feedback_type=Literal["llm_feedback", "human_feedback"]):
    #Domäne setzen (Variable aus paths.py)
    with open(os.path.join(domain_name, "desc.txt")) as f:
        domain = f.read().strip()

    #task setzen (Variable aus paths.py)
    with open(os.path.join(task_name, "task1.txt")) as f:   #TODO: auf mehrere Tasks ausweiten
        task = f.read().strip()

    #feedback_type festlegen
    feedback_type = feedback_type

    return {"domain_desc": domain, "task": task, "feedback_type": feedback_type}



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
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n{task}")])
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
    type_extraction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n{task}\n{first_solution}")])
    feedback_chain = input_prompt | type_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types
        }
    )
    #Gibt Feedback für Schritt "0" zurück
    return {"feedback": {0: feedback_call.feedback}}


def type_extraction_with_feedback(state:NL2PlanState):
    """Führt Type_Extraction-Generierung mit Feedback aus."""
    with open(os.path.join(type_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = mediator_llm.with_structured_output(Type_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n{task}\n{first_solution}\n{feedback}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    feedback = state.feedback.get(0)
    type_extraction_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types,
         "feedback": feedback})
    #Gibt Liste an types zurück
    return {"types": type_extraction_call.types}


# # Conditional_Edge
# def route_to_hierarchy_construction(state: NL2PlanState):
#     """Weiterleiten zum Hierarchy_Construction-Node oder mediator_llm-Node."""
#     if state.feedback.get(0) == "blue":
#         return "Hierarchy_Construction"
#     else:
#         return "mediator_llm"


# =============================================================================
# Hierarchy-Construction Schritt
# =============================================================================

def regular_hierarchy_construction(state: NL2PlanState):
    """Führt Hierarchie-Generierung aus."""
    with open(os.path.join(type_hierarchy_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    hierarchy_construction_llm = mediator_llm.with_structured_output(Hierarchy)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n{task}\n{types}")])
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
    hierarchy_construction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{types}\n{first_solution}")])
    feedback_chain = input_prompt | hierarchy_construction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "types": state.types,
         "first_solution": state.type_hierarchy})

    #Gibt Feedback für Schritt "1" zurück
    return {"step": 1, "feedback": feedback_call.feedback}


def hierarchy_construction_with_feedback(state: NL2PlanState):
    """Führt Hierarchie-Generierung mit Feedback aus."""
    with open(os.path.join(type_hierarchy_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    hierarchy_construction_llm = mediator_llm.with_structured_output(Hierarchy)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}\n{task}\n{types}\n{first_solution}\n{feedback}")])
    hierarchy_construction_chain = input_prompt | hierarchy_construction_llm
    hierarchy_construction_call = hierarchy_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "types": state.types,
         "first_solution": state.type_hierarchy,
         "feedback": state.feedback.get(1)})

    #Gibt Hierarchie zurück
    return {"type_hierarchy": hierarchy_construction_call.hierarchy}


def validate_hierarchy(state: NL2PlanState):
    """Validiert die Hierarchie auf Vollständigkeit und Duplikate der Typen."""
    # Sammle alle Typnamen aus der Hierarchie
    hierarchy_type_names = []
    for h_obj in state.type_hierarchy:
        hierarchy_type_names.append(h_obj.parent_type.name)
        if h_obj.child_types:
            for child in h_obj.child_types:
                hierarchy_type_names.append(child.name)

    # Prüfe, ob alle Typen aus state.types in der Hierarchie vorkommen
    for type_obj in state.types:
        if type_obj.name not in hierarchy_type_names:
            raise KeyError(f"Type '{type_obj.name}' is not in the hierarchy.")

    # Prüfe auf Duplikate in der Hierarchie
    for type_name in hierarchy_type_names:
        if hierarchy_type_names.count(type_name) > 1:
            raise ValueError(f"Type '{type_name}' appears multiple times in the hierarchy.")

    # Gibt den unveränderten State zurück
    return state


# =============================================================================
# Action-Extraction Schritt
# =============================================================================

def regular_action_extraction(state: NL2PlanState):
    """Führt Aktionsgenerierung aus."""
    with open(os.path.join(action_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_extraction_llm = mediator_llm.with_structured_output(Nominated_Action_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}")])
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
    action_extraction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{first_solution}")])
    feedback_chain = input_prompt | action_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "first_solution": state.nominated_actions})

    #Gibt Feedback für Schritt "2" zurück
    return {"step": 2, "feedback": feedback_call.feedback}


def action_extraction_with_feedback(state: NL2PlanState):
    """Führt Aktionsgenerierung aus."""
    with open(os.path.join(action_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_extraction_llm = mediator_llm.with_structured_output(Nominated_Action_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{first_solution}\n{feedback}")])
    action_extraction_chain = input_prompt | action_extraction_llm
    action_extraction_call = action_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "first_solution": state.nominated_actions,
         "feedback": state.feedback.get(2)})

    # Gibt Liste an benötigten Aktionen zurück
    return {"nominated_actions": action_extraction_call.actions}

# =============================================================================
# Action-Construction Schritt
# =============================================================================

def action_construction(state: NL2PlanState):
    """Konstruiert alle nominierten Aktionen."""
    constructed_actions = []

    for action in state.nominated_actions:
        # Konstruiere die Aktion mit construct_one_action
        constructed_action = construct_one_action(state, action)

        # Füge die konstruierte Aktion zur Liste hinzu
        constructed_actions.append(constructed_action)

    # Gib alle erfolgreich konstruierten Aktionen zurück
    return {"actions": constructed_actions}


def construct_one_action(state: NL2PlanState, action: Nominated_Action):
    """Generiert eine Aktion."""
    with open(os.path.join(action_construction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = mediator_llm.with_structured_output(Action)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:{nominated_actions}\n ## Action {action_to_create}\n ### Available Predicates {predicates}")])
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
    # speichert Predicate-Liste im State
    state.predicates = extracted_predicates

    # Gibt eine Aktion zurück
    return action_construction_call


def give_action_construction_feedback(state: NL2PlanState):
    """Führt Feedback für die Aktionsgenerierung aus."""
    with open(os.path.join(action_construction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{generated_actions}\n{generated_predicates}")])
    feedback_chain = input_prompt | action_construction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "generated_actions": state.actions,
         "generated_predicates": state.predicates})

    # Gibt Feedback für Schritt "3" zurück
    return {"step": 3, "feedback": feedback_call.feedback}


def construct_one_action_with_feedback(state: NL2PlanState, action: Nominated_Action):
    """Generiert eine Aktion,"""
    with open(os.path.join(action_construction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    action_construction_llm = mediator_llm.with_structured_output(Action)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\nThe following actions will be defined later and together they make up the entire domain:{nominated_actions}\n ## Action {action_to_create}\n ### Available Predicates {predicates}\n {feedback}")])
    action_construction_chain = input_prompt | action_construction_llm
    action_construction_call = action_construction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "nominated_actions": state.nominated_actions,
         "action_to_create": action,
         "predicates": state.predicates,
         "feedback": state.feedback.get(3)})

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

def regular_task_extraction(state: NL2PlanState):
    """Führt Taskgenerierung aus."""
    with open(os.path.join(state_goal_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(Task_Description)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{predicates}")])
    action_extraction_chain = input_prompt | task_extraction_llm
    action_extraction_call = action_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates})

    # Gibt Liste an benötigten Aktionen zurück
    return {"object_instances": action_extraction_call.object_instances,
            "initial_state": action_extraction_call.initial_state,
            "goal_state": action_extraction_call.goal_state}


def give_task_extraction_feedback(state: NL2PlanState):
    """Führt Feedback für die Taskgenerierung aus."""
    with open(os.path.join(state_goal_extraction_prompts, "feedback.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"),
         ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{predicates}\n{object_instances}\n{initial_state}\n{goal_state}")])
    feedback_chain = input_prompt | task_extraction_llm
    feedback_call = feedback_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "object_instances": state.object_instances,
         "predicates": state.predicates,
         "initial_state": state.initial_state,
         "goal_state": state.goal_state})

    # Gibt Feedback für Schritt "4" zurück
    return {"step": 4, "feedback": feedback_call.feedback}


def task_extraction_with_feedback(state: NL2PlanState):
    """Führt Taskgenerierung mit Feedback aus."""
    with open(os.path.join(state_goal_extraction_prompts, "main.txt")) as f:
        system_message = f.read().strip()
    task_extraction_llm = mediator_llm.with_structured_output(Task_Description)
    input_prompt = ChatPromptTemplate(
        [("system", "{system_message}"), ("human", "{domain_desc}\n{task}\n{type_hierarchy}\n{predicates}\n{feedback}")])
    action_extraction_chain = input_prompt | task_extraction_llm
    action_extraction_call = action_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "type_hierarchy": state.type_hierarchy,
         "predicates": state.predicates,
         "feedback": state.feedback.get(4)})

    # Gibt Liste an benötigten Aktionen zurück
    return {"object_instances": action_extraction_call.object_instances,
            "initial_state": action_extraction_call.initial_state,
            "goal_state": action_extraction_call.goal_state}

# =============================================================================
# Planning Schritt
# =============================================================================

def create_pddl():
    pass


# async def call_model(state: NL2PlanState, config: RunnableConfig) -> Dict[str, Any]:
#     """Process input and returns output.
#
#     Can use runtime configuration to alter behavior.
#     """
#     configuration = config["configurable"]
#     return {
#         "changeme": "output from call_model. "  #TODO: anpassen, um beim Start des Graphen das u.a. Modell festlegen zu können
#         f'Configured with {configuration.get("my_configurable_param")}'
#     }