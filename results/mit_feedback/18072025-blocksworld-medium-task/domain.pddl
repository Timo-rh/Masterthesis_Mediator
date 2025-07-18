(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        block table - object
    )
    (:predicates (clear ?b - block)  (handempty) (holding ?b - block)  (on ?block1 - block ?block2 - block)  (ontable ?b - block))
    (:action pick_up
        :parameters (?b - block ?y - block)
        :precondition (and (clear ?b) (handempty) (or (ontable ?b) (on ?b ?y)))
        :effect (and (holding ?b) (not (handempty)) (not (ontable ?b)) (not (on ?b ?y)))
    )
     (:action put_down
        :parameters (?b - block ?dest - block)
        :precondition (and (holding ?b) (clear ?dest))
        :effect (and (not (holding ?b)) (handempty) (on ?b ?dest) (clear ?b))
    )
)