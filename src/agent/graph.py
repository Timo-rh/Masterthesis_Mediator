from langgraph.constants import START
from src.agent.states import NL2PlanState
from langgraph.graph import StateGraph, START, END
from src.agent.nodes_and_edges import *


graph = StateGraph(NL2PlanState)

#Nodes
graph.add_node("Type Extraction", regular_type_extraction)
graph.add_node("Type Extraction Feedback", give_type_extraction_feedback)
graph.add_node("Type Extraction with Feedback", type_extraction_with_feedback)
graph.add_node("Hierarchy Construction", regular_hierarchy_construction)
graph.add_node("Hierarchy Construction Feedback", give_hierarchy_construction_feedback)
graph.add_node("Hierarchy Construction with Feedback", hierarchy_construction_with_feedback)
graph.add_node("Action Extraction", regular_action_extraction)
graph.add_node("Action Extraction Feedback", give_action_extraction_feedback)
graph.add_node("Action Extraction with Feedback", action_extraction_with_feedback)
graph.add_node("Action Construction", action_construction)
graph.add_node("Action Construction Feedback", give_action_construction_feedback)
graph.add_node("Action Construction with Feedback",action_construction_with_feedback)
graph.add_node("Task Extraction - Objects", regular_objects_extraction)
graph.add_node("Task Extraction - Initial State", regular_initial_state_extraction)
graph.add_node("Task Extraction - Goal State", regular_goal_state_extraction)
graph.add_node("Task Extraction Feedback", give_task_extraction_feedback)
graph.add_node("Task Extraction - Objects with Feedback", objects_extraction_with_feedback)
graph.add_node("Task Extraction - Initial State with Feedback", initial_state_extraction_with_feedback)
graph.add_node("Task Extraction - Goal State with Feedback", goal_state_extraction_with_feedback)
graph.add_node("Save Complete State", save_complete_state)
graph.add_node("PDDL Creation - Domain", domain_to_state)
graph.add_node("PDDL Creation - Problem", problem_to_state)
graph.add_node("Save PDDL Files", save_pddl_files)

#Edges
graph.add_edge(START, "Type Extraction")
graph.add_edge("Type Extraction", "Type Extraction Feedback")
graph.add_edge("Type Extraction Feedback", "Type Extraction with Feedback")
graph.add_edge("Type Extraction with Feedback", "Hierarchy Construction")
graph.add_edge("Hierarchy Construction", "Hierarchy Construction Feedback")
graph.add_edge("Hierarchy Construction Feedback", "Hierarchy Construction with Feedback")
graph.add_edge("Hierarchy Construction with Feedback", "Action Extraction")
graph.add_edge("Action Extraction", "Action Extraction Feedback")
graph.add_edge("Action Extraction Feedback", "Action Extraction with Feedback")
graph.add_edge("Action Extraction with Feedback", "Action Construction")
graph.add_edge("Action Construction", "Action Construction Feedback")
graph.add_edge("Action Construction Feedback", "Action Construction with Feedback")
graph.add_edge("Action Construction with Feedback", "Task Extraction - Objects")
graph.add_edge("Task Extraction - Objects", "Task Extraction - Initial State")
graph.add_edge("Task Extraction - Initial State", "Task Extraction - Goal State")
graph.add_edge("Task Extraction - Goal State", "Task Extraction Feedback")
graph.add_edge("Task Extraction Feedback", "Task Extraction - Objects with Feedback")
graph.add_edge("Task Extraction - Objects with Feedback", "Task Extraction - Initial State with Feedback")
graph.add_edge("Task Extraction - Initial State with Feedback", "Task Extraction - Goal State with Feedback")
graph.add_edge("Task Extraction - Goal State with Feedback", "Save Complete State")
graph.add_edge("Save Complete State", "PDDL Creation - Domain")
graph.add_edge("PDDL Creation - Domain", "PDDL Creation - Problem")
graph.add_edge("PDDL Creation - Problem", "Save PDDL Files")
graph.add_edge("Save PDDL Files", END)
#Compile
graph.compile(name="Mediator mit einfachem Feedback")


nfgraph = StateGraph(NL2PlanState)
#Nodes
nfgraph.add_node("Type Extraction", regular_type_extraction)
nfgraph.add_node("Hierarchy Construction", regular_hierarchy_construction)
nfgraph.add_node("Action Extraction", regular_action_extraction)
nfgraph.add_node("Action Construction", action_construction)
nfgraph.add_node("Task Extraction - Objects", regular_objects_extraction)
nfgraph.add_node("Task Extraction - Initial State", regular_initial_state_extraction)
nfgraph.add_node("Task Extraction - Goal State", regular_goal_state_extraction)
nfgraph.add_node("Save Complete State", save_complete_state)
nfgraph.add_node("PDDL Creation - Domain", domain_to_state)
nfgraph.add_node("PDDL Creation - Problem", problem_to_state)
nfgraph.add_node("Save PDDL Files", save_pddl_files)

#Edges
nfgraph.add_edge(START, "Type Extraction")
nfgraph.add_edge("Type Extraction", "Hierarchy Construction")
nfgraph.add_edge("Hierarchy Construction", "Action Extraction")
nfgraph.add_edge("Action Extraction", "Action Construction")
nfgraph.add_edge("Action Construction", "Task Extraction - Objects")
nfgraph.add_edge("Task Extraction - Objects", "Task Extraction - Initial State")
nfgraph.add_edge("Task Extraction - Initial State", "Task Extraction - Goal State")
nfgraph.add_edge("Task Extraction - Goal State", "Save Complete State")
nfgraph.add_edge("Save Complete State", "PDDL Creation - Domain")
nfgraph.add_edge("PDDL Creation - Domain", "PDDL Creation - Problem")
nfgraph.add_edge("PDDL Creation - Problem", "Save PDDL Files")
nfgraph.add_edge("Save PDDL Files", END)

#Compile
nfgraph.compile(name="Mediator ohne Feedback")

