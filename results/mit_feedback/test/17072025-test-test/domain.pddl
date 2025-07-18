(define (domain test)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        test - object
    )
    (:predicates (can_test ?t - test)  (tested ?t - test))
    (:action test_action
        :parameters (?t - test)
        :precondition (can_test ?t)
        :effect (and (tested ?t) (not (can_test ?t)))
    )
)