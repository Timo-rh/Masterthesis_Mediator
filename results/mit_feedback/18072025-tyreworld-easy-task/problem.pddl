(define (problem easy-task)
  (:domain tyreworld)

  (:objects
    wrench1 - wrench
    jack1 - jack
    pump1 - pump
    flat_tire - tire
    spare_tire - tire
    hub1 - hub
    nut1 - nut
  )

  (:init
    (holding wrench1)
    (holding jack1)
    (holding pump1)
    (holding spare_tire)
    (whole spare_tire)
    (jacked_up hub1)
    (nut_loose hub1)
    (nut_loosened hub1)
    (mounted flat_tire hub1)
    (on_hub flat_tire hub1)
  )

  (:goal
    (and
      (mounted spare_tire hub1)
      (inflated spare_tire)
      (tire_secured hub1)
      (hub_lowered hub1)
      (validated spare_tire hub1)
    )
  )
)