(define (problem easy-task)
    (:domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:objects
        blue_block green_block red_block yellow_block - block
    )
    (:init
        (arm_empty)
        (clear blue_block)
        (clear green_block)
        (on blue_block red_block)
        (on green_block table1)
        (on red_block yellow_block)
        (on yellow_block table1)
    )
    (:goal
        (and
            (on red_block green_block)
        )
    )
)