(define (domain household)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

    (:types
        location storage_item kitchenware food robot - object
        container surface - location
        cabinet drawer fridge dish_washer - container
        dining_table - surface
        lunch_box pizza_box - storage_item
        plate bowl pan cutting_board - kitchenware
    )

    (:predicates
        (at ?obj ?loc - location)
        (connected ?l1 - location ?l2 - location)
        (in_on ?item ?container)
        (holding ?robot - robot ?obj)
        (pickupable ?obj)
        (in_storage ?obj ?container - storage_item)
        (opened ?c - container)
        (sliced ?f - food)
        (on_surface ?obj ?s - surface)
        (not_holding_anything ?robot - robot)
    )

    (:action move
        :parameters (?robot - robot ?from - location ?to - location)
        :precondition (and
            (at ?robot ?from)
            (not (= ?from ?to))
            (connected ?from ?to)
        )
        :effect (and
            (not (at ?robot ?from))
            (at ?robot ?to)
        )
    )

    (:action pick_up
        :parameters (?robot - robot ?item - storage_item ?source - location)
        :precondition (and
            (at ?robot ?source)
            (in_on ?item ?source)
            (pickupable ?item)
            (not_holding_anything ?robot)
        )
        :effect (and
            (holding ?robot ?item)
            (not (in_on ?item ?source))
            (not (not_holding_anything ?robot))
        )
    )

    (:action put_down
        :parameters (?robot - robot ?item - storage_item ?target - location)
        :precondition (and
            (at ?robot ?target)
            (holding ?robot ?item)
            (pickupable ?item)
        )
        :effect (and
            (in_on ?item ?target)
            (not (holding ?robot ?item))
            (not_holding_anything ?robot)
        )
    )

    (:action open_container
        :parameters (?c - container ?l - location ?robot - robot)
        :precondition (and
            (at ?robot ?l)
            (at ?c ?l)
            (not (opened ?c))
            (not_holding_anything ?robot)
        )
        :effect (and
            (opened ?c)
        )
    )

    (:action close_container
        :parameters (?c - container ?r - robot)
        :precondition (and
            (at ?r ?c)
            (opened ?c)
            (not_holding_anything ?r)
        )
        :effect (and
            (not (opened ?c))
        )
    )

    (:action slice
        :parameters (?f - food ?s - surface ?robot - robot ?c - cutting_board)
        :precondition (and
            (at ?robot ?s)
            (at ?f ?s)
            (at ?c ?s)
            (not (sliced ?f))
            (not (holding ?robot ?c))
            (pickupable ?c)
        )
        :effect (and
            (sliced ?f)
        )
    )
)