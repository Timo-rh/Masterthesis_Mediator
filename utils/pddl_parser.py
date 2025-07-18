from pddl.core import Action
from pddl.core import Problem, Domain
from pddl.logic import Predicate, variables
from pddl.logic.base import And, Not, Or
from pddl.logic.terms import Constant
from pddl.requirements import Requirements
from src.agent.states import *


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
        actions=create_actions(state)
    )
    # Domäne zurückgeben
    return domain

# =============================================================================
# Erzeugung des PDDL-Problems
# =============================================================================

# Erstellen der Objekte (Constants) aus den ObjectInstances
def create_objects(state: NL2PlanState) -> dict[str, Constant]:
    """
    Erstellt eine Map von Objektnamen zu PDDL-Constant-Objekten.
    """
    object_map = {}

    # Iteriere über alle Objekte in object_instances
    for name, type_ in state.object_instances.objects.items():
        name_lower = name.lower()
        object_map[name_lower] = Constant(name_lower, type_tag=type_)

    return object_map


# Erstellen des Initialzustands (InitialState)
# def create_initial_state(state: NL2PlanState, object_map: dict[str, Constant]) -> list[Predicate]:
#     """
#     Erstellt eine Liste von Prädikaten für den Initialzustand basierend auf dem initial_state.
#     """
#     initial_predicates = []
#     # Zugriff auf das InitialState-Objekt
#     for pred_inst in state.initial_state.initial_state_predicates:
#         name = pred_inst.name
#         parameters = pred_inst.parameters
#
#         constants = []
#         for p in parameters:
#             key = p.lower()
#             if key not in object_map:
#                 raise ValueError(
#                     f"Constant '{p}' (als '{key}') nicht in object_instances gefunden.")
#             constants.append(object_map[key])
#
#         pred = Predicate(name, *constants)
#         initial_predicates.append(pred)
#     return initial_predicates


# Erstellen des Zielzustands (GoalState)
# def create_goal_state(state: NL2PlanState, object_map: dict[str, Constant]) -> And:
#     """
#     Erstellt eine And-Bedingung für den Zielzustand basierend auf dem goal_state.
#     """
#     predicates = []
#     # Zugriff auf das GoalState-Objekt
#     if "and" in state.goal_state.goal_state_predicates:
#         goal_predicates = state.goal_state.goal_state_predicates["and"]
#     else:
#         raise ValueError("Goal state muss einen 'and'-Schlüssel mit einer Liste von Prädikaten enthalten.")
#
#     for pred_inst in goal_predicates:
#         name = pred_inst.name
#         parameters = pred_inst.parameters
#
#         constants = []
#         for p in parameters:
#             key = p.lower()
#             if key not in object_map:
#                 raise ValueError(
#                     f"Objekt '{p}' (als '{key}') nicht in object_instances gefunden")
#             constants.append(object_map[key])
#
#         pred = Predicate(name, *constants)
#         predicates.append(pred)
#     return And(*predicates)


# def parse_condition(condition, object_map):
#     """
#     Parst verschiedene Arten von Bedingungen rekursiv.
#     """
#     if not condition:
#         return None
#
#     # Einfaches Prädikat
#     if hasattr(condition, "name") and hasattr(condition, "parameters"):
#         name = condition.name
#         parameters = []
#         for p in condition.parameters:
#             key = p.lower()
#             if key not in object_map:
#                 raise ValueError(f"Konstante '{p}' nicht in object_map gefunden")
#             parameters.append(object_map[key])
#         return Predicate(name, *parameters)
#
#     # Komplexe Bedingung
#     elif hasattr(condition, "type"):
#         if condition.type == "not":
#             inner = parse_condition(condition.conditions, object_map)
#             return Not(inner) if inner else None
#         elif condition.type == "and":
#             parts = []
#             for c in condition.conditions:
#                 part = parse_condition(c, object_map)
#                 if part:
#                     parts.append(part)
#             return And(*parts) if parts else None
#         elif condition.type == "or":
#             parts = []
#             for c in condition.conditions:
#                 part = parse_condition(c, object_map)
#                 if part:
#                     parts.append(part)
#             return Or(*parts) if parts else None
#
#     return None


def create_initial_state(state: NL2PlanState, object_map: dict[str, Constant]) -> list:
    """
    Erstellt Initialzustand - prüft auf Conditions und normale Prädikate.
    """
    predicates = []
    for pred in state.initial_state.initial_state_predicates:
        # Prüfe ob es eine Condition ist (hat 'type' Attribut)
        if hasattr(pred, 'type') and pred.type == "not":
            # Negatives Prädikat - hole das innere Prädikat aus 'conditions'
            inner = pred.conditions
            name = inner.name
            params = [object_map[p.lower()] for p in inner.parameters if p.lower() in object_map]
            predicates.append(Not(Predicate(name, *params)))
        else:
            # Normales Prädikat (Predicate_Instance)
            name = pred.name
            params = [object_map[p.lower()] for p in pred.parameters if p.lower() in object_map]
            predicates.append(Predicate(name, *params))
    return predicates


def create_goal_state(state: NL2PlanState, object_map: dict[str, Constant]) -> And:
    """
    Erstellt Zielzustand - direkte Liste ohne "and".
    """
    predicates = []
    for pred in state.goal_state.goal_state_predicates:
        if pred.get("type") == "not":
            # Negatives Prädikat
            inner = pred["conditions"]
            name = inner["name"]
            params = [object_map[p.lower()] for p in inner["parameters"] if p.lower() in object_map]
            predicates.append(Not(Predicate(name, *params)))
        else:
            # Positives Prädikat
            name = pred["name"]
            params = [object_map[p.lower()] for p in pred["parameters"] if p.lower() in object_map]
            predicates.append(Predicate(name, *params))
    return And(*predicates)

def create_problem(state: NL2PlanState):
    # 1. Erstelle alle Constant-Objekte (als dict)
    constants_map = create_objects(state)  # dict[name -> Constant]

    # 2. Erstelle initial state mit vorhandenen Constants
    initial_state = create_initial_state(state, constants_map)

    # 3. Erstelle goal state mit vorhandenen Constants
    goal_state = create_goal_state(state, constants_map)

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