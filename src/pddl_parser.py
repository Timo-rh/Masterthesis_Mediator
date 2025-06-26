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
from src.agent.nodes_and_edges import *


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
    ],  #TODO: Not included in JSON

actions = [
    Action_(
        name="load_truck",
        description="A package is loaded onto a truck at a location. Requires that the package and the truck to be at the same location.",
        action_parameters={"p": "package", "t": "truck", "l": "location"},
        preconditions={
            "and": [
                Predicate_Instance(name="at", parameters=["p", "l"]),
                Predicate_Instance(name="at", parameters=["t", "l"]),
                {"not": Predicate_Instance(name="in", parameters=["p", "t"])}
            ]
        },
        effects={
            "and": [
                Predicate_Instance(name="in", parameters=["p", "t"]),
                {"not": Predicate_Instance(name="at", parameters=["p", "l"])}
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
                {"not": Predicate_Instance(name="in", parameters=["p", "t"])}
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
                {"not": Predicate_Instance(name="in", parameters=["p", "a"])}
            ]
        },
        effects={
            "and": [
                Predicate_Instance(name="in", parameters=["p", "a"]),
                {"not": Predicate_Instance(name="at", parameters=["p", "ap"])}
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
                {"not": Predicate_Instance(name="in", parameters=["p", "a"])},
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
                {"not": Predicate_Instance(name="at", parameters=["t", "from"])},
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
                {"not": Predicate_Instance(name="at", parameters=["a", "from"])},
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
            "colin_truck": "truck",
            "duran_airport": "airport",
            "duran_truck": "truck",
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
            Predicate_Instance(name="at", parameters=["A1","AdoStorage"]),
            Predicate_Instance(name="at", parameters=["A2", "AdoStorage"]),
            Predicate_Instance(name="at", parameters=["A3", "AdoStorage"]),
            Predicate_Instance(name="at", parameters=["B1", "BetarStorage"]),
            Predicate_Instance(name="at", parameters=["B2", "BetarStorage"]),
            Predicate_Instance(name="at", parameters=["AdoTruck", "AdoStorage"]),
            Predicate_Instance(name="at", parameters=["BetarTruck", "BetarStorage"]),
            Predicate_Instance(name="at", parameters=["ColinTruck", "ColinStorage"]),
            Predicate_Instance(name="at", parameters=["DuranTruck", "DuranStorage"]),
            Predicate_Instance(name="at", parameters=["Plane1", "DuranAirport"]),
            Predicate_Instance(name="in-city", parameters=["AdoStorage", "Ado"]),
            Predicate_Instance(name="in-city", parameters=["AdoAirport", "Ado"]),
            Predicate_Instance(name="in-city", parameters=["BetarStorage", "Betar"]),
            Predicate_Instance(name="in-city", parameters=["BetarStreet", "Betar"]),
            Predicate_Instance(name="in-city", parameters=["BetarAirport", "Betar"]),
            Predicate_Instance(name="in-city", parameters=["ColinStorage", "Colin"]),
            Predicate_Instance(name="in-city", parameters=["ColinPromenade", "Colin"]),
            Predicate_Instance(name="in-city", parameters=["ColinAirport", "Colin"]),
            Predicate_Instance(name="in-city", parameters=["DuranStorage", "Duran"]),
            Predicate_Instance(name="in-city", parameters=["DuranAirport", "Duran"]),        ]
    ),

    goal_state=GoalState(
        goal_state_predicates={
            "and": [
                Predicate_Instance(name="at", parameters=["L1","bal_street"]),
                Predicate_Instance(name="at", parameters=["L2","cli_promenade"]),
                Predicate_Instance(name="at", parameters=["L3","cli_promenade"]),
                Predicate_Instance(name="at", parameters=["L4","ado_storage"]),
                Predicate_Instance(name="at", parameters=["L5","ado_storage"]),
            ]
        }
    ),

    feedback=[],

    pddl_domain=None
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

# Variablen für Predicates und Actions erzeugen
parameter_vars = {}

def get_or_create_variable(name, type_):
    if name in parameter_vars:
        return parameter_vars[name]
    else:
        if type_ == "object":
            v, = variables(name)
        else:
            v, = variables(name, types=[type_])
        parameter_vars[name] = v
        return v

# Predicates erzeugen
def create_predicates(state:NL2PlanState):
    predicates_list = []
    for pred in state.predicates:
        vars_ = []
        for var_name, var_type in pred.predicate_parameters.items():
            v = get_or_create_variable(var_name, var_type)
            vars_.append(v)
        p = Predicate(pred.name, *vars_)
        predicates_list.append(p)
    return predicates_list

# Actions erzeugen
def create_actions(state: NL2PlanState):
    actions = []

    for action in state.actions:
        action_vars = {}
        for param_name, param_type in action.action_parameters.items():
            v, = variables(param_name, types=[param_type])
            action_vars[param_name] = v

        def build_predicate(pred_: Predicate_Instance):
            args = []
            for var in pred_.parameters:
                if var not in action_vars:
                    raise ValueError(f"Variable '{var}' nicht in Action-Params gefunden")
                args.append(action_vars[var])
            return Predicate(pred_.name, *args)

        def parse_condition(cond):
            if isinstance(cond, dict):
                if "and" in cond:
                    parts = []
                    for c in cond["and"]:
                        res = parse_condition(c)
                        if isinstance(res, list):
                            parts.extend(res)
                        else:
                            parts.append(res)
                    return And(*parts)

                elif "or" in cond:
                    parts = []
                    for c in cond["or"]:
                        res = parse_condition(c)
                        if isinstance(res, list):
                            parts.extend(res)
                        else:
                            parts.append(res)
                    return Or(*parts)

                elif "not" in cond:
                    inner = parse_condition(cond["not"])
                    return Not(inner)

                else:
                    raise ValueError(f"Unbekanntes Dict-Format in Bedingung: {cond}")

            elif isinstance(cond, Predicate_Instance):
                return build_predicate(cond)

            else:
                raise ValueError(f"Unbekannter Bedingungstyp: {cond}")

        precondition = parse_condition(action.preconditions)
        effect = parse_condition(action.effects)

        pddl_action = Action(
            name=action.name,
            parameters=list(action_vars.values()),
            precondition=precondition,
            effect=effect
        )
        actions.append(pddl_action)

    return actions

# =============================================================================
# Erzeugung des PDDL-Problems
# =============================================================================

# Erstellen der Objekte (Constants) aus den ObjectInstances
def create_objects(state: NL2PlanState) -> list[Constant]:
    constants_list = []
    for name, type_ in state.object_instances.objects.items():
        const = Constant(name, type_tag=type_)
        constants_list.append(const)
    return constants_list


# Erstellen des Initialzustands (InitialState)
def create_initial_state(state: NL2PlanState):
    pass



















# Test
print(create_objects(result1))

requirements = [
        Requirements.STRIPS,
        Requirements.TYPING,
        Requirements.EQUALITY,
        Requirements.NEG_PRECONDITION,
        Requirements.DIS_PRECONDITION,
        Requirements.UNIVERSAL_PRECONDITION,
        Requirements.CONDITIONAL_EFFECTS,
    ]


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

domain = create_domain(result1)

def create_problem(state: NL2PlanState):
    problem = Problem(
        name=state.task_name,
        requirements=requirements,
        domain=domain,
        objects=create_objects(state),
        # init=create_initial_state(state),
        # goal=create_goal_state(state)
    )

print(create_problem(result1))