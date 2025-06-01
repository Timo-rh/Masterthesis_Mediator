from __future__ import annotations
from typing import Dict, Any
from langchain import chat_models
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from utils.paths import type_extraction_prompts as prompt_dir
from src.agent.states import *
import os

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

#Initalisierung des Mediator-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
mediator_llm = chat_models.init_chat_model("gpt-4o", temperature=0, timeout=300)

#Initalisierung des Feedback-LLMs (Temperatur = 0, Timeout nach 300 Sekunden)
feedback_llm = chat_models.init_chat_model("gpt-4o", temperature=0, timeout=300)

def initialize_mediator():
    pass


object_instances = ObjectInstances(
    object_description="Beispielbeschreibung für Objekte",
    object_instances={"obj1": "Beschreibung für obj1"}
)

# Erstelle eine Instanz von InitialState
initial_state = InitialState(
    initial_state_description="Beschreibung des Anfangszustands",
    initial_state_predicates=[
        Predicate(
            name="at",
            parameters={"object": "obj1", "location": "Berlin"},
            description="Das Objekt befindet sich in Berlin"
        )
    ]
)

# Erstelle eine Instanz von GoalState
goal_state = GoalState(
    goal_state_description="Beschreibung des Zielzustands",
    goal_state_predicates={
        "and": [
            Predicate(
                name="at",
                parameters={"object": "obj1", "location": "München"},
                description="Das Objekt soll sich in München befinden"
            )
        ]
    }
)


#TODO: Initialisierungsfunktion erstellen
example_question = NL2PlanState(
    natural_language_task="Currently I've got five packages to ship, 3 in a storage in Ado and the rest in Betar's storage. Those from Ado should be sent 1 to Bal Street in Betar, 2 to Cli Promenade in Colin. Those from Betar should be moved to the Ado storage. The only plane is currently in Duran's airport, but each city has it's own truck and airport.",
    domain_desc="The AI agent here is a logistics planner that has to plan to transport packages within the locations in a city through a truck and between cities through an airplane. Within a city, the locations are directly linked, allowing trucks to travel between any two of these locations. Similarly, cities are directly connected to each other allowing airplanes to travel between any two cities. Also, there is no limit to how many packages a truck or plane can carry (so in theory a truck or plane can carry an infinite number of packages).",
    types=[],                               # Leere Liste für types
    type_hierarchy=[],                      # Leere Liste für type_hierarchy
    nominated_actions=[],                   # Leere Liste für nominated_actions
    predicates=[],                          # Leere Liste für predicates
    actions=[],                             # Leere Liste für actions
    object_instances=object_instances,      # None für object_instances
    initial_state=initial_state,            # None für initial_state
    goal_state=goal_state,                  # None für goal_state
    feedback_type="llm_feedback",           # Standard-Feedback-Typ
    feedback=None                           # Leeres Dictionary für feedback
)

# =============================================================================
# Type-Extraction Schritt
# =============================================================================
#TODO: Few_shot_prompt - Beispiele für structured_output erzeugen (siehe :https://python.langchain.com/docs/how_to/structured_output/)

#Type Extraction - Node
def regular_type_extraction(state: NL2PlanState):  #TODO: domain_and_task ist variabel und wird bei Start angegeben
    """Führt Type_Extraction-Generierung aus."""
    with open(os.path.join(prompt_dir, "main.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = mediator_llm.with_structured_output(Type_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}{task}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    type_extraction_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task})
    #Gibt Liste an types zurück
    return {"types": type_extraction_call.types}


def give_type_extraction_feedback(state: NL2PlanState):
    """Führt Feedback für Type_Extraction aus."""
    with open(os.path.join(prompt_dir, "feedback.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = feedback_llm.with_structured_output(Feedback)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}{task}{first_solution}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    feedback_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types
        }
    )
    #Gibt Feedback für Schritt "0" zurück
    return {"step": 0, "feedback": feedback_call.feedback}


def type_extraction_with_feedback(state:NL2PlanState):
    """Führt Type_Extraction-Generierung mit Feedback aus."""
    with open(os.path.join(prompt_dir, "main.txt")) as f:
        system_message = f.read().strip()
    type_extraction_llm = mediator_llm.with_structured_output(Type_List)
    input_prompt = ChatPromptTemplate([("system", "{system_message}"),("human", "{domain_desc}{task}{first_solution}{feedback}")])
    type_extraction_chain = input_prompt | type_extraction_llm
    type_extraction_call = type_extraction_chain.invoke(
        {"system_message": system_message,
         "domain_desc": state.domain_desc,
         "task": state.natural_language_task,
         "first_solution": state.types,
         "feedback": state.feedback.get(0)})
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

def do_hierarchy_construction():
    pass

def give_hierarchy_construction_feedback():
    pass

# =============================================================================
# Action-Extraction Schritt
# =============================================================================

def do_action_extraction():
    pass


def give_action_extraction_feedback():
    pass

# =============================================================================
# Action-Construction Schritt
# =============================================================================

def do_action_construction():
    pass

def validate_actions():
    pass

def give_action_construction_feedback():
    pass

# =============================================================================
# Task - Extraction Schritt
# =============================================================================

def do_task_extraction():
    pass

def validate_task():
    pass

def give_task_extraction_feedback():
    pass



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