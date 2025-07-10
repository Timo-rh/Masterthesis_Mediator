(define (domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        city location package vehicle - object
        airport storage street - location
        airplane truck - vehicle
    )
    (:predicates (at ?obj ?loc - location)  (in ?pkg - package ?veh - vehicle)  (in_city ?loc - location ?city - city)  (in_truck ?pkg - package ?truck - truck))
    (:action drive_truck
        :parameters (?truck - truck ?from - location ?to - location ?city - city)
        :precondition (and (at ?truck ?from) (in_city ?from ?city) (in_city ?to ?city))
        :effect (and (not (at ?truck ?from)) (at ?truck ?to))
    )
     (:action fly_airplane
        :parameters (?a - airplane ?from_city - city ?to_city - city)
        :precondition (and (at ?a ?from_city) (are_different ?from_city ?to_city))
        :effect (and (not (at ?a ?from_city)) (at ?a ?to_city))
    )
     (:action load_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?p ?ap) (at ?a ?ap))
        :effect (and (not (at ?p ?ap)) (in ?p ?a))
    )
     (:action load_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?p ?l) (at ?t ?l))
        :effect (and (not (at ?p ?l)) (in ?p ?t))
    )
     (:action unload_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (in ?p ?a) (at ?a ?ap))
        :effect (and (not (in ?p ?a)) (at ?p ?ap))
    )
     (:action unload_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (in ?p ?t) (at ?t ?l))
        :effect (and (not (in ?p ?t)) (at ?p ?l))
    )
)