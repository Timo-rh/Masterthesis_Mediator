import os
from utils.paths import results_dir
from src.agent.states import NL2PlanState
from collections import defaultdict
from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements


class StateBasedPDDLConverter:
    def __init__(self):
        self.results_dir = results_dir

    def convert_state_to_pddl(self, state: NL2PlanState, problem_number=None):
        """
        Konvertiert ein NL2PlanState-Objekt zu PDDL-Dateien
        """
        # Results-Ordner erstellen
        os.makedirs(self.results_dir, exist_ok=True)

        # Problem-Nummer bestimmen
        if problem_number is None:
            problem_number = self._get_next_problem_number(state.domain_name)

        problem_name = f"{state.domain_name}_problem_{problem_number}"

        print(f"Konvertiere State zu PDDL:")
        print(f"  Domain: {state.domain_name}")
        print(f"  Problem: {problem_name}")
        print(f"  Zielordner: {self.results_dir}")

        try:
            self._convert_with_pddl_package(state, problem_name)
        except Exception as e:
            print(f"Fehler mit PDDL-Paket: {e}. Verwende Fallback-Methode.")

    def _get_next_problem_number(self, domain_name):
        """Ermittelt die nächste verfügbare Problem-Nummer"""
        counter = 1
        while True:
            potential_filename = os.path.join(self.results_dir, f"{domain_name}_problem_{counter}.pddl")
            if not os.path.exists(potential_filename):
                return counter
            counter += 1

    def _convert_with_pddl_package(self, state: NL2PlanState, problem_name: str):
        """Konvertierung mit dem PDDL-Paket"""

        # 1. Types sammeln
        types_dict = self._extract_types(state)

        # 2. Predicates definieren
        predicates_list = self._create_predicates_list(state, types_dict)

        # 3. Actions erstellen
        actions_list = self._create_actions_list(state, types_dict, predicates_list)

        # 4. Requirements
        requirements = [
            Requirements.STRIPS,
            Requirements.TYPING,
            Requirements.EQUALITY,
            Requirements.NEGATIVE_PRECONDITIONS,
            Requirements.DISJUNCTIVE_PRECONDITIONS,
            Requirements.UNIVERSAL_PRECONDITIONS,
            Requirements.CONDITIONAL_EFFECTS
        ]

        # 5. Domain erstellen (OHNE Constants)
        domain = Domain(
            state.domain_name,
            requirements=requirements,
            types=types_dict,
            predicates=predicates_list,
            actions=actions_list
        )

        # 6. Problem erstellen (mit Objects statt Constants)
        objects_list = self._create_objects_list(state, types_dict)
        init_list = self._create_init_list(state, predicates_list, objects_list)
        goal = self._create_goal(state, predicates_list, objects_list)

        problem = Problem(
            problem_name,
            domain=domain,
            requirements=requirements,
            objects=objects_list,
            init=init_list,
            goal=goal
        )

        # 7. PDDL-Dateien schreiben
        self._write_pddl_files_with_package(domain, problem, state.domain_name, problem_name)

    def _extract_types(self, state: NL2PlanState):
        """Extrahiert Types für das PDDL-Paket"""
        types_dict = {}

        if state.type_hierarchy:
            for hierarchy_obj in state.type_hierarchy:
                parent_name = hierarchy_obj.parent_type.name

                # Parent Type hinzufügen (außer "object")
                if parent_name != "object":
                    types_dict[parent_name] = None

                # Child Types hinzufügen
                if hierarchy_obj.child_types:
                    for child_type in hierarchy_obj.child_types:
                        child_name = child_type.name
                        if parent_name == "object":
                            types_dict[child_name] = None
                        else:
                            types_dict[child_name] = parent_name

        return types_dict

    def _create_predicates_list(self, state: NL2PlanState, types_dict):
        """Erstellt Predicates für das PDDL-Paket - mit tatsächlichen Typen und Namen aus Actions"""
        predicate_signatures = {}

        if not state.actions:
            return []

        # Sammle alle Prädikate aus Actions mit ihrer Typ-Information
        for action in state.actions:
            action_params = action.action_parameters  # {"?p": "package", "?t": "truck", "?l": "location"}

            # Sammle aus Preconditions
            for condition_group in action.preconditions.values():
                for predicate in condition_group:
                    self._process_predicate(predicate, action_params, predicate_signatures, types_dict)

            # Sammle aus Effects
            for effect_group in action.effects.values():
                for predicate in effect_group:
                    self._process_predicate(predicate, action_params, predicate_signatures, types_dict)

        return list(predicate_signatures.values())

    def _process_predicate(self, predicate, action_params, predicate_signatures, types_dict):
        """Verarbeitet ein einzelnes Prädikat und extrahiert die Typ-Information"""
        name = predicate.name

        # Entferne "not_" Prefix für Signatur-Erkennung
        if name.startswith("not_"):
            name = name[4:]

        # Prüfe ob diese Predicate-Signatur bereits existiert
        if name not in predicate_signatures:
            # Extrahiere Parameter-Namen und -Typen direkt aus der Action
            param_names = []
            param_types = []

            for param_key, param_value in predicate.predicate_parameters.items():
                # param_value ist der Verweis wie "?p", param_key ist meist derselbe
                if param_value in action_params:
                    # Verwende den originalen Parameter-Namen aus der Action
                    param_names.append(param_value.lstrip('?'))  # "?p" → "p"
                    # Hole den Typ aus action_parameters
                    param_types.append(action_params[param_value])
                else:
                    # Fallback für unbekannte Parameter
                    param_names.append(param_key.lstrip('?'))
                    param_types.append("object")

            # Validiere Typen gegen verfügbare types_dict
            validated_types = []
            for ptype in param_types:
                if ptype in types_dict:
                    validated_types.append(ptype)
                else:
                    validated_types.append("object")

            # Erstelle Variable-Liste mit den originalen Namen und extrahierten Typen
            if param_names and validated_types:
                var_names_str = " ".join(param_names)
                var_list = variables(var_names_str, types=validated_types)

                # Predicate erstellen
                pred_obj = Predicate(name, *var_list)
                predicate_signatures[name] = pred_obj

