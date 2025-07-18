(define (domain blocksworld)
  (:requirements
   :strips :typing :equality :negative-preconditions :disjunctive-preconditions :universal-preconditions :conditional-effects :existential-preconditions

  )

  (:types
    location - object
    block - location
    table - location
  )

  (:predicates
    (on ?b1 - block ?l - location)
    (holding ?b - block)
  )

  (:action pick-block
    :parameters (
         ?b - block
         ?l - location
     )
    :precondition
        (and
          (not (exists (?b2 - block) (holding ?b2)))
          (not (exists (?b2 - block) (on ?b2 ?b)))
          (on ?b ?l)
    )
    :effect
        (and
            (holding ?b)
            (not (on ?b ?l))
    )
  )

  (:action place-block-on-table
    :parameters (
        ?b - block
        ?t - table
    )
    :precondition
        (and
            (holding ?b)
        )
    :effect
        (and
          (not (holding ?b))
          (on ?b ?t)
        )
  )

  (:action place-block-on-block
    :parameters (
        ?b1 - block
        ?b2 - block
    )
    :precondition
        (and
          (holding ?b1)
          (not (exists (?b3 - block) (on ?b3 ?b2)))
          (not (= ?b1 ?b2))
    )
    :effect
        (and
          (not (holding ?b1))
          (on ?b1 ?b2)
    )
  )
)
