(define (domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:types
        city location package vehicle - object
        airport promenade storage street - location
        airplane truck - vehicle
    )
    (:predicates (at ?p - package ?l - location)  (different ?c1 - city ?c2 - city)  (in ?p - package ?t - vehicle)  (in_city ?l - location ?c - city)  (is_airport ?l - location))
)