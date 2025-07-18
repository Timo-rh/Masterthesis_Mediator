(define (domain household)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)

    (:types
        location movable_object robot - object
        carpet container furniture burner - location
        appliance book cleaning_tool cookware dishware food storage_container utensil - movable_object
    )

    (:predicates
        (at ?obj ?loc - location)
        (food_in_cookware ?food - food ?cookware - cookware)
        (holding ?r - robot ?obj)
        (in_on ?obj ?container)
        (is_cookware ?obj)
        (is_stove_burner ?loc - location)
        (on ?obj ?surface - location)
        (pickupable ?obj)
        (turned_on ?a - appliance)
        (is_clean ?obj)
        (is_empty ?burner - location)
        (gripper_empty ?r - robot)
        (is_opened ?container)
        (is_sliced ?food - food)
        (has_empty_dust_bin ?vacuum - cleaning_tool)
    )

    (:action place_food_in_cookware
        :parameters (?robot - robot ?food - food ?cookware - cookware ?loc - location)
        :precondition (and (at ?robot ?loc) (at ?cookware ?loc) (holding ?robot ?food) (pickupable ?food))
        :effect (and (food_in_cookware ?food ?cookware) (not (holding ?robot ?food)) (gripper_empty ?robot))
    )

    (:action place_on_burner
        :parameters (?cookware - cookware ?burner - location ?robot - robot)
        :precondition (and (holding ?robot ?cookware) (at ?robot ?burner) (is_stove_burner ?burner) (is_empty ?burner))
        :effect (and (not (holding ?robot ?cookware)) (on ?cookware ?burner) (gripper_empty ?robot) (not (is_empty ?burner)))
    )

    (:action turn_off
        :parameters (?r - robot ?a - appliance ?l - location)
        :precondition (and (at ?r ?l) (at ?a ?l) (turned_on ?a) (gripper_empty ?r))
        :effect (not (turned_on ?a))
    )

    (:action turn_on_burner
        :parameters (?r - robot ?burner - location)
        :precondition (and (at ?r ?burner) (is_stove_burner ?burner) (gripper_empty ?r))
        :effect (turned_on ?burner)
    )

    (:action pick_up
        :parameters (?robot - robot ?obj - movable_object ?loc - location)
        :precondition (and (at ?robot ?loc) (in_on ?obj ?loc) (pickupable ?obj) (gripper_empty ?robot))
        :effect (and (holding ?robot ?obj) (not (in_on ?obj ?loc)) (not (gripper_empty ?robot)))
    )

    (:action put_down
        :parameters (?robot - robot ?obj - movable_object ?loc - location)
        :precondition (and (at ?robot ?loc) (holding ?robot ?obj))
        :effect (and (in_on ?obj ?loc) (not (holding ?robot ?obj)) (gripper_empty ?robot))
    )

    (:action move
        :parameters (?robot - robot ?from - location ?to - location)
        :precondition (at ?robot ?from)
        :effect (and (not (at ?robot ?from)) (at ?robot ?to))
    )

    (:action open_container
        :parameters (?robot - robot ?container - container ?loc - location)
        :precondition (and (at ?robot ?loc) (in_on ?container ?loc) (not (is_opened ?container)) (gripper_empty ?robot))
        :effect (is_opened ?container)
    )
)