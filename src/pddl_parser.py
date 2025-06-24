from src.agent.states import *
from pddl.core import Domain, Problem, Types
from pddl.logic import Predicate
from pddl.action import Action
from pddl.requirements import Requirements

result1 = NL2PlanState(
    natural_language_task="Currently I've got five packages to ship, 3 in a storage in Ado and the rest in Betar's storage. Those from Ado should be sent 1 to Bal Street in Betar, 2 to Cli Promenade in Colin. Those from Betar should be moved to the Ado storage. The only plane is currently in Duran's airport, but each city has it's own truck and airport.",

    domain_desc="The AI agent here is a logistics planner that has to plan to transport packages within the locations in a city through a truck and between cities through an airplane. Within a city, the locations are directly linked, allowing trucks to travel between any two of these locations. Similarly, cities are directly connected to each other allowing airplanes to travel between any two cities. Also, there is no limit to how many packages a truck or plane can carry (so in theory a truck or plane can carry an infinite number of packages).",

    domain_name="logistics",

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

    predicates=None,  # Not included in JSON

    actions = [
        Action_(
            name="load_truck",
            description="A package is loaded onto a truck at a location. Requires that the package and the truck to be at the same location.",
            action_parameters={"?p": "package", "?t": "truck", "?l": "location"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?l"},
                               description="The package must be at the location"),
                    Predicate_(name="at", predicate_parameters={"?t": "?t", "?l": "?l"},
                               description="The truck must be at the location"),
                    {"not": Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?t"},
                                       description="The package must not already be in the truck")}
                ]
            },
            effects={
                "and": [
                    Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?t"},
                               description="The package is now in the truck"),
                    {"not": Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?l"},
                                       description="The package is no longer at the location")}
                ]
            }
        ),
        Action_(
            name="unload_truck",
            description="A package is unloaded from a truck at a location. Requires that the truck with the package be at the destination location.",
            action_parameters={"?p": "package", "?t": "truck", "?l": "location"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?t": "?t", "?l": "?l"},
                               description="The truck must be at the location"),
                    Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?t"},
                               description="The package must be in the truck")
                ]
            },
            effects={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?l"},
                               description="The package is now at the location"),
                    {"not": Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?t"},
                                       description="The package is no longer in the truck")}
                ]
            }
        ),
        Action_(
            name="load_airplane",
            description="A package is loaded onto an airplane at an airport. Requires that the package and the airplane to be at the same airport.",
            action_parameters={"?p": "package", "?a": "airplane", "?ap": "airport"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?ap"},
                               description="The package must be at the airport"),
                    Predicate_(name="at", predicate_parameters={"?t": "?a", "?l": "?ap"},
                               description="The airplane must be at the airport"),
                    {"not": Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?a"},
                                       description="The package must not already be in the airplane")}
                ]
            },
            effects={
                "and": [
                    Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?a"},
                               description="The package is now in the airplane"),
                    {"not": Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?ap"},
                                       description="The package is no longer at the airport")}
                ]
            }
        ),
        Action_(
            name="unload_airplane",
            description="A package is unloaded from an airplane at an airport. Requires that the airplane with the package be at the destination airport.",
            action_parameters={"?p": "package", "?a": "airplane", "?ap": "airport"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?t": "?a", "?l": "?ap"},
                               description="The airplane must be at the airport"),
                    Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?a"},
                               description="The package must be in the airplane")
                ]
            },
            effects={
                "and": [
                    {"not": Predicate_(name="in", predicate_parameters={"?p": "?p", "?t": "?a"},
                                       description="The package is no longer in the airplane")},
                    Predicate_(name="at", predicate_parameters={"?p": "?p", "?l": "?ap"},
                               description="The package is now at the airport")
                ]
            }
        ),
        Action_(
            name="drive_truck",
            description="A truck drives from one location to another within the same city. Locations within a city are directly connected.",
            action_parameters={"?t": "truck", "?from": "location", "?to": "location", "?c": "city"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?t": "?t", "?l": "?from"},
                               description="The truck must be at the starting location"),
                    Predicate_(name="in_city", predicate_parameters={"?l": "?from", "?c": "?c"},
                               description="The starting location must be in the specified city"),
                    Predicate_(name="in_city", predicate_parameters={"?l": "?to", "?c": "?c"},
                               description="The destination location must be in the same city")
                ]
            },
            effects={
                "and": [
                    {"not": Predicate_(name="at", predicate_parameters={"?t": "?t", "?l": "?from"},
                                       description="The truck is no longer at the starting location")},
                    Predicate_(name="at", predicate_parameters={"?t": "?t", "?l": "?to"},
                               description="The truck is now at the destination location")
                ]
            }
        ),
        Action_(
            name="fly_airplane",
            description="An airplane flies from one city's airport to another city's airport. Cities are directly connected.",
            action_parameters={"?a": "airplane", "?from": "airport", "?to": "airport", "?from_city": "city",
                               "?to_city": "city"},
            preconditions={
                "and": [
                    Predicate_(name="at", predicate_parameters={"?o": "?a", "?l": "?from"},
                               description="The airplane must be at the departure airport"),
                    Predicate_(name="in_city", predicate_parameters={"?l": "?from", "?c": "?from_city"},
                               description="The departure airport must be in the departure city"),
                    Predicate_(name="in_city", predicate_parameters={"?l": "?to", "?c": "?to_city"},
                               description="The destination airport must be in the destination city"),
                    Predicate_(name="is_airport", predicate_parameters={"?l": "?from"},
                               description="The departure location must be an airport"),
                    Predicate_(name="is_airport", predicate_parameters={"?l": "?to"},
                               description="The destination location must be an airport"),
                    Predicate_(name="different", predicate_parameters={"?c1": "?from_city", "?c2": "?to_city"},
                               description="The departure and destination cities must be different")
                ]
            },
            effects={
                "and": [
                    {"not": Predicate_(name="at", predicate_parameters={"?o": "?a", "?l": "?from"},
                                       description="The airplane is no longer at the departure airport")},
                    Predicate_(name="at", predicate_parameters={"?o": "?a", "?l": "?to"},
                               description="The airplane is now at the destination airport")
                ]
            }
        )
    ],

    object_instances=ObjectInstances(
        objects={
            "ado_city": "The city of Ado",
            "betar_city": "The city of Betar",
            "colin_city": "The city of Colin",
            "duran_city": "The city of Duran",
            "ado_storage": "Storage location in Ado",
            "ado_airport": "Airport in Ado",
            "ado_truck": "Truck assigned to Ado city",
            "betar_storage": "Storage location in Betar",
            "betar_airport": "Airport in Betar",
            "betar_street": "Street location in Betar",
            "betar_truck": "Truck assigned to Betar city",
            "colin_promenade": "Promenade location in Colin",
            "colin_airport": "Airport in Colin",
            "colin_truck": "Truck assigned to Colin city",
            "duran_airport": "Airport in Duran",
            "duran_truck": "Truck assigned to Duran city",
            "airplane1": "The only airplane in the system, currently at Duran's airport",
            "package1": "First package from Ado, needs to go to Betar Street",
            "package2": "Second package from Ado, needs to go to Colin Promenade",
            "package3": "Third package from Ado, needs to go to Colin Promenade",
            "package4": "First package from Betar, needs to go to Ado Storage",
            "package5": "Second package from Betar, needs to go to Ado Storage"
        }
    ),

    initial_state=InitialState(
        initial_state_predicates=[
            Predicate_(name="at", predicate_parameters={"A1": "AdoStorage"},
                       description="First Ado package is in Ado's storage"),
            Predicate_(name="at", predicate_parameters={"A2": "AdoStorage"},
                       description="Second Ado package is in Ado's storage"),
            Predicate_(name="at", predicate_parameters={"A3": "AdoStorage"},
                       description="Third Ado package is in Ado's storage"),
            Predicate_(name="at", predicate_parameters={"B1": "BetarStorage"},
                       description="First Betar package is in Betar's storage"),
            Predicate_(name="at", predicate_parameters={"B2": "BetarStorage"},
                       description="Second Betar package is in Betar's storage"),
            Predicate_(name="at", predicate_parameters={"AdoTruck": "AdoStorage"},
                       description="Ado's truck starts at its storage"),
            Predicate_(name="at", predicate_parameters={"BetarTruck": "BetarStorage"},
                       description="Betar's truck starts at its storage"),
            Predicate_(name="at", predicate_parameters={"ColinTruck": "ColinStorage"},
                       description="Colin's truck starts at its storage"),
            Predicate_(name="at", predicate_parameters={"DuranTruck": "DuranStorage"},
                       description="Duran's truck starts at its storage"),
            Predicate_(name="at", predicate_parameters={"Plane1": "DuranAirport"},
                       description="The plane starts at Duran's airport"),
            Predicate_(name="in-city", predicate_parameters={"AdoStorage": "Ado"},
                       description="Ado storage is in Ado city"),
            Predicate_(name="in-city", predicate_parameters={"AdoAirport": "Ado"},
                       description="Ado airport is in Ado city"),
            Predicate_(name="in-city", predicate_parameters={"BetarStorage": "Betar"},
                       description="Betar storage is in Betar city"),
            Predicate_(name="in-city", predicate_parameters={"BetarStreet": "Betar"},
                       description="Betar street is in Betar city"),
            Predicate_(name="in-city", predicate_parameters={"BetarAirport": "Betar"},
                       description="Betar airport is in Betar city"),
            Predicate_(name="in-city", predicate_parameters={"ColinStorage": "Colin"},
                       description="Colin storage is in Colin city"),
            Predicate_(name="in-city", predicate_parameters={"ColinPromenade": "Colin"},
                       description="Colin promenade is in Colin city"),
            Predicate_(name="in-city", predicate_parameters={"ColinAirport": "Colin"},
                       description="Colin airport is in Colin city"),
            Predicate_(name="in-city", predicate_parameters={"DuranStorage": "Duran"},
                       description="Duran storage is in Duran city"),
            Predicate_(name="in-city", predicate_parameters={"DuranAirport": "Duran"},
                       description="Duran airport is in Duran city")
        ]
    ),

    goal_state=GoalState(
        goal_state_predicates={
            "and": [
                Predicate_(name="at", predicate_parameters={"package": "L1", "location": "bal_street"},
                           description="Package L1 from Ado should be at Bal Street in Betar"),
                Predicate_(name="at", predicate_parameters={"package": "L2", "location": "cli_promenade"},
                           description="Package L2 from Ado should be at Cli Promenade in Colin"),
                Predicate_(name="at", predicate_parameters={"package": "L3", "location": "cli_promenade"},
                           description="Package L3 from Ado should be at Cli Promenade in Colin"),
                Predicate_(name="at", predicate_parameters={"package": "L4", "location": "ado_storage"},
                           description="Package L4 from Betar should be at Ado storage"),
                Predicate_(name="at", predicate_parameters={"package": "L5", "location": "ado_storage"},
                           description="Package L5 from Betar should be at Ado storage")
            ]
        }
    ),

    feedback=[]
)


