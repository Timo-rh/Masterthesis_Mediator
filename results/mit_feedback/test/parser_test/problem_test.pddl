(define (problem task1)
    (:domain
        logistics
    )
    (:requirements
        :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions
    )
    (:objects
        airplane1 - airplane
        ado_airport betar_airport colin_airport duran_airport - airport
        ado_city betar_city colin_city duran_city - city
        betar_street - location
        package1 package2 package3 package4 package5 - package
        colin_promenade - promenade
        ado_storage betar_storage colin_storage duran_storage - storage
        ado_truck betar_truck colin_truck duran_truck - truck
    )
    (:init
        (at ado_truck ado_storage)
        (at airplane1 duran_airport)
        (at betar_truck betar_storage)
        (at colin_truck colin_storage)
        (at duran_truck duran_storage)
        (at package1 ado_storage)
        (at package2 ado_storage)
        (at package3 ado_storage)
        (at package4 betar_storage)
        (at package5 betar_storage)
        (in_city ado_airport ado_city)
        (in_city ado_storage ado_city)
        (in_city betar_airport betar_city)
        (in_city betar_storage betar_city)
        (in_city betar_street betar_city)
        (in_city colin_airport colin_city)
        (in_city colin_promenade colin_city)
        (in_city colin_storage colin_city)
        (in_city duran_airport duran_city)
        (in_city duran_storage duran_city)
    )
    (:goal
        (and
            (at package1 betar_street)
            (at package2 colin_promenade)
            (at package3 colin_promenade)
            (at package4 ado_storage)
            (at package5 ado_storage)
        )
    )
)