def _create_actions_list(self, state: NL2PlanState, types_dict, predicates_list):
    """Erstellt Actions für das PDDL-Paket - verwendet vorhandene action_parameters"""
    actions_list = []
    
    if state.actions:
        predicates_by_name = {pred.name: pred for pred in predicates_list}
        
        for action in state.actions:
            # 1. Parameter direkt aus action.action_parameters verwenden
            # Input: {"?p": "package", "?t": "truck", "?l": "location"}
            param_names = [name.lstrip('?') for name in action.action_parameters.keys()]
            param_types = list(action.action_parameters.values())
            
            if param_names:
                param_vars = variables(" ".join(param_names), types=param_types)
                param_dict = dict(zip(action.action_parameters.keys(), param_vars))
            else:
                param_vars = []
                param_dict = {}
            
            # 2. Preconditions erstellen
            combined_precondition = self._build_preconditions(
                action.preconditions, predicates_by_name, param_dict
            )
            
            # 3. Effects erstellen
            combined_effect = self._build_effects(
                action.effects, predicates_by_name, param_dict
            )
            
            # 4. Action erstellen
            action_obj = Action(
                action.name,
                parameters=param_vars,
                precondition=combined_precondition,
                effect=combined_effect
            )
            
            actions_list.append(action_obj)
    
    return actions_list

