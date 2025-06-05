from __future__ import annotations
import operator
from typing import List, Optional, Dict, Literal, Annotated
from pydantic import BaseModel, Field


# =============================================================================
# Haupt-State für den gesamten Graphen
# =============================================================================

class NL2PlanState(BaseModel):
    # === INPUT ===
    natural_language_task: str  #TODO: Prüfen ob die Aufteilung in domain_desc, task, etc. mehr Sinn ergibt
    domain_desc: str
    feedback_type: Optional[Literal["llm_feedback", "human_feedback"]] = Field(default=None, description="The type of feedback received.")  # TODO: Wäre das nicht eher für die config relevant?

    # === ZWISCHENERGEBNISSE (Pipeline-Outputs) ===
    types: Optional[List[Type]] = None                          # Step 1
    type_hierarchy: Optional[List[Hierarchy_Object]] = None     # Step 2
    nominated_actions: Optional[List[Nominated_Action]] = None  # Step 3
    predicates: Optional[List[Predicate]] = None                # Step 4
    actions: Optional[List[Action]] = None                      # Step 4
    object_instances: Optional[ObjectInstances] = None          # Step 5
    initial_state: Optional[InitialState] = None                # Step 5
    goal_state: Optional[GoalState] = None                      # Step 5
    feedback: Annotated[list, operator.add]                     # Entspricht dem Feedback-Schema


# =============================================================================
# Schemata für Strukturierung der Outputs (Types, Hierarchie etc.)
# =============================================================================

class Type(BaseModel):
    name: str = Field(description="The name of the type, e.g., 'city', 'truck', etc.")
    description: str = Field(description="A description of the type, e.g., 'A city contains locations'.")

#Diese Klasse ist nur für die Ausstattung des LLMs mit einem strukturierten Output
class Type_List(BaseModel):
    types: List[Type] = Field(description="List of all types.")

#Klasse für ein Hierarchie - Element
class Hierarchy_Object(BaseModel):
    parent_type: Type = Field(description="The name and description of the parent type.")
    child_types: Optional[List[Type]] = Field(description="The name and description of the child type.")

#Klasse für die Hierarchie, bspw: hierarchy = Hierarchy(
#     hierarchy=[
#         Hierarchy_Object(parent_type="object", child_type="package"),
#         Hierarchy_Object(parent_type="object", child_type="vehicle"),
#         Hierarchy_Object(parent_type="object", child_type="city"),
#         Hierarchy_Object(parent_type="vehicle", child_type="truck"),
#         Hierarchy_Object(parent_type="vehicle", child_type="plane")])
class Hierarchy(BaseModel):
    hierarchy: List[Hierarchy_Object] = Field(description="List of all hierarchy elements. Makes up the complete hierarchy.")

#Klasse für die Nennung einer Aktion (Action Extraction Step)
class Nominated_Action(BaseModel):
    related_type: str = Field(description="The name of the type that the action relates to.")
    name: str = Field(description="The name of the action, e.g., 'drive'.")
    description: str = Field(description="A description of the action. Includes what is required to take that action, e.g., 'A package is loaded onto a vehicle at a location. Requires that the package and the truck to be at the same location.'.")
    usage_example: str = Field(description="An example of how the action can be used, e.g., 'Drive to the city of Berlin'.")

#Diese Klasse ist nur für die Ausstattung des LLMs mit einem strukturierten Output
class Nominated_Action_List(BaseModel):
    actions: List[Nominated_Action] = Field(description="List of all actions.")

#Klasse für Prädikate
class Predicate(BaseModel):
    name: str = Field(description="The name of the predicate, e.g., 'at'.")
    predicate_parameters: Dict[str, str] #= Field(description="The parameters of the predicate, e.g., '{param_name (?o): param_type (object)}'")
    description: str #= Field(description="A description of the predicate, e.g., 'true if the object is at the location.'.")

#Klasse für Beschreibung einer Aktion (Action Construction Step) #TODO: "Key-Tuple" durch einzelnen Wert ersetzen (Erklärung des Operators (add etc.) fällt dann weg. -> In Doku aufnehmen
class Action(BaseModel):
    name: str = Field(description="The name of the action, e.g., 'drive'.")
    description: str = Field(description="A description of the action. Includes what is required to take that action, e.g., 'A package is loaded onto a vehicle at a location. Requires that the package and the truck to be at the same location.'.")
    action_parameters: Dict[str, str] #= Field(description="The parameters of the action, e.g., '{param_name: param_type}'")
    preconditions: Dict[str, List[Predicate]] #= Field(description="All preconditions for the action, e.g., {'and': [Predicate(name='at', parameters={'object': '?p', 'location': '?l'}, description='The package is at the location'), Predicate(name='at', parameters={'object': '?v', 'location': '?l'}, description='The vehicle is at the location')]}")
    effects: Dict[str, List[Predicate]] #= Field(description="All effects for the action, e.g., {'and': [Predicate(name='at', parameters={'object': '?p', 'location': '?l'}, description='The package is at the location'), Predicate(name='at', parameters={'object': '?v', 'location': '?l'}, description='The vehicle is at the location')]}")


#Klasse für alle Objektinstanzen
class ObjectInstances(BaseModel):
    objects: Dict[str, str] = Field(description="A dictionary of object instances with object name and description, e.g., {'L1': 'The first London package', 'L2': 'The second London package'.")

#Klasse für den Ausgangszustand
class InitialState(BaseModel):
    initial_state_predicates: List[Predicate] = Field(description="A list of predicates describing the initial state of the world, e.g., [{'at', {'L1': 'LStorage'}, The first London package location}, {'at', {'L2': 'LStorage'}, The second London package location}")

#Klasse für den Zielzustand
class GoalState(BaseModel):
    goal_state_predicates: Dict[str, List[Predicate]] = Field(description="{'and': [Predicate(name='at', parameters={'package': 'L1', 'location': 'Addr1'}, description='L1 is delivered'), Predicate(name='at', parameters={'package': 'L2', 'location': 'Addr2'}, description='L2 is delivered')]}")

##Diese Klasse ist nur für die Ausstattung des LLMs mit einem strukturierten Output (für die Taskgenerierung)
class Task_Description(BaseModel):
    object_instances: ObjectInstances = Field(description="Grounded objects for the task.")
    initial_state: InitialState = Field(description="Grounded Initial state of the world.")
    goal_state: GoalState = Field(description="Grounded Goal state of the world.")

#Klasse für das Feedback
class Feedback(BaseModel):
    feedback: str = Field(description="Description of the feedback received for the current step.")


#TODO: Klären, ob sich der Inputprompt dynamisch in den Schritten ändert. -> eher statisch, aber domain_desc, task und type_extraction/main sind alles einzelne Dateien
#TODO: Feedback und restliche States definieren
