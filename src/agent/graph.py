from langgraph.constants import START

from src.agent.states import NL2PlanState
from langgraph.graph import StateGraph, START, END
from src.agent.nodes_and_edges import *


graph = StateGraph(NL2PlanState) #TODO:Config hinzufügen

#Nodes #TODO: Nodes an die neue Struktur anpassen
#graph.add_node("Initialization", initialize_mediator)
graph.add_node("Type Extraction", regular_type_extraction)
graph.add_node("Type Extraction Feedback", give_type_extraction_feedback)
graph.add_node("Type Extraction with Feedback", type_extraction_with_feedback)
graph.add_node("Hierarchy Construction", regular_hierarchy_construction)
graph.add_node("Hierarchy Construction Feedback", give_hierarchy_construction_feedback)
graph.add_node("Hierarchy Construction with Feedback", hierarchy_construction_with_feedback)
graph.add_node("Hierarchy Validation", validate_hierarchy)
graph.add_node("Action Extraction", regular_action_extraction)
graph.add_node("Action Extraction Feedback", give_action_extraction_feedback)
graph.add_node("Action Extraction with Feedback", action_extraction_with_feedback)
graph.add_node("Action Construction", action_construction)
graph.add_node("Action Construction Feedback", give_action_construction_feedback)
graph.add_node("Action Construction with Feedback",action_construction_with_feedback)
graph.add_node("Task Extraction", regular_task_extraction)
graph.add_node("Task Extraction Feedback", give_task_extraction_feedback)
graph.add_node("Task Extraction with Feedback", task_extraction_with_feedback)
#graph.add_node("PDDL Creation", create_pddl)
#graph.add_node("Automatic Planner", generate_plan)


#Edges
# graph.add_edge(START, "Initialization")
# graph.add_edge("Initialization", "Type Extraction")
# graph.add_edge("Type Extraction", "Type Extraction Feedback")
# graph.add_conditional_edges("Type Extraction Feedback", route_to_hierarchy_construction,{"No Feedback": "Type Extraction", "Feedback Done": "Hierarchy Construction"})
# #graph.add_edge("Type Extraction Feedback", "Hierarchy Construction")
# graph.add_edge("Hierarchy Construction", "Hierarchy Construction Feedback")
# graph.add_edge("Hierarchy Construction Feedback", "Action Extraction")
# graph.add_edge("Action Extraction", "Action Extraction Feedback")
# graph.add_edge("Action Extraction Feedback", "Action Construction")
# graph.add_edge("Action Construction", "Action Construction Automatic Validation")
# graph.add_edge("Action Construction Automatic Validation", "Action Construction Feedback")
# graph.add_edge("Action Construction Feedback", "Task Extraction")
# graph.add_edge("Task Extraction", "Task Extraction Automatic Validation")
# graph.add_edge("Task Extraction Automatic Validation", "Task Extration Feedback")
# graph.add_edge("Task Extration Feedback", "PDDL Creation")
# graph.add_edge("PDDL Creation", END)

#Edges NEU
graph.add_edge(START, "Type Extraction")
#graph.add_edge("Initialization", "Type Extraction")
graph.add_edge("Type Extraction", "Type Extraction Feedback")
graph.add_edge("Type Extraction Feedback", "Type Extraction with Feedback")
graph.add_edge("Type Extraction with Feedback", "Hierarchy Construction")
graph.add_edge("Hierarchy Construction", "Hierarchy Construction Feedback")
graph.add_edge("Hierarchy Construction Feedback", "Hierarchy Construction with Feedback")
graph.add_edge("Hierarchy Construction with Feedback", "Hierarchy Validation")
graph.add_edge("Hierarchy Validation", "Action Extraction")
graph.add_edge("Action Extraction", "Action Extraction Feedback")
graph.add_edge("Action Extraction Feedback", "Action Extraction with Feedback")
graph.add_edge("Action Extraction with Feedback", "Action Construction")
graph.add_edge("Action Construction", "Action Construction Feedback")
graph.add_edge("Action Construction Feedback", "Action Construction with Feedback")
graph.add_edge("Action Construction with Feedback", "Task Extraction")
graph.add_edge("Task Extraction", "Task Extraction Feedback")
graph.add_edge("Task Extraction Feedback", "Task Extraction with Feedback")
graph.add_edge("Task Extraction with Feedback", END)



#Compile
graph.compile(name="Mediator")

# # Define the graph
# graph = (
#     StateGraph(NL2PlanState, config_schema=Config_Schema)
#     .add_node(call_model)
#     .add_edge("__start__", "call_model")
#     .compile(name="New Graph")
# )