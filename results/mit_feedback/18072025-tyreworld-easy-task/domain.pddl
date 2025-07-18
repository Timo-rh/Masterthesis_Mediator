(define (domain tyreworld)
  (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

  (:types
    tool tire hub nut - object
    wrench jack pump - tool
  )

  (:predicates
    (on_hub ?t - tire ?h - hub)
    (jacked_up ?h - hub)
    (nut_loose ?h - hub)
    (holding ?o)
    (whole ?t - tire)
    (nut_tight ?h - hub)
    (inflated ?t - tire)
    (tire_secured ?h - hub)
    (mounted ?t - tire ?h - hub)
    (hub_lowered ?h - hub)
    (validated ?t - tire ?h - hub)
    (hub_empty ?h - hub)
    (nut_loosened ?h - hub)
  )

  (:action remove_tire
    :parameters (?t - tire ?h - hub)
    :precondition (and
      (on_hub ?t ?h)
      (jacked_up ?h)
      (nut_loosened ?h)
    )
    :effect (and
      (not (on_hub ?t ?h))
      (holding ?t)
      (hub_empty ?h)
    )
  )

  (:action place_tire
    :parameters (?t - tire ?h - hub)
    :precondition (and
      (holding ?t)
      (jacked_up ?h)
      (hub_empty ?h)
    )
    :effect (and
      (on_hub ?t ?h)
      (mounted ?t ?h)
      (not (holding ?t))
      (not (hub_empty ?h))
    )
  )

  (:action tighten_nut
    :parameters (?h - hub ?w - wrench)
    :precondition (and
      (holding ?w)
      (jacked_up ?h)
      (not (hub_empty ?h))
      (nut_loosened ?h)
    )
    :effect (and
      (nut_tight ?h)
      (not (nut_loosened ?h))
      (tire_secured ?h)
    )
  )

  (:action inflate_tire
    :parameters (?t - tire ?p - pump)
    :precondition (and
      (holding ?p)
      (whole ?t)
      (not (inflated ?t))
    )
    :effect (and
      (inflated ?t)
    )
  )

  (:action lower_jack
    :parameters (?h - hub ?j - jack)
    :precondition (and
      (jacked_up ?h)
      (not (hub_empty ?h))
      (holding ?j)
      (nut_tight ?h)
    )
    :effect (and
      (not (jacked_up ?h))
      (hub_lowered ?h)
    )
  )

  (:action validate_replacement
    :parameters (?t - tire ?h - hub)
    :precondition (and
      (mounted ?t ?h)
      (inflated ?t)
      (tire_secured ?h)
      (hub_lowered ?h)
    )
    :effect (and
      (validated ?t ?h)
    )
  )
)