def _build_preconditions(self, preconditions_dict, predicates_by_name, param_dict):
    """Baut Preconditions auf - beachtet Gruppen-Namen für Negation"""
    all_conditions = []
    
    for group_name, condition_list in preconditions_dict.items():
        for condition in condition_list:
            pred_condition = self._create_condition_with_package(
                condition, predicates_by_name, param_dict
            )
            if pred_condition:
                # Prüfe Gruppen-Namen für Negations-Logik
                if ("not_" in group_name.lower() or 
                    "negative" in group_name.lower() or
                    group_name.lower().endswith("_conditions") and "not" in group_name.lower()):
                    all_conditions.append(~pred_condition)
                else:
                    all_conditions.append(pred_condition)
    
    # Alle mit & verknüpfen
    if len(all_conditions) > 1:
        combined = all_conditions[0]
        for cond in all_conditions[1:]:
            combined = combined & cond
        return combined
    elif all_conditions:
        return all_conditions[0]
    else:
        return None

def _build_effects(self, effects_dict, predicates_by_name, param_dict):
    """Baut Effects auf - unterscheidet ADD/DELETE Effects"""
    all_effects = []
    
    for group_name, effect_list in effects_dict.items():
        for effect in effect_list:
            pred_effect = self._create_effect_with_package(
                effect, predicates_by_name, param_dict
            )
            
            if pred_effect:
                # Effect-Klassifizierung basierend auf Namen oder Gruppe
                if (effect.name.startswith("not_") or 
                    "delete" in group_name.lower() or 
                    "remove" in group_name.lower()):
                    
                    # DELETE-Effect: negieren
                    if effect.name.startswith("not_"):
                        # "not_in" → eigentlich "in" negieren
                        actual_name = effect.name[4:]
                        if actual_name in predicates_by_name:
                            actual_pred = self._create_single_predicate(
                                actual_name, effect.predicate_parameters, 
                                predicates_by_name, param_dict
                            )
                            if actual_pred:
                                all_effects.append(~actual_pred)
                    else:
                        all_effects.append(~pred_effect)
                else:
                    # ADD-Effect: positiv
                    all_effects.append(pred_effect)
    
    # Alle Effects mit & verknüpfen
    if len(all_effects) > 1:
        combined = all_effects[0]
        for eff in all_effects[1:]:
            combined = combined & eff
        return combined
    elif all_effects:
        return all_effects[0]
    else:
        return None

    def _create_objects_list(self, state: NL2PlanState, types_dict):
        """Erstellt Objects für das Problem (nicht Domain)"""
        objects_list = []

        if state.object_instances:
            objects_by_type = self._infer_object_types(state)

            for obj_type, obj_names in objects_by_type.items():
                # Typ für Objects bestimmen
                type_name = obj_type if obj_type in types_dict else None

                # Objects erstellen
                for obj_name in obj_names:
                    obj_instance = constants(obj_name, type_=type_name)[0]
                    objects_list.append(obj_instance)

        return objects_list

    def _create_init_list(self, state: NL2PlanState, predicates_list, objects_list):
        """Erstellt Initial State für PDDL-Paket - korrigiert für result1.json Struktur"""
        init_list = []

        # ✅ KORRIGIERT: initial_state ist direkte Liste von Predicate_ Objekten
        if state.initial_state:
            predicates_by_name = {pred.name: pred for pred in predicates_list}
            objects_by_name = {obj.name: obj for obj in objects_list}

            # Direkt über die Liste iterieren (nicht .initial_state_predicates!)
            for predicate in state.initial_state:
                name = predicate.name
                is_negated = name.startswith("not_")

                if is_negated:
                    name = name[4:]

                if name in predicates_by_name:
                    pred_template = predicates_by_name[name]

                    # Parameter-Mapping
                    param_values = []
                    for param_key in sorted(predicate.predicate_parameters.keys()):
                        param_value = predicate.predicate_parameters[param_key]
                        if param_value in objects_by_name:
                            param_values.append(objects_by_name[param_value])
                        else:
                            obj_instance = constants(param_value)[0]
                            param_values.append(obj_instance)

                    # Predicate instanziieren
                    pred_instance = pred_template(*param_values) if param_values else pred_template

                    if is_negated:
                        init_list.append(~pred_instance)
                    else:
                        init_list.append(pred_instance)

        return init_list

    def _create_goal(self, state: NL2PlanState, predicates_list, objects_list):
        """Erstellt Goal für PDDL-Paket"""
        goals = []

        if state.goal_state and state.goal_state.goal_state_predicates:
            predicates_by_name = {pred.name: pred for pred in predicates_list}
            objects_by_name = {obj.name: obj for obj in objects_list}

            for goal_group in state.goal_state.goal_state_predicates.values():
                for goal in goal_group:
                    name = goal.name
                    is_negated = name.startswith("not_")

                    if is_negated:
                        name = name[4:]

                    if name in predicates_by_name:
                        pred_template = predicates_by_name[name]

                        # Parameter-Mapping
                        param_values = []
                        for param_key in sorted(goal.predicate_parameters.keys()):
                            param_value = goal.predicate_parameters[param_key]
                            if param_value in objects_by_name:
                                param_values.append(objects_by_name[param_value])
                            else:
                                obj_instance = constants(param_value)[0]
                                param_values.append(obj_instance)

                        # Predicate instanziieren
                        pred_instance = pred_template(*param_values) if param_values else pred_template

                        if is_negated:
                            goals.append(~pred_instance)
                        else:
                            goals.append(pred_instance)

        # Goal kombinieren
        if len(goals) > 1:
            combined_goal = goals[0]
            for goal in goals[1:]:
                combined_goal = combined_goal & goal
            return combined_goal
        elif goals:
            return goals[0]
        else:
            return None

    def _write_pddl_files_with_package(self, domain, problem, domain_name, problem_name):
        """Schreibt PDDL-Dateien mit dem PDDL-Paket"""

        # Domain-Datei
        domain_filename = os.path.join(self.results_dir, f"{domain_name}.pddl")
        with open(domain_filename, "w", encoding='utf-8') as f:
            f.write(str(domain))
        print(f"Domain-Datei '{domain_filename}' wurde erstellt.")

        # Problem-Datei
        problem_filename = os.path.join(self.results_dir, f"{problem_name}.pddl")
        with open(problem_filename, "w", encoding='utf-8') as f:
            f.write(str(problem))
        print(f"Problem-Datei '{problem_filename}' wurde erstellt.")

    def _infer_object_types(self, state: NL2PlanState):
        """Leitet Objekttypen ab"""
        objects_by_type = defaultdict(list)

        if not state.object_instances:
            return objects_by_type

        # Alle verfügbaren Typen sammeln
        all_types = set()
        if state.type_hierarchy:
            for hierarchy_obj in state.type_hierarchy:
                all_types.add(hierarchy_obj.parent_type.name)
                if hierarchy_obj.child_types:
                    for child in hierarchy_obj.child_types:
                        all_types.add(child.name)

        # Objekte typisieren
        for obj_name, description in state.object_instances.objects.items():
            obj_type = self._infer_single_object_type(obj_name, description, all_types)
            if obj_type:
                objects_by_type[obj_type].append(obj_name)

        return dict(objects_by_type)

    def _infer_single_object_type(self, obj_name, description, all_types):
        """Leitet Typ eines einzelnen Objekts ab"""
        obj_name_lower = obj_name.lower()
        description_lower = description.lower() if description else ""

        # Direkte Übereinstimmungen
        for type_name in all_types:
            if type_name in obj_name_lower or type_name in description_lower:
                return type_name

        # Fallback-Logik
        type_keywords = {
            "city": ["city", "town"],
            "location": ["location", "place"],
            "storage": ["storage", "warehouse"],
            "street": ["street", "road"],
            "promenade": ["promenade", "boulevard"],
            "airport": ["airport", "airfield"],
            "truck": ["truck", "vehicle"],
            "airplane": ["airplane", "plane", "aircraft"],
            "package": ["package", "parcel", "item"],
            "vehicle": ["vehicle", "transport"]
        }

        for type_name, keywords in type_keywords.items():
            if type_name in all_types:
                for keyword in keywords:
                    if keyword in obj_name_lower or keyword in description_lower:
                        return type_name

        return "object" if "object" in all_types else None


