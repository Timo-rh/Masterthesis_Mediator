(define (problem medium-task)
  (:domain tyreworld)

  (:objects
    wrench1 - wrench
    jack1 - jack
    pump1 - pump
    flat_tyre - tyre
    spare_tyre - tyre
    bl_hub - hub
    bl_nut - nut
    robot - location
    boot - location
  )

  (:init
    (at wrench1 robot)
    (has wrench1)
    (in_boot jack1)
    (in_boot pump1)
    (in_boot spare_tyre)
    (attached flat_tyre bl_hub)
    (fastened bl_nut bl_hub)
    (nut_on bl_nut bl_hub)
    (has_tyre bl_hub)
    (not_jacked_up bl_hub)
    (on_ground bl_hub)
    (tight bl_nut)
    (flat flat_tyre)
    (inflated spare_tyre)
  )

  (:goal
    (and
      (attached spare_tyre bl_hub)
      (tight bl_nut)
      (not_jacked_up bl_hub)
      (on_ground bl_hub)
      (in_boot flat_tyre)
    )
  )
)