from src.agent.states import *
from pddl.core import Domain, Action
from pddl.logic.base import And, Not, Or
from pddl.logic import Predicate, variables
from pddl.logic.terms import Constant
import re
from datetime import datetime

import os
from utils.paths import *
from langchain import chat_models
from langchain_core.prompts import ChatPromptTemplate
from pddl.core import Problem, Domain
from pddl.requirements import Requirements



result1 = NL2PlanState(
    natural_language_task="Currently I've got five packages to ship, 3 in a storage in Ado and the rest in Betar's storage. Those from Ado should be sent 1 to Bal Street in Betar, 2 to Cli Promenade in Colin. Those from Betar should be moved to the Ado storage. The only plane is currently in Duran's airport, but each city has it's own truck and airport.",

    domain_desc="The AI agent here is a logistics planner that has to plan to transport packages within the locations in a city through a truck and between cities through an airplane. Within a city, the locations are directly linked, allowing trucks to travel between any two of these locations. Similarly, cities are directly connected to each other allowing airplanes to travel between any two cities. Also, there is no limit to how many packages a truck or plane can carry (so in theory a truck or plane can carry an infinite number of packages).",

    domain_name="logistics",

    task_name="task1",

    types=[
        Type_(name="city",
              description="A city contains locations and has its own truck and airport. Cities are directly connected to each other."),
        Type_(name="location",
              description="A place within a city that can contain packages. Locations in a city are directly connected."),
        Type_(name="storage", description="A type of location used to store packages."),
        Type_(name="street", description="A type of location where packages can be delivered."),
        Type_(name="promenade", description="A type of location where packages can be delivered."),
        Type_(name="airport", description="A type of location where airplanes can land and take off."),
        Type_(name="vehicle", description="A means of transport that can carry packages between locations."),
        Type_(name="truck", description="A type of vehicle that transports packages between locations within a city."),
        Type_(name="airplane", description="A type of vehicle that transports packages between cities."),
        Type_(name="package", description="An item that needs to be transported from one location to another.")
    ],

    type_hierarchy=[
        Hierarchy_Object(
            parent_type=Type_(name="object", description="Object is always root, everything is an object"),
            child_types=[
                Type_(name="city", description="A city contains locations and has its own truck and airport..."),
                Type_(name="location", description="A place within a city that can contain packages..."),
                Type_(name="vehicle", description="A means of transport that can carry packages..."),
                Type_(name="package", description="An item that needs to be transported...")
            ]
        ),
        Hierarchy_Object(
            parent_type=Type_(name="vehicle", description="A means of transport..."),
            child_types=[
                Type_(name="truck", description="..."),
                Type_(name="airplane", description="...")
            ]
        ),
        Hierarchy_Object(
            parent_type=Type_(name="location", description="A place within a city..."),
            child_types=[
                Type_(name="storage", description="..."),
                Type_(name="street", description="..."),
                Type_(name="promenade", description="..."),
                Type_(name="airport", description="...")
            ]
        )
    ],

    nominated_actions=[
        Nominated_Action(
            related_type="truck",
            name="load_truck",
            description="A package is loaded onto a truck at a location. Requires that the package and the truck to be at the same location.",
            usage_example="Load package_1 onto truck_1 at storage_1"
        ),
        Nominated_Action(
            related_type="truck",
            name="unload_truck",
            description="A package is unloaded from a truck at a location. Requires that the truck with the package be at the destination location.",
            usage_example="Unload package_1 from truck_1 at street_1"
        ),
        Nominated_Action(
            related_type="airplane",
            name="load_airplane",
            description="A package is loaded onto an airplane at an airport. Requires that the package and the airplane to be at the same airport.",
            usage_example="Load package_2 onto airplane_1 at airport_1"
        ),
        Nominated_Action(
            related_type="airplane",
            name="unload_airplane",
            description="A package is unloaded from an airplane at an airport. Requires that the airplane with the package be at the destination airport.",
            usage_example="Unload package_2 from airplane_1 at airport_2"
        ),
        Nominated_Action(
            related_type="truck",
            name="drive_truck",
            description="A truck drives from one location to another within the same city. Locations within a city are directly connected.",
            usage_example="Drive truck_1 from storage_1 to airport_1"
        ),
        Nominated_Action(
            related_type="airplane",
            name="fly_airplane",
            description="An airplane flies from one city's airport to another city's airport. Cities are directly connected.",
            usage_example="Fly airplane_1 from airport_1 to airport_2"
        )
    ],

    predicates=[
        Predicate_Defintion(
            name="at",
            predicate_parameters={"p": "object", "l": "location"},
            description="Package p is at location l"
        ),
        Predicate_Defintion(
            name="in",
            predicate_parameters={"p": "package", "t": "vehicle"},
            description="Package p is in vehicle t"
        ),
        Predicate_Defintion(
            name="in_city",
            predicate_parameters={"l": "location", "c": "city"},
            description="Location l is in city c"
        ),
        Predicate_Defintion(
            name="is_airport",
            predicate_parameters={"l": "location"},
            description="Location l is an airport"
        ),
        Predicate_Defintion(
            name="different",
            predicate_parameters={"c1": "city", "c2": "city"},
            description="Cities c1 and c2 are different"
        )
    ],

actions = [
    Action_(
        name="load_truck",
        description="A package is loaded onto a truck at a location. Requires that the package and the truck to be at the same location.",
        action_parameters={"p": "package", "t": "truck", "l": "location"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["p", "l"]),
                Predicate_Instance(name="at", parameters=["t", "l"]),
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="in", parameters=["p", "t"])
                )
            ]
        },
        effects={
            "and": [
                Predicate_Instance(name="in", parameters=["p", "t"]),
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="at", parameters=["p", "l"])
                )
            ]
        }
    ),
    Action_(
        name="unload_truck",
        description="A package is unloaded from a truck at a location. Requires that the truck with the package be at the destination location.",
        action_parameters={"p": "package", "t": "truck", "l": "location"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["t", "l"]),
                Predicate_Instance(name="in", parameters=["p", "t"])
            ]
        },
        effects={
            "and": [
                Predicate_Instance(name="at", parameters=["p", "l"]),
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="in", parameters=["p", "t"])
                )
            ]
        }
    ),
    Action_(
        name="load_airplane",
        description="A package is loaded onto an airplane at an airport. Requires that the package and the airplane to be at the same airport.",
        action_parameters={"p": "package", "a": "airplane", "ap": "airport"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["p", "ap"]),
                Predicate_Instance(name="at", parameters=["a", "ap"]),
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="in", parameters=["p", "a"])
                )
            ]
        },
        effects={
            "and": [
                Predicate_Instance(name="in", parameters=["p", "a"]),
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="at", parameters=["p", "ap"])
                )
            ]
        }
    ),
    Action_(
        name="unload_airplane",
        description="A package is unloaded from an airplane at an airport. Requires that the airplane with the package be at the destination airport.",
        action_parameters={"p": "package", "a": "airplane", "ap": "airport"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["a", "ap"]),
                Predicate_Instance(name="in", parameters=["p", "a"])
            ]
        },
        effects={
            "and": [
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="in", parameters=["p", "a"])
                ),
                Predicate_Instance(name="at", parameters=["p", "ap"])
            ]
        }
    ),
    Action_(
        name="drive_truck",
        description="A truck drives from one location to another within the same city. Locations within a city are directly connected.",
        action_parameters={"t": "truck", "from": "location", "to": "location", "c": "city"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["t", "from"]),
                Predicate_Instance(name="in_city", parameters=["from", "c"]),
                Predicate_Instance(name="in_city", parameters=["to", "c"])
            ]
        },
        effects={
            "and": [
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="at", parameters=["t", "from"])
                ),
                Predicate_Instance(name="at", parameters=["t", "to"])
            ]
        }
    ),
    Action_(
        name="fly_airplane",
        description="An airplane flies from one city's airport to another city's airport. Cities are directly connected.",
        action_parameters={
            "a": "airplane",
            "from": "airport",
            "to": "airport",
            "from_city": "city",
            "to_city": "city"
        },
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["a", "from"]),
                Predicate_Instance(name="in_city", parameters=["from", "from_city"]),
                Predicate_Instance(name="in_city", parameters=["to", "to_city"]),
                Predicate_Instance(name="is_airport", parameters=["from"]),
                Predicate_Instance(name="is_airport", parameters=["to"]),
                Predicate_Instance(name="different", parameters=["from_city", "to_city"])
            ]
        },
        effects={
            "and": [
                Condition(
                    type="not",
                    conditions=Predicate_Instance(name="at", parameters=["a", "from"])
                ),
                Predicate_Instance(name="at", parameters=["a", "to"])
            ]
        }
    )
],
    object_instances=ObjectInstances(
        objects={
            "ado_city": "city",
            "betar_city": "city",
            "colin_city": "city",
            "duran_city": "city",
            "ado_storage": "storage",
            "ado_airport": "airport",
            "ado_truck": "truck",
            "betar_storage": "storage",
            "betar_airport": "airport",
            "betar_street": "location",
            "betar_truck": "truck",
            "colin_promenade": "promenade",
            "colin_airport": "airport",
            "colin_storage": "storage",
            "colin_truck": "truck",
            "duran_airport": "airport",
            "duran_truck": "truck",
            "duran_storage": "storage",
            "airplane1": "airplane",
            "package1": "package",
            "package2": "package",
            "package3": "package",
            "package4": "package",
            "package5": "package"
        }
    ),

    initial_state=InitialState(
        initial_state_predicates=[
            Predicate_Instance(name="at", parameters=["package1","ado_storage"]),
            Predicate_Instance(name="at", parameters=["package2", "ado_storage"]),
            Predicate_Instance(name="at", parameters=["package3", "ado_storage"]),
            Predicate_Instance(name="at", parameters=["package4", "betar_storage"]),
            Predicate_Instance(name="at", parameters=["package5", "betar_storage"]),
            Predicate_Instance(name="at", parameters=["ado_truck", "ado_storage"]),
            Predicate_Instance(name="at", parameters=["betar_truck", "betar_storage"]),
            Predicate_Instance(name="at", parameters=["colin_truck", "colin_storage"]),
            Predicate_Instance(name="at", parameters=["duran_truck", "duran_storage"]),
            Predicate_Instance(name="at", parameters=["airplane1", "duran_airport"]),
            Predicate_Instance(name="in_city", parameters=["ado_storage", "ado_city"]),
            Predicate_Instance(name="in_city", parameters=["ado_airport", "ado_city"]),
            Predicate_Instance(name="in_city", parameters=["betar_storage", "betar_city"]),
            Predicate_Instance(name="in_city", parameters=["betar_street", "betar_city"]),
            Predicate_Instance(name="in_city", parameters=["betar_airport", "betar_city"]),
            Predicate_Instance(name="in_city", parameters=["colin_storage", "colin_city"]),
            Predicate_Instance(name="in_city", parameters=["colin_promenade", "colin_city"]),
            Predicate_Instance(name="in_city", parameters=["colin_airport", "colin_city"]),
            Predicate_Instance(name="in_city", parameters=["duran_storage", "duran_city"]),
            Predicate_Instance(name="in_city", parameters=["duran_airport", "duran_city"])
        ]
    ),

    goal_state=GoalState(
        goal_state_predicates={
            "and": [
                Predicate_Instance(name="at", parameters=["package1","betar_street"]),
                Predicate_Instance(name="at", parameters=["package2","colin_promenade"]),
                Predicate_Instance(name="at", parameters=["package3","colin_promenade"]),
                Predicate_Instance(name="at", parameters=["package4","ado_storage"]),
                Predicate_Instance(name="at", parameters=["package5","ado_storage"])
            ]
        }
    ),

    feedback=[],

    pddl_domain="""(define (domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        city location package vehicle - object
        airport promenade storage street - location
        airplane truck - vehicle
    )
    (:predicates (at ?p ?l - location)  (different ?c1 - city ?c2 - city)  (in ?p ?t - vehicle)  (in_city ?l - location ?c - city)  (is_airport ?l - location))
    (:action drive_truck
        :parameters (?t - truck ?from - location ?to - location ?c - city)
        :precondition (and (at ?t ?from) (in_city ?from ?c) (in_city ?to ?c))
        :effect (and (not (at ?t ?from)) (at ?t ?to))
    )
     (:action fly_airplane
        :parameters (?a - airplane ?from - airport ?to - airport ?from_city - city ?to_city - city)
        :precondition (and (at ?a ?from) (in_city ?from ?from_city) (in_city ?to ?to_city) (is_airport ?from) (is_airport ?to) (different ?from_city ?to_city))
        :effect (and (not (at ?a ?from)) (at ?a ?to))
    )
     (:action load_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?p ?ap) (at ?a ?ap) (not (in ?p ?a)))
        :effect (and (in ?p ?a) (not (at ?p ?ap)))
    )
     (:action load_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?p ?l) (at ?t ?l) (not (in ?p ?t)))
        :effect (and (in ?p ?t) (not (at ?p ?l)))
    )
     (:action unload_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?a ?ap) (in ?p ?a))
        :effect (and (not (in ?p ?a)) (at ?p ?ap))
    )
     (:action unload_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?t ?l) (in ?p ?t))
        :effect (and (at ?p ?l) (not (in ?p ?t)))
    )
    )"""
)
# =============================================================================
# Erzeugung der PDDL-Domain
# =============================================================================

