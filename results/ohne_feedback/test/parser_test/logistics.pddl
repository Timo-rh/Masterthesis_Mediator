(define (domain logistics)
    (:requirements
        :strips :typing :equality :negative−preconditions :disjunctive−preconditions  :universal−preconditions :conditional−effects
        )

    (:types
        city - object ; A city contains locations and has its own truck and airport.
        package - object ; An item that needs to be transported.
        location - object ;  A place within a city that can contain packages.
        storage - location ;
        street - location ;
        promenade - location ;
        airport - location ;
        vehicle - object ; A means of transport
        truck - vehicle ;
        airplane - vehicle ;
    )

    (:predicates
        (at ?p - package ?l - location)
        (at ?t - truck ?l - location)
        (in ?p - package ?t - truck)
        (at ?p - package ?ap - airport)
        (at ?a - airplane ?ap - airport)
        (in ?p - package ?a - airplane)
        (at ?
