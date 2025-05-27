from __future__ import annotations
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
# Relativen Import verwenden
from src.agent.states import NL2PlanState, Type, ObjectInstances, InitialState, GoalState, Predicate

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

#Output des Feedback-LLMs bleibt immer gleich
feedback_llm = ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=0) #TODO: Ein Feedback LLM für alle Steps?

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


#TODO: Initialisierungsfunktion erstellen (
example_question = NL2PlanState(
    natural_language_task="What is the type of the city of Berlin?",
    types=[],                          # Leere Liste für types
    type_hierarchy=[],                 # Leere Liste für type_hierarchy
    nominated_actions=[],              # Leere Liste für nominated_actions
    predicates=[],                     # Leere Liste für predicates
    actions=[],                        # Leere Liste für actions
    object_instances=object_instances,             # None für object_instances
    initial_state=initial_state,                # None für initial_state
    goal_state=goal_state,                   # None für goal_state
    feedback_type="llm_feedback",      # Standard-Feedback-Typ
    feedback={0: "blue"}                        # Leeres Dictionary für feedback
)

# =============================================================================
# Type-Extraction Schritt
# =============================================================================

# #Type_Extraction_LLMs mit strukturiertem Output
llm = ChatOpenAI(model="gpt-4.1-2025-04-14", temperature=0)
mediator_llm = llm.with_structured_output(Type)


#TODO: Few_shot_prompt - Beispiele für structured_output erzeugen (siehe :https://python.langchain.com/docs/how_to/structured_output/)

#Type Extraction - Node
def do_type_extraction(state: NL2PlanState):
    """Führt Type_Extraction-Generierung aus."""
    if not state.feedback.get(0):
        msg = mediator_llm.invoke(f"This is a test. Please answer my question: Can you hear me?")
    else:
        msg = mediator_llm.invoke(f"What color has the feedback? Hint: {state.feedback}")
    return {"type_name": msg.name, "type_description": msg.description}






test_call = do_type_extraction(state=example_question)
print(f"Ergebnis des Test_calls: {test_call}")
#Ergebnis des Test_calls: {'type_name': 'Color', 'type_description': 'The feedback color is blue.'}


        #falls noch kein Feedback existiert soll nur invoke ausgeführt werden. Sonst soll das Feedback in den Input übernommen werden.
    #conditional_edge prüft dann, ob feedback_durchgeführt wahr ist und leitet an den Node für Hierarchy_Construction weiter (TODO: feedback_state erweitern)


def give_type_extraction_feedback():
    pass

# Conditional_Edge
def route_to_hierarchy_construction(state: NL2PlanState):
    """Weiterleiten zum Hierarchy_Construction-Node oder mediator_llm-Node."""
    if state.feedback.get(0) == "blue":
        return "Hierarchy_Construction"
    else:
        return "mediator_llm"


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