# Types erzeugen
def create_types(state: NL2PlanState):
    # Typ-Hierarchie in ein Mapping wandeln: {child: parent}
    types_map = {}

    for hierarchy in state.type_hierarchy:
        parent_name = hierarchy.parent_type.name
        for child in hierarchy.child_types:
            child_name = child.name
            types_map[child_name] = parent_name

        # Eltern auch sicherstellen, wenn nicht schon vorhanden
        if parent_name not in types_map:
            types_map[parent_name] = None  # root-type hat keinen parent

    return types_map

# Variablen für Prädikate und Aktionen erzeugen
predicate_variables = {}

def get_or_create_variable(name, type_):
    if name in predicate_variables:
        return predicate_variables[name]
    else:
        if type_ == "object":
            variable, = variables(name)
        else:
            variable, = variables(name, types=[type_])
        predicate_variables[name] = variable
        return variable

def build_predicate(predicate_instance: Predicate_Instance):
    """
    Wandelt eine Predicate_Instance in ein Predicate-Objekt um.
    """
    name = predicate_instance.name
    parameters = [get_or_create_variable(param, "object") for param in predicate_instance.parameters]
    return Predicate(name, *parameters)

def create_predicates(state: NL2PlanState):
    """
    Erstellt eine Liste von Prädikaten aus den Prädikatsdefinitionen im Zustand.
    """
    predicates = []
    for predicate in state.predicates:
        variables_list = []
        for var_name, var_type in predicate.predicate_parameters.items():
            variable = get_or_create_variable(var_name, var_type)
            variables_list.append(variable)
        predicates.append(Predicate(predicate.name, *variables_list))
    return predicates

