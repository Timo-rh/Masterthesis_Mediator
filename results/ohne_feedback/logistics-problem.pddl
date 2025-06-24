(define (problem logistics-problem)
  (:domain logistics)

  (:objects
    airplane1 - airplane
    ado_airport betar_airport colin_airport duran_airport - airport
    ado_city ado_truck betar_city betar_truck colin_city colin_truck duran_city duran_truck - city
    ado_storage betar_storage - location
    package4 package5 - package
    colin_promenade package2 package3 - promenade
    betar_street package1 - street
  )

  (:init
    (at AdoStorage)
    (at AdoStorage)
    (at AdoStorage)
    (at BetarStorage)
    (at BetarStorage)
    (at AdoStorage)
    (at BetarStorage)
    (at ColinStorage)
    (at DuranStorage)
    (at DuranAirport)
    (in-city Ado)
    (in-city Ado)
    (in-city Betar)
    (in-city Betar)
    (in-city Betar)
    (in-city Colin)
    (in-city Colin)
    (in-city Colin)
    (in-city Duran)
    (in-city Duran)
  )

  (:goal
    (and
      (at bal_street L1)
      (at cli_promenade L2)
      (at cli_promenade L3)
      (at ado_storage L4)
      (at ado_storage L5)
    )
  )
)
