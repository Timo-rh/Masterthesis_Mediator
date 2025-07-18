(define (domain blocksworld)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

  (:types
    block - object
    red_block blue_block green_block - block
  )

  (:predicates
    (clear ?b - block)
    (on_table ?b - block)
    (on ?b1 ?b2 - block)
    (holding ?b - block)
    (arm_empty)
  )

  (:action pick_up_block
    :parameters (?b - block)
    :precondition (and
      (clear ?b)
      (on_table ?b)
      (arm_empty)
    )
    :effect (and
      (not (on_table ?b))
      (holding ?b)
      (not (arm_empty))
    )
  )

  (:action put_down_block_on_table
    :parameters (?b - block)
    :precondition (and
      (holding ?b)
    )
    :effect (and
      (on_table ?b)
      (clear ?b)
      (not (holding ?b))
      (arm_empty)
    )
  )

  (:action stack_block
    :parameters (?held_block ?target_block - block)
    :precondition (and
      (holding ?held_block)
      (clear ?target_block)
      (not (= ?held_block ?target_block))
    )
    :effect (and
      (arm_empty)
      (clear ?held_block)
      (on ?held_block ?target_block)
      (not (holding ?held_block))
      (not (clear ?target_block))
    )
  )
)