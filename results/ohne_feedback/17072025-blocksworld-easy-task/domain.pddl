(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        block position stack - object
        table - position
    )
    (:predicates (arm_empty) (clear ?position - position)  (holding ?block)  (on ?block1 - block ?position - position)  (on_table ?b - block))
    (:action pick_up
        :parameters (?b - block)
        :precondition (and (clear ?b) (handempty) (on_table ?b))
        :effect (and (holding ?b) (not (handempty)) (not (on_table ?b)))
    )
     (:action put_down
        :parameters (?b - block)
        :precondition (holding ?b)
        :effect (and (not (holding ?b)) (on_table ?b) (clear ?b))
    )
     (:action stack
        :parameters (?b1 - block ?b2 - block)
        :precondition (and (holding ?b1) (clear ?b2))
        :effect (and (on ?b1 ?b2) (not (holding ?b1)))
    )
)