# Aktionen erzeugen
def create_actions(state: NL2PlanState):
    actions = []

    for action in state.actions:
        action_variables = {}
        for param_name, param_type in action.action_parameters.items():
            variable, = variables(param_name, types=[param_type])
            action_variables[param_name] = variable

        # Überprüfe, ob alle Variablen in den Bedingungen definiert sind
        def validate_parameters(condition):
            if isinstance(condition, Predicate_Instance):
                for var in condition.parameters:
                    if var not in action_variables:
                        raise ValueError(
                            f"Variable '{var}' in condition '{condition.name}' ist nicht in den action_parameters definiert. "
                            f"Definierte Parameter: {list(action_variables.keys())}")
            elif isinstance(condition, Condition):
                if condition.type == "not" and condition.conditions:
                    validate_parameters(condition.conditions)
                elif condition.type in {"and", "or"} and isinstance(condition.conditions, list):
                    for sub_condition in condition.conditions:
                        validate_parameters(sub_condition)
            else:
                raise ValueError(f"Unbekannter Bedingungstyp: {type(condition)}")

        def parse_condition(condition):
            if isinstance(condition, Condition):
                if condition.type is None:
                    return None
                if condition.type == "not":
                    inner = parse_condition(condition.conditions)
                    return Not(inner)
                elif condition.type == "or":
                    if not isinstance(condition.conditions, list) or len(condition.conditions) < 2:
                        raise ValueError("`or`-Bedingungen müssen mindestens zwei `Predicate_Instance` enthalten.")
                    parts = [parse_condition(c) for c in condition.conditions if c is not None]
                    return Or(*parts)
                else:
                    raise ValueError(f"Unbekannter Condition-Typ: {condition.type}")
            elif isinstance(condition, Predicate_Instance):
                return build_predicate(condition)
            else:
                raise ValueError(f"Unbekannter Bedingungstyp: {condition}")

        # Validierung der preconditions und effects
        for condition in action.preconditions["and"]:
            validate_parameters(condition)
        for condition in action.effects["and"]:
            if isinstance(condition, Condition) and condition.type == "not":
                validate_parameters(condition.conditions)
            elif isinstance(condition, Predicate_Instance):
                validate_parameters(condition)

        precondition = And(*[c for c in (parse_condition(c) for c in action.preconditions["and"]) if c is not None])
        effect = And(*[c for c in (parse_condition(c) for c in action.effects["and"]) if c is not None])

        pddl_action = Action(
            name=action.name,
            parameters=list(action_variables.values()),
            precondition=precondition,
            effect=effect
        )
        actions.append(pddl_action)

    return actions

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
    # Domäne zurückgeben
    return domain

