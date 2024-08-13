(define (problem health-problem)
 (:domain health-domain)
 (:objects
   counter - difficulty
   physical - physical_0
   social - social_0
 )
 (:init (= (difficulty_lvl counter) 0) (= (difficulty_lvl_physical counter) 0) (= (difficulty_lvl_social counter) 0) (= (total-cost) 0))
 (:goal (and (= (difficulty_lvl_physical counter) 4)))
 (:metric minimize (total-cost))
)
