(define (problem easy-task)
  (:domain blocksworld)

  (:objects
    blue_block - block
    red_block - block
    yellow_block - block
    green_block - block
  )

  (:init
    ; Initial block positions
    (on blue_block red_block)
    (on red_block yellow_block)
    (on_table yellow_block)
    (on_table green_block)

    ; Clear blocks (nothing on top)
    (clear blue_block)
    (clear green_block)

    ; Robot arm state
    (arm_empty)
  )

  (:goal
    (and
      ; Main goal: red block on green block
      (on red_block green_block)

      ; Additional goal constraints for completeness
      (arm_empty)
      (clear red_block)
    )
  )
)