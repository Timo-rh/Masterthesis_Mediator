(define (domain tyreworld)
  (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

  (:types
    hub wheel nut trunk tool - object
    wrench jack pump - tool
  )

  (:predicates
    (raised ?h - hub)
    (holding ?t - tool)
    (in_trunk ?o)
    (trunk_open ?t - trunk)
    (attached ?w - wheel ?h - hub)
    (loose ?n - nut)
    (tight ?n - nut)
    (has_nut ?h - hub ?n - nut)
    (uninflated ?w - wheel)
    (inflated ?w - wheel)
    (verified ?w - wheel ?h - hub)
    (lowered ?h - hub)
    (holding_wheel ?w - wheel)
    (has_wheel ?h - hub)
    (no_wheel ?h - hub)
  )

  (:action open_trunk
    :parameters (?t - trunk)
    :precondition (not (trunk_open ?t))
    :effect (trunk_open ?t)
  )

  (:action close_trunk
    :parameters (?t - trunk)
    :precondition (trunk_open ?t)
    :effect (not (trunk_open ?t))
  )

  (:action take_from_trunk
    :parameters (?obj  ?t - trunk)
    :precondition (and (trunk_open ?t) (in_trunk ?obj))
    :effect (and (holding ?obj) (not (in_trunk ?obj)))
  )

  (:action put_in_trunk
    :parameters (?o  ?t - trunk)
    :precondition (and (trunk_open ?t) (holding ?o))
    :effect (and (in_trunk ?o) (not (holding ?o)))
  )

  (:action loosen_nut
    :parameters (?h - hub ?n - nut ?w - wrench)
    :precondition (and (has_nut ?h ?n) (tight ?n) (lowered ?h) (has_wheel ?h) (holding ?w))
    :effect (and (loose ?n) (not (tight ?n)))
  )

  (:action tighten_nut
    :parameters (?h - hub ?n - nut ?w - wrench)
    :precondition (and (has_nut ?h ?n) (loose ?n) (lowered ?h) (has_wheel ?h) (holding ?w))
    :effect (and (tight ?n) (not (loose ?n)))
  )

  (:action jack_up_hub
    :parameters (?h - hub ?j - jack)
    :precondition (and (holding ?j) (lowered ?h))
    :effect (and (raised ?h) (not (lowered ?h)))
  )

  (:action lower_hub
    :parameters (?h - hub ?j - jack)
    :precondition (and (holding ?j) (raised ?h))
    :effect (and (lowered ?h) (not (raised ?h)))
  )

  (:action remove_wheel
    :parameters (?h - hub ?w - wheel ?n - nut)
    :precondition (and (raised ?h) (attached ?w ?h) (has_nut ?h ?n) (loose ?n))
    :effect (and (holding_wheel ?w) (not (attached ?w ?h)) (no_wheel ?h) (not (has_wheel ?h)))
  )

  (:action attach_wheel
    :parameters (?h - hub ?w - wheel ?n - nut)
    :precondition (and (raised ?h) (no_wheel ?h) (has_nut ?h ?n) (loose ?n) (holding_wheel ?w) (inflated ?w))
    :effect (and (attached ?w ?h) (not (holding_wheel ?w)) (has_wheel ?h) (not (no_wheel ?h)))
  )

  (:action inflate_wheel
    :parameters (?w - wheel ?p - pump)
    :precondition (and (holding ?p) (uninflated ?w))
    :effect (and (inflated ?w) (not (uninflated ?w)))
  )

  (:action verify_wheel_attachment
    :parameters (?h - hub ?w - wheel)
    :precondition (and (raised ?h) (attached ?w ?h))
    :effect (verified ?w ?h)
  )
)