(define (domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        city location package vehicle - object
        airport promenade storage street - location
        airplane truck - vehicle
    )
    (:predicates (at ?p ?l - location)  (different ?c1 - city ?c2 - city)  (in ?p ?t - vehicle)  (in_city ?l - location ?c - city)  (is_airport ?l - location))
    (:action drive_truck
        :parameters (?t - truck ?from - location ?to - location ?c - city)
        :precondition (and (at ?t ?from) (in_city ?from ?c) (in_city ?to ?c))
        :effect (and (not (at ?t ?from)) (at ?t ?to))
    )
     (:action fly_airplane
        :parameters (?a - airplane ?from - airport ?to - airport ?from_city - city ?to_city - city)
        :precondition (and (at ?a ?from) (in_city ?from ?from_city) (in_city ?to ?to_city) (is_airport ?from) (is_airport ?to) (different ?from_city ?to_city))
        :effect (and (not (at ?a ?from)) (at ?a ?to))
    )
     (:action load_airplane
        :parameters (?p - package ?a - airplane ?ap - airport)
        :precondition (and (at ?p ?ap) (at ?a ?ap) (not (in ?p ?a)))
        :effect (and (in ?p ?a) (not (at ?p ?ap)))
    )
     (:action load_truck
        :parameters (?p - package ?t - truck ?l - location)
        :precondition (and (at ?p ?l) (at ?t ?l) (not (in ?p ?t)))
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