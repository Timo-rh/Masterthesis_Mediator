# def check_keyword_usage(constructed_action):
#     """Überprüft, ob ungültige Keywords in der konstruierten Aktion verwendet werden."""
#     # Konvertiere die effects zu einem String für die Keyword-Suche
#     effects_str = str(constructed_action.effects)
#
#     for keyword in ['forall', 'exists', 'if']:
#         if keyword in effects_str:
#             feedback_message = f'The keyword `{keyword}` is not supported in the action effects.'
#             #kein_error, error_type, keyword, feedback_message
#             return False, 'invalid_effect_keyword', keyword, feedback_message
#     # gibt keinen Error für "has unsupported_keywords" zurück, falls keywords nicht gefunden werden
#     return True, 'has_unsupported_keywords', None, None
#
# def check_param_types(constructed_action, state:NL2PlanState):
#     # Extrahiere alle Typ-Namen aus der Hierarchie
#     valid_types = set()
#     for hierarchy_obj in state.type_hierarchy:
#         valid_types.add(hierarchy_obj.parent_type.name)
#         if hierarchy_obj.child_types:
#             for child_type in hierarchy_obj.child_types:
#                 valid_types.add(child_type.name)
#
#     for param_type in constructed_action.action_parameters.values():
#         if param_type not in valid_types:
#             feedback_message = f'There is an invalid object type `{param_type}` for the parameter {constructed_action.action_parameters}.'
#             # kein_error, error_type, fehlerhafter_parameter, feedback_message
#             return False, 'invalid_object_type', constructed_action.action_parameters, feedback_message
#     return True, 'invalid_object_type', None, None
#
# def check_predicate_names(constructed_action, state:NL2PlanState):
#
#
# def validate_action(constructed_action):
#     """Validiert eine konstruierte Aktion."""
#     # Überprüfe auf ungültige Keywords
#     is_valid, error_type, keyword, feedback_message = check_keyword_usage(constructed_action)
#
#     if not is_valid:
#         return False, error_type, keyword, feedback_message
#
#     # Weitere Validierungen können hier hinzugefügt werden
#
#     return "valid"