# =============================================================================
# Erzeugung des PDDL-Problems
# =============================================================================

# Erstellen der Objekte (Constants) aus den ObjectInstances
def create_objects(state: NL2PlanState) -> dict[str, Constant]:
    object_map = {}

    # Debugging: Ausgabe des Formats von object_instances
    print(f"object_instances Inhalt: {state.object_instances}")
    print(f"object_instances Typ: {type(state.object_instances)}")

    # Überprüfung des Formats von object_instances
    if isinstance(state.object_instances, dict):
        objects = state.object_instances
    elif hasattr(state.object_instances, "objects"):
        objects = state.object_instances.objects
    elif hasattr(state.object_instances, "data"):  # Beispiel für ein alternatives Attribut
        objects = state.object_instances.data
    else:
        raise ValueError("`object_instances` hat ein unerwartetes Format.")

    # Erstellen der Objekte
    for name, type_ in objects.items():
        object_map[name] = Constant(name, type_tag=type_)
    return object_map

# Erstellen des Initialzustands (InitialState)
def create_initial_state(state: NL2PlanState, object_map: dict[str, Constant]) -> list[Predicate]:
    initial_predicates = []

    # Arity-Map zur Validierung
    arity_map = {pred_def.name: len(pred_def.predicate_parameters) for pred_def in state.predicates}

    for pred_inst in state.initial_state.initial_state_predicates:
        name = pred_inst.name
        parameters = pred_inst.parameters

        if name not in arity_map:
            raise ValueError(f"Predicate '{name}' not defined in domain.")
        if len(parameters) != arity_map[name]:
            raise ValueError(f"Predicate '{name}' expects {arity_map[name]} arguments, got {len(parameters)}")

        # Parameters auf Constants mappen
        constants = []
        for p in parameters:
            key = p.lower()
            if key not in object_map:
                raise ValueError(f"Constant '{p}' not found in objects.")
            constants.append(object_map[key])

        pred = Predicate(name, *constants)
        initial_predicates.append(pred)

    return initial_predicates


