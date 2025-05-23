"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations
from langchain_core.runnables import RunnableConfig
from typing import TypedDict, List, Optional, Dict, Any, Union
from langgraph.graph import StateGraph, START, END


class Configuration(TypedDict):
    """Configurable parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str



class NL2PlanState(TypedDict):
    # === INPUT ===
    natural_language_task: str

    # === ZWISCHENERGEBNISSE (Pipeline-Outputs) ===
    types: Optional[List[Dict[str, str]]]  # Step 1 output
    type_hierarchy: Optional[Dict[str, Any]]  # Step 2 output
    actions_nl: Optional[List[Dict[str, str]]]  # Step 3 output
    pddl_domain: Optional[str]  # Step 4 output
    pddl_problem: Optional[str]  # Step 5 output

    # === FINAL OUTPUT ===
    plan: Optional[List[str]]  # Success case   #TODO: Output sollte sich aus Domänenbeschreibung mit Aufgaben zusammensetzen (Node mit Konkatenierung des States am Ende?)
    error_message: Optional[str]  # Failure case

    # === PROCESS CONTROL ===
    current_step: str
    is_complete: bool

# =============================================================================
# PRIVATE STATES für Feedback-Schleifen (nur innerhalb Subgraphen)
# =============================================================================


class TypeExtractionState(TypedDict):
    # Input für diesen Schritt (komplette Task-Beschreibung)
    natural_language_task: str

    # Arbeits-State für Feedback-Schleife
    current_attempt: Optional[List[Dict[str, str]]]  # [{"name": "City", "description": "A city contains locations"}]
    feedback_received: Optional[str]
    feedback_round: int         #TODO: notwendig?
    max_feedback_rounds: int    #TODO: notwendig?

    # Output dieses Schritts - strukturierte Type-Liste
    final_types: Optional[List[Dict[str, str]]]
    is_step_complete: bool


class HierarchyConstructionState(TypedDict):
    # Input für diesen Schritt
    types: List[Dict[str, str]]

    # Arbeits-State für Feedback-Schleife
    current_attempt: Optional[Dict[str, Any]]
    feedback_received: Optional[str]    #TODO: notwendig?
    feedback_round: int                 #TODO: notwendig?
    max_feedback_rounds: int

    # Output dieses Schritts
    final_hierarchy: Optional[Dict[str, Any]]
    is_step_complete: bool


class ActionExtractionState(TypedDict):
    # Inputs für diesen Schritt
    natural_language_task: str
    types: List[Dict[str, str]]  # Von Schritt 1
    type_hierarchy: Dict[str, Any]  # Von Schritt 2

    # Arbeits-State für Feedback-Schleife
    current_attempt: Optional[List[Dict[str, Any]]]  # Strukturierte Action-Liste
    feedback_received: Optional[str]        #TODO: notwendig?
    feedback_round: int                     #TODO: notwendig?
    max_feedback_rounds: int

    # Output dieses Schritts - Natural Language Actions mit Kategorien
    final_actions_nl: Optional[List[Dict[str, Any]]]
    is_step_complete: bool


class ActionConstructionState(TypedDict):
    # Inputs für diesen Schritt
    actions_nl: List[Dict[str, str]]
    types: List[Dict[str, str]]
    type_hierarchy: Dict[str, Any]

    # Arbeits-State für Feedback-Schleife + Validation
    current_attempt: Optional[str]  # PDDL domain string
    validation_errors: Optional[List[str]]
    feedback_received: Optional[str]
    feedback_round: int
    max_feedback_rounds: int
    max_validation_rounds: int
    validation_round: int

    # Output dieses Schritts
    final_pddl_domain: Optional[str]
    is_step_complete: bool


class TaskExtractionState(TypedDict):
    # Inputs für diesen Schritt
    natural_language_task: str
    pddl_domain: str

    # Arbeits-State für Feedback-Schleife + Validation
    current_attempt: Optional[str]  # PDDL problem string
    validation_errors: Optional[List[str]]
    feedback_received: Optional[str]
    feedback_round: int
    max_feedback_rounds: int
    max_validation_rounds: int
    validation_round: int

    # Output dieses Schritts
    final_pddl_problem: Optional[str]
    is_step_complete: bool





async def call_model(state: NL2PlanState, config: RunnableConfig) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime configuration to alter behavior.
    """
    configuration = config["configurable"]
    return {
        "changeme": "output from call_model. "
        f'Configured with {configuration.get("my_configurable_param")}'
    }


# Define the graph
graph = (
    StateGraph(NL2PlanState, config_schema=Configuration)
    .add_node(call_model)
    .add_edge("__start__", "call_model")
    .compile(name="New Graph")
)

