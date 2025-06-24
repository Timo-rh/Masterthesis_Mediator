import unified_planning as up
from unified_planning.model import Problem, InstantaneousAction, Object, Fluent
from unified_planning.shortcuts import UserType
import json
import os
from utils.paths import *

# Pfad zur JSON-Datei im Ordner "results"
json_path = "results/ohne feedback/result1.json"

# JSON-Datei laden
with open(json_path, "r", encoding="utf-8") as file:
    json_model = json.load(file)

# Jetzt kannst du mit dem geladenen JSON-Objekt weiterarbeiten
print("Natural Language Task:", json_model["natural_language_task"])
# Weitere Verarbeitung z. B. Zugriff auf types, actions etc.

# Beispiel: Alle Typnamen ausgeben
for item in json_model.get("types", []):
    print("Type:", item["name"], "-", item["description"])



def json_to_up_problem(json_model):
    problem = Problem('mydomain')
    types = {t: UserType(t) for t in json_model['types']}
    problem.add_types(types.values())

    # Aktionen
    for act in json_model['actions']:
        params = {p['name']: types[p['type']] for p in act['params']}
        up_act = InstantaneousAction(act['name'], **params)
        # Preconditions & Effects hinzufügen
        # Beispiel: up_act.add_precondition(...)
        problem.add_action(up_act)
    # Objekte
    for o in json_model['objects']:
        problem.add_object(Object(o['name'], types[o['type']]))
    # Initialzustand & Ziel
    for init in json_model['init']:
        # problem.set_initial_value(...)
        pass
    for g in json_model['goal']:
        # problem.add_goal(...)
        pass

    return problem