# Erstellen des Zielzustands (GoalState)
def create_goal_state(goal_state: GoalState, object_map: dict[str, Constant]) -> And:
    predicates = []
    for pred_inst in goal_state.goal_state_predicates.get("and", []):
        name = pred_inst.name
        parameters = pred_inst.parameters

        constants = []
        for p in parameters:
            key = p.lower()
            if key not in object_map:
                raise ValueError(f"Constant '{p}' not found in objects.")
            constants.append(object_map[key])

        pred = Predicate(name, *constants)
        predicates.append(pred)

    return And(*predicates)


def create_problem(state: NL2PlanState):
    # 1. Erstelle alle Constant-Objekte (als dict)
    constants_map = create_objects(state)  # dict[name -> Constant]

    # 2. Erstelle initial state mit vorhandenen Constants
    initial_state = create_initial_state(state, constants_map)

    # 3. Erstelle goal state mit vorhandenen Constants
    goal_state = create_goal_state(state.goal_state, constants_map)

    # 4. Erstelle PDDL-Problem
    problem = Problem(
        name=state.task_name,
        requirements=requirements,
        domain=create_domain(state),
        objects=list(constants_map.values()),  # Liste aller Constant-Objekte
        init=initial_state,
        goal=goal_state
    )
    return problem


if __name__ == "__main__":
    try:
        print("Erstelle Domain...")
        domain = create_domain(result1)
        print("Domain erfolgreich erstellt:")
        print(domain)

        print("\nErstelle Problem...")
        problem = create_problem(result1)
        print("Problem erfolgreich erstellt:")
        print(problem)
    except Exception as e:
        print("Fehler während der Verarbeitung:")
        print(e)