(define (problem hard-task)
  (:domain blocksworld)

  (:objects
    red1 - red_block
    red2 - red_block
    blue1 - blue_block
    green1 - green_block
    green2 - green_block
  )

  (:init
    (on_table red1)
    (on blue1 red1)
    (on green1 blue1)
    (clear green1)
    (on_table red2)
    (on green2 red2)
    (clear green2)
    (arm_empty)
  )

  (:goal
    (and
      (on_table red1)
      (on red2 red1)
      (on blue1 red2)
      (on green1 blue1)
      (on green2 green1)
      (arm_empty)
      (clear green2)
    )
  )
)