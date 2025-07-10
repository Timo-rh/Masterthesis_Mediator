(define (domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        city location package vehicle - object
        airport storage street - location
        airplane truck - vehicle
    )
    (:predicates
        (at ?obj ?loc - location)
        (in ?pkg - package ?veh - vehicle)
        (in_city ?loc - location ?city - city)
        (in_truck ?pkg - package ?truck - truck))
    (:action drive_truck
        :parameters (?t - truck ?from - location ?to - location ?c - city)
        :precondition (and (at ?t ?from) (in_city ?from ?c) (in_city ?to ?c) (are_different ?from ?to))
        :effect (and (not (at ?t ?from)) (at ?t ?to))
    )
     (:action fly_airplane
        :parameters (?plane - airplane ?from_city - city ?to_city - city)
        :precondition (and (at ?plane ?from_city) (are_different ?from_city ?to_city))
        :effect (and (not (at ?plane ?from_city)) (at ?plane ?to_city))
    )
     (:action load_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?p ?ap) (at ?a ?ap) (not_in ?p ?a))
        :effect (and (in ?p ?a) (not (at ?p ?ap)))
    )
     (:action load_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?p ?l) (at ?t ?l))
        :effect (and (in ?p ?t) (not (at ?p ?l)))
    )
     (:action unload_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?a ?ap) (in ?p ?a))
        :effect (and (not (in ?p ?a)) (at ?p ?ap))
    )
     (:action unload_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?t ?l) (in ?p ?t))
        :effect (and (at ?p ?l) (not (in ?p ?t)))
    )
)