# def create_domain(state: NL2PlanState):
#     """
#     Erzeugt die PDDL-Domain aus dem gegebenen NL2PlanState.
#     """
#
#     # 0) Erstelle die Requirements
#     requirements = [Requirements.STRIPS, Requirements.TYPING, Requirements.EQUALITY, Requirements.NEG_PRECONDITION,
#                     Requirements.DIS_PRECONDITION, Requirements.UNIVERSAL_PRECONDITION,
#                     Requirements.CONDITIONAL_EFFECTS]
#
#     domain = Domain(
#         name=state.domain_name,
#         requirements=requirements,
#         predicates=[],
#         actions=[]
#     )
#
#     return domain
#
#
# def create_types(state:NL2PlanState):
#     """
#        Erstellt PDDL Domain und Problem aus einem NL2PlanState Objekt
#     """
#
#
#     # 1) Erstelle das Mapping von Kind-Typ zu Parent-Typ (oder None für Wurzel)
#     types_map = {}
#
#     # Alle Elterntypen zuerst sammeln (für Root-Type "object" ohne Parent)
#     for hierarchy in state.type_hierarchy:
#         parent_name = hierarchy.parent_type.name
#         if parent_name not in types_map:
#             types_map[parent_name] = None  # Root-Type bekommt None als Parent
#
#     # Jetzt alle Kindtypen einzeln mit ihrem Elterntyp verknüpfen
#     for hierarchy in state.type_hierarchy:
#         parent_name = hierarchy.parent_type.name
#         for child in hierarchy.child_types:
#             child_name = child.name
#             types_map[child_name] = parent_name
#
#     types=types_map_to_pddl(types_map)
#     return types
#
#
#
#
#
#
#
# def types_map_to_pddl(types_map):
#     lines = []
#     for child, parent in types_map.items():
#         # Root-Type hat parent = None
#         if parent is None:
#             continue
#         lines.append(f"{child} - {parent}")
#     return "(:types\n    " + "\n    ".join(lines) + "\n)"
#
# print(create_domain(result1))
# print(create_types(result1))

def create_domain(state: NL2PlanState):
    # 1. Requirements definieren
    requirements = [
        Requirements.STRIPS,
        Requirements.TYPING,
        Requirements.EQUALITY,
        Requirements.NEG_PRECONDITION,
        Requirements.DIS_PRECONDITION,
        Requirements.UNIVERSAL_PRECONDITION,
        Requirements.CONDITIONAL_EFFECTS,
    ]

    # 2. Domain erzeugen mit diesem Mapping
    domain = Domain(
        name=state.domain_name,
        requirements=requirements,
        types=create_types(state),
        predicates=[],  # später ergänzen
        actions=[],     # später ergänzen
    )

    return domain


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


domain = create_domain(result1)
print(domain)

def create_predicates(state: NL2PlanState):
    predicates = []

    # # Hier können die Prädikate aus dem State extrahiert und in PDDL-Form gebracht werden
    # for action in state.actions:
    #     for precondition in action.preconditions.get("preconditions", []):
    #         predicates.append(precondition)
    #
    #     for effect in action.effects.get("effects", []):
    #         predicates.append(effect)
    #
    # return predicates

print(create_predicates(result1))