# Benutzerfreundliche Funktion
def convert_state_to_pddl(state: NL2PlanState, problem_number=None):
    """
    Konvertiert ein NL2PlanState-Objekt zu PDDL-Dateien
    """
    converter = StateBasedPDDLConverter()
    converter.convert_state_to_pddl(state, problem_number)
    return state  # Für Langgraph-Kompatibilität



import os
from utils.paths import results_dir
from src.agent.states import NL2PlanState
from collections import defaultdict
from pddl.logic import Predicate, constants, variables
from pddl.core import Domain, Problem
from pddl.action import Action
from pddl.requirements import Requirements

# ... [Alle bestehenden Klassen und Methoden bleiben unverändert] ...

# =============================================================================
# DIREKTER TEST-AUFRUF
# =============================================================================

if __name__ == "__main__":
    import json

    # Minimaler Test-State basierend auf result1.json
    test_state = NL2PlanState(
        natural_language_task="Transport packages using trucks and airplanes",
        domain_desc="Logistics domain with trucks, airplanes, and packages",
        domain_name="logistics",

        # Types aus result1.json
        types=[
            {"name": "city", "description": "A city contains locations"},
            {"name": "location", "description": "A place within a city"},
            {"name": "truck", "description": "Vehicle for city transport"},
            {"name": "airplane", "description": "Vehicle for inter-city transport"},
            {"name": "package", "description": "Item to be transported"}
        ],

        # Type hierarchy
        type_hierarchy=[
            {
                "parent_type": {"name": "object", "description": "Root type"},
                "child_types": [
                    {"name": "city", "description": "A city"},
                    {"name": "location", "description": "A location"},
                    {"name": "vehicle", "description": "A vehicle"},
                    {"name": "package", "description": "A package"}
                ]
            },
            {
                "parent_type": {"name": "vehicle", "description": "A vehicle"},
                "child_types": [
                    {"name": "truck", "description": "A truck"},
                    {"name": "airplane", "description": "An airplane"}
                ]
            }
        ],

        # Eine einfache Action
        actions=[
            {
                "name": "load_truck",
                "description": "Load package onto truck",
                "action_parameters": {"?p": "package", "?t": "truck", "?l": "location"},
                "preconditions": {
                    "at_conditions": [
                        {
                            "name": "at",
                            "predicate_parameters": {"?p": "?p", "?l": "?l"},
                            "description": "Package at location"
                        },
                        {
                            "name": "at",
                            "predicate_parameters": {"?t": "?t", "?l": "?l"},
                            "description": "Truck at location"
                        }
                    ]
                },
                "effects": {
                    "add_effects": [
                        {
                            "name": "in",
                            "predicate_parameters": {"?p": "?p", "?t": "?t"},
                            "description": "Package in truck"
                        }
                    ]
                }
            }
        ],

        # Objekte
        object_instances={
            "objects": {
                "P1": "Package 1",
                "T1": "Truck 1",
                "L1": "Location 1"
            }
        },

        # Initial state
        initial_state=[
            {
                "name": "at",
                "predicate_parameters": {"P1": "P1", "L1": "L1"},
                "description": "Package P1 at location L1"
            },
            {
                "name": "at",
                "predicate_parameters": {"T1": "T1", "L1": "L1"},
                "description": "Truck T1 at location L1"
            }
        ],

        # Goal state
        goal_state={
            "goal_state_predicates": {
                "and": [
                    {
                        "name": "in",
                        "predicate_parameters": {"P1": "P1", "T1": "T1"},
                        "description": "Package P1 in truck T1"
                    }
                ]
            }
        },

        feedback=[]
    )

    print("🚀 STARTE PDDL-KONVERTIERUNG")
    print("=" * 50)

    try:
        # PDDL konvertieren
        converter = StateBasedPDDLConverter()
        converter.convert_state_to_pddl(test_state, problem_number=1)

        print("\n✅ ERFOLGREICH!")
        print(f"📁 Dateien in: {converter.results_dir}")

    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()