(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        block color stack table - object
    )
    (:predicates (arm_empty) (clear ?b - block)  (has_color ?b - block ?c - color)  (holding ?b - block)  (on ?b1 ?b2)  (on_table ?b - block) (are_different ?block_held - block ?block_target - block))
    (:action pick_up
        :parameters (?block - block)
        :precondition (and (clear ?block) (on_table ?block) (arm_empty))
        :effect (holding ?block)
    )
     (:action put_down_on_table
        :parameters (?block - block)
        :precondition (holding ?block)
        :effect (and (not (holding ?block)) (on_table ?block) (clear ?block))
    )
     (:action stack
        :parameters (?block_held - block ?block_target - block)
        :precondition (and (holding ?block_held) (clear ?block_target) (are_different ?block_held ?block_target))
        :effect (and (not (holding ?block_held)) (on ?block_held ?block_target) (not (clear ?block_target)))
    )
)