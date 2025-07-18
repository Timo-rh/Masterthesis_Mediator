(define (domain household)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

    (:types
        location robot small_item - object
        storage_location surface_location - location
        appliance book container food tool - small_item
        cabinet drawer fridge - storage_location
        countertop dining_table side_table - surface_location
    )

    (:predicates
        (at ?obj ?loc - location)
        (holding ?r ?item)
        (is_on ?app - appliance)
        (opened ?s - storage_location)
        (pickupable ?item)
        (gripper_empty ?r - robot)
        (in_on ?item - small_item ?loc - location)
        (turned_on ?app - appliance)
        (turned_off ?app - appliance)
    )

    (:action turn_on
        :parameters (?r - robot ?a - appliance ?l - location)
        :precondition (and (at ?r ?l) (at ?a ?l) (turned_off ?a) (gripper_empty ?r))
        :effect (and (turned_on ?a) (not (turned_off ?a)))
    )

    (:action turn_off
        :parameters (?r - robot ?a - appliance ?l - location)
        :precondition (and (at ?r ?l) (at ?a ?l) (turned_on ?a) (gripper_empty ?r))
        :effect (and (turned_off ?a) (not (turned_on ?a)))
    )

    (:action close_storage
        :parameters (?r - robot ?s - storage_location)
        :precondition (and (at ?r ?s) (opened ?s) (gripper_empty ?r))
        :effect (not (opened ?s))
    )

    (:action move_to
        :parameters (?robot - robot ?from - location ?to - location)
        :precondition (and (at ?robot ?from))
        :effect (and (not (at ?robot ?from)) (at ?robot ?to))
    )

    (:action open_storage
        :parameters (?s - storage_location ?r - robot)
        :precondition (and (at ?r ?s) (not (opened ?s)) (gripper_empty ?r))
        :effect (and (opened ?s))
    )

    (:action pick_up
        :parameters (?robot - robot ?item - small_item ?location - location)
        :precondition (and (at ?robot ?location) (at ?item ?location) (pickupable ?item) (gripper_empty ?robot))
        :effect (and (not (at ?item ?location)) (not (gripper_empty ?robot)) (holding ?robot ?item))
    )

    (:action put_down
        :parameters (?robot - robot ?item - small_item ?location - location)
        :precondition (and (at ?robot ?location) (holding ?robot ?item))
        :effect (and (at ?item ?location) (gripper_empty ?robot) (not (holding ?robot ?item)))
    )
)