(define (domain household)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

    (:types
        location container tableware food - object
        cabinet drawer fridge dining_table dish_washer - location
        lunch_box pizza_box - container
        serving_ware cookware preparation_ware - tableware
        bowl plate - serving_ware
        pan - cookware
        cutting_board - preparation_ware
        fruit vegetable bread - food
    )

    (:predicates
        (at ?obj ?loc - location)
        (holding ?obj)
        (pickupable ?obj)
        (robot_at ?loc - location)
        (in ?item ?container - container)
        (opened ?container - container)
        (empty_gripper)
        (in_on ?obj ?container)
        (sliced ?food - food)
        (location_opened ?loc - location)
    )

    (:action move_robot
        :parameters (?from - location ?to - location)
        :precondition (and
            (robot_at ?from)
            (not (= ?from ?to))
        )
        :effect (and
            (not (robot_at ?from))
            (robot_at ?to)
        )
    )

    (:action open_container
        :parameters (?c - container ?l - location)
        :precondition (and
            (robot_at ?l)
            (in_on ?c ?l)
            (empty_gripper)
            (not (opened ?c))
        )
        :effect (and
            (opened ?c)
        )
    )

    (:action close_container
        :parameters (?c - container ?l - location)
        :precondition (and
            (robot_at ?l)
            (in_on ?c ?l)
            (opened ?c)
            (empty_gripper)
        )
        :effect (and
            (not (opened ?c))
        )
    )

    (:action open_location
        :parameters (?l - location)
        :precondition (and
            (robot_at ?l)
            (not (location_opened ?l))
            (empty_gripper)
        )
        :effect (and
            (location_opened ?l)
        )
    )

    (:action close_location
        :parameters (?l - location)
        :precondition (and
            (robot_at ?l)
            (location_opened ?l)
            (empty_gripper)
        )
        :effect (and
            (not (location_opened ?l))
        )
    )

    (:action pickup
        :parameters (?obj ?loc - location)
        :precondition (and
            (robot_at ?loc)
            (in_on ?obj ?loc)
            (pickupable ?obj)
            (empty_gripper)
        )
        :effect (and
            (holding ?obj)
            (not (in_on ?obj ?loc))
            (not (empty_gripper))
        )
    )

    (:action putdown
        :parameters (?obj ?loc - location)
        :precondition (and
            (holding ?obj)
            (robot_at ?loc)
        )
        :effect (and
            (not (holding ?obj))
            (in_on ?obj ?loc)
            (empty_gripper)
        )
    )

    (:action get_from_container
        :parameters (?item ?container - container ?location - location)
        :precondition (and
            (robot_at ?location)
            (in_on ?container ?location)
            (in ?item ?container)
            (opened ?container)
            (empty_gripper)
        )
        :effect (and
            (holding ?item)
            (not (in ?item ?container))
            (not (empty_gripper))
        )
    )

    (:action put_in_container
        :parameters (?obj  ?container - container ?loc - location)
        :precondition (and
            (robot_at ?loc)
            (in_on ?container ?loc)
            (holding ?obj)
            (opened ?container)
        )
        :effect (and
            (in ?obj ?container)
            (not (holding ?obj))
            (empty_gripper)
        )
    )

    (:action slice
        :parameters (?f - food ?c - cutting_board ?l - location)
        :precondition (and
            (robot_at ?l)
            (in_on ?f ?l)
            (in_on ?c ?l)
            (empty_gripper)
            (not (sliced ?f))
            (pickupable ?c)
        )
        :effect (and
            (sliced ?f)
        )
    )
)