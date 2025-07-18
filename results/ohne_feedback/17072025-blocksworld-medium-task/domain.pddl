(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        block - object
    )
    (:predicates
        (hand_empty)
        (clear ?b - block)
        (holding ?b - block)
        (on ?b1 - block ?b2 - block)
        (on_table ?b - block)
    )

    (:action pick_up
        :parameters (?b - block)
        :precondition (and (clear ?b) (hand_empty) (on_table ?b))
        :effect (and (holding ?b) (not (hand_empty)) (not (on_table ?b)) (not (clear ?b)))
    )

    (:action put_down_on_table
        :parameters (?b - block)
        :precondition (holding ?b)
        :effect (and (not (holding ?b)) (hand_empty) (on_table ?b) (clear ?b))
    )

    (:action stack
        :parameters (?b1 - block ?b2 - block)
        :precondition (and (holding ?b1) (clear ?b2))
        :effect (and (on ?b1 ?b2) (clear ?b1) (not (holding ?b1)) (hand_empty) (not (clear ?b2)))
    )

    (:action unstack
        :parameters (?b1 - block ?b2 - block)
        :precondition (and (hand_empty) (clear ?b1) (on ?b1 ?b2))
        :effect (and (holding ?b1) (not (hand_empty)) (not (clear ?b1)) (not (on ?b1 ?b2)) (clear ?b2))
    )
)