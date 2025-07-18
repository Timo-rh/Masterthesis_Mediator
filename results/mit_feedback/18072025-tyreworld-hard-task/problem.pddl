(define (problem hard-task)
  (:domain tyreworld)

  (:objects
    trunk1 - trunk
    hub_fl hub_bl - hub
    wheel_bl_flat wheel_spare - wheel
    nut_fl nut_bl - nut
    wrench1 - wrench
    jack1 - jack
    pump1 - pump
  )

  (:init
    (raised hub_fl)
    (lowered hub_bl)
    (has_nut hub_fl nut_fl)
    (has_nut hub_bl nut_bl)
    (attached wheel_bl_flat hub_bl)
    (has_wheel hub_bl)
    (no_wheel hub_fl)
    (tight nut_bl)
    (tight nut_fl)
    (in_trunk wheel_spare)
    (in_trunk wrench1)
    (in_trunk jack1)
    (in_trunk pump1)
    (uninflated wheel_spare)
  )

  (:goal
    (and
      (attached wheel_spare hub_bl)
      (inflated wheel_spare)
      (verified wheel_spare hub_bl)
      (in_trunk wheel_bl_flat)
      (in_trunk wrench1)
      (in_trunk jack1)
      (in_trunk pump1)
      (lowered hub_bl)
      (tight nut_bl)
    )
  )
)