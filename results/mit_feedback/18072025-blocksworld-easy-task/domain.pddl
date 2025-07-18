(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        block - object
    )
    (:predicates
        (arm_empty)
        (clear ?block - block)
        (on_table ?block - block)
        (on ?block1 - block ?block2 - block)
        (holding ?block - block)
    )
    (:action pick_up_block
        :parameters (?block - block)
        :precondition (and
            (clear ?block)
            (or
                (on_table ?block)
                (exists (?other - block) (on ?block ?other))
            )
            (arm_empty)
        )
        :effect (and
            (holding ?block)
            (not (arm_empty))
            (not (on_table ?block))
            (forall (?other - block)
                (not (on ?block ?other))
            )
            (forall (?other - block)
                (when (on ?block ?other)
                    (clear ?other)
                )
            )
        )
    )
    (:action put_down_block_on_table
        :parameters (?block - block)
        :precondition (and
            (holding ?block)
        )
        :effect (and
            (on_table ?block)
            (clear ?block)
            (not (holding ?block))
            (arm_empty)
        )
    )
    (:action stack_block
        :parameters (?block ?target - block)
        :precondition (and
            (holding ?block)
            (clear ?target)
            (not (= ?block ?target))
        )
        :effect (and
            (on ?block ?target)
            (not (holding ?block))
            (clear ?block)
            (not (clear ?target))
            (arm_empty)
        )
    )
)
