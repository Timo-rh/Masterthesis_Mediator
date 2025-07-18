(define (problem hard-task)
    (:domain household)

    (:objects
        cabinet_1 cabinet_2 cabinet_3 cabinet_4 - cabinet
        drawer_1 drawer_2 drawer_4 - drawer
        fridge_1 - fridge
        dining_table_1 - dining_table
        dish_washer_1 - dish_washer
        bowl_1 bowl_2 - bowl
        plate_1 plate_2 - plate
        pan_1 pan_2 - pan
        cutting_board_1 - cutting_board
        lunch_box_1 lunch_box_2 - lunch_box
        pizza_box_1 - pizza_box
        apple_1 apple_2 - fruit
        banana_1 - fruit
        potato_1 - vegetable
        pizza_1 - food
        toast_1 - bread
    )

    (:init
        (location_opened fridge_1)
        (robot_at cabinet_2)
        (empty_gripper)
        (in_on bowl_1 cabinet_2)
        (in_on bowl_2 drawer_2)
        (in_on plate_1 dining_table_1)
        (in_on plate_2 dish_washer_1)
        (in_on pan_1 cabinet_3)
        (in_on pan_2 cabinet_4)
        (in_on lunch_box_1 fridge_1)
        (in_on lunch_box_2 fridge_1)
        (in_on pizza_box_1 drawer_4)
        (in_on cutting_board_1 drawer_1)
        (in_on apple_1 cabinet_1)
        (in_on apple_2 fridge_1)
        (in_on banana_1 cabinet_2)
        (in pizza_1 lunch_box_1)
        (in toast_1 lunch_box_1)
        (in potato_1 lunch_box_2)
        (not (opened lunch_box_1))
        (not (opened lunch_box_2))
        (not (opened pizza_box_1))
        (pickupable cutting_board_1)
        (pickupable potato_1)
        (not (sliced apple_1))
        (not (sliced apple_2))
        (not (sliced banana_1))
        (not (sliced potato_1))
        (not (sliced toast_1))
    )

    (:goal (and
        (in_on potato_1 plate_1)
        (not (location_opened fridge_1))
    ))
)