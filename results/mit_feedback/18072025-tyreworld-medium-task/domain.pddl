(define (domain tyreworld)
  (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

  (:types
    tool car_part location - object
    wrench jack pump - tool
    tyre hub nut - car_part
  )

  (:predicates
    (has ?obj)
    (in_boot ?obj)
    (attached ?t - tyre ?h - hub)
    (fastened ?n - nut ?h - hub)
    (on_ground ?h - hub)
    (jacked_up ?h - hub)
    (loose ?n - nut)
    (tight ?n - nut)
    (flat ?t - tyre)
    (inflated ?t - tyre)
    (at ?obj ?loc - location)
    (tyre_on ?t - tyre ?h - hub)
    (nut_on ?n - nut ?h - hub)
    (has_tyre ?h - hub)
    (not_jacked_up ?h - hub)
  )

  (:action pickup_tool
    :parameters (?t - tool)
    :precondition (in_boot ?t)
    :effect (and (has ?t) (not (in_boot ?t)))
  )

  (:action store_tool
    :parameters (?t - tool)
    :precondition (has ?t)
    :effect (and (in_boot ?t) (not (has ?t)))
  )

  (:action pickup_tyre
    :parameters (?t - tyre)
    :precondition (in_boot ?t)
    :effect (and (has ?t) (not (in_boot ?t)))
  )

  (:action store_tyre
    :parameters (?t - tyre)
    :precondition (has ?t)
    :effect (and (in_boot ?t) (not (has ?t)))
  )

  (:action loosen_nut
    :parameters (?n - nut ?h - hub ?w - wrench)
    :precondition (and
      (has ?w)
      (nut_on ?n ?h)
      (has_tyre ?h)
      (not_jacked_up ?h)
      (tight ?n)
    )
    :effect (and (loose ?n) (not (tight ?n)))
  )

  (:action tighten_nut
    :parameters (?n - nut ?h - hub ?w - wrench)
    :precondition (and
      (has ?w)
      (nut_on ?n ?h)
      (loose ?n)
      (has_tyre ?h)
      (not_jacked_up ?h)
    )
    :effect (and (tight ?n) (not (loose ?n)))
  )

  (:action jack_up_hub
    :parameters (?h - hub ?j - jack)
    :precondition (and
      (has ?j)
      (not_jacked_up ?h)
    )
    :effect (and (jacked_up ?h) (not (not_jacked_up ?h)))
  )

  (:action lower_hub
    :parameters (?h - hub ?j - jack)
    :precondition (and
      (has ?j)
      (jacked_up ?h)
    )
    :effect (and (not_jacked_up ?h) (not (jacked_up ?h)))
  )

  (:action remove_tyre
    :parameters (?t - tyre ?h - hub ?n - nut)
    :precondition (and
      (attached ?t ?h)
      (jacked_up ?h)
      (loose ?n)
      (nut_on ?n ?h)
    )
    :effect (and
      (has ?t)
      (not (attached ?t ?h))
      (not (has_tyre ?h))
    )
  )

  (:action attach_tyre
    :parameters (?t - tyre ?h - hub ?n - nut)
    :precondition (and
      (has ?t)
      (jacked_up ?h)
      (loose ?n)
      (nut_on ?n ?h)
      (not (has_tyre ?h))
    )
    :effect (and
      (attached ?t ?h)
      (has_tyre ?h)
      (not (has ?t))
    )
  )
)