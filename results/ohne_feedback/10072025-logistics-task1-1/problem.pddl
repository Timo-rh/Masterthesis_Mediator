(define (problem task1)
    (:domain logistics)
    (:requirements :conditional-effects :disjunctive-preconditions :equality :negative-preconditions :strips :typing :universal-preconditions)
    (:objects
        plane1 - airplane
        ado_airport betar_airport colin_airport duran_airport - airport
        ado betar colin duran - city
        pkg1 pkg2 pkg3 pkg4 pkg5 - package
        ado_storage betar_storage - storage
        bal_street cli_promenade - street
        ado_truck betar_truck colin_truck duran_truck - truck)
    (:init
        (at ado_truck ado_storage)
        (at betar_truck betar_storage)
        (at colin_truck colin_airport)
        (at duran_truck duran_airport)
        (at pkg1 ado_storage)
        (at pkg2 ado_storage)
        (at pkg3 ado_storage)
        (at pkg4 betar_storage)
        (at pkg5 betar_storage)
        (at plane1 duran_airport)
        (in_city ado_airport ado)
        (in_city ado_storage ado)
        (in_city bal_street betar)
        (in_city betar_airport betar)
        (in_city betar_storage betar)
        (in_city cli_promenade colin)
        (in_city colin_airport colin)
        (in_city duran_airport duran))
    (:goal (and
        (at pkg1 bal_street)
        (at pkg2 cli_promenade)
        (at pkg3 cli_promenade)
        (at pkg4 ado_storage)
        (at pkg5 ado_storage)))
)