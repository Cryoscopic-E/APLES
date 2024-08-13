(define (domain health-domain)
 (:requirements :strips :typing :negative-preconditions :equality :numeric-fluents :action-costs)
 (:types
    activity difficulty - object
    physical_0 social_0 - activity
 )
 (:predicates (candoactivitytype ?activitytype - activity))
 (:functions (difficulty_lvl ?d - difficulty) (difficulty_lvl_physical ?d - difficulty) (difficulty_lvl_social ?d - difficulty) (cost_put_on_your_walking_shoes_and_take_a_picture_of_them_) (cost_take_a_15_minute_walk_without_stopping_) (cost_run_500_km_) (total-cost))
 (:action tutorial_video
  :parameters ( ?activity_type - activity ?d - difficulty)
  :precondition (and (not (candoactivitytype ?activity_type)))
  :effect (and (candoactivitytype ?activity_type) (increase (difficulty_lvl ?d) 1) (increase (total-cost) 0)))
 (:action put_on_your_walking_shoes_and_take_a_picture_of_them_
  :parameters ( ?d - difficulty ?atype - physical_0)
  :precondition (and (candoactivitytype ?atype))
  :effect (and (increase (difficulty_lvl_physical ?d) 2) (increase (total-cost) 9)))
 (:action take_a_15_minute_walk_without_stopping_
  :parameters ( ?d - difficulty ?atype - physical_0)
  :precondition (and (candoactivitytype ?atype))
  :effect (and (increase (difficulty_lvl_physical ?d) 2) (increase (total-cost) 7)))
 (:action run_500_km_
  :parameters ( ?d - difficulty ?atype - physical_0)
  :precondition (and (candoactivitytype ?atype))
  :effect (and (increase (difficulty_lvl_physical ?d) 2) (increase (total-cost) 7)))
)
