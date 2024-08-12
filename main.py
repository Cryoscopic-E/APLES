from unified_planning.shortcuts import *
from activity_class import ActivityClass

import custom_types as types
import fluents

get_environment().credits_stream = None

def problem():
    tutorial_action = InstantaneousAction('tutorial_video', activity_type=types.Activity, d=types.Difficulty)
    # parameters
    activity_type = tutorial_action.parameter('activity_type')
    difficulty = tutorial_action.parameter('d')
    # preconditions
    tutorial_action.add_precondition(Not(fluents.can_do_activity_type(activity_type)))
    # effects
    tutorial_action.add_effect(fluents.can_do_activity_type(activity_type), True)
    tutorial_action.add_increase_effect(fluents.difficulty_lvl(difficulty), 1)


    activities = [{'name': 'running', 'score': 1, 'activity_type': 'physical'}, {'name': 'call friend', 'score': 1, 'activity_type':'social'}]
    actions = []
    for a in activities:
        actions.append(ActivityClass(a['name'], a['score'], a['activity_type']))
    p = Problem('health')

    p.add_fluent(fluents.can_do_activity_type, default_initial_value=False)
    p.add_fluent(fluents.difficulty_lvl, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_physical, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_social, default_initial_value=0)

    physical_act_type = Object('physical', types.Physical)
    social_act_type = Object('social', types.Social)

    diff = Object('counter', types.Difficulty)

    p.add_action(tutorial_action)
    p.add_actions(actions)

    p.add_object(diff)
    p.add_object(physical_act_type)
    p.add_object(social_act_type)

    p.add_goal(Equals(fluents.difficulty_lvl_physical(diff), 3))
    p.add_goal(Equals(fluents.difficulty_lvl_social(diff), 5))

    print(p)
    return p


def main():
    with OneshotPlanner(name='lpg') as planner:
        result = planner.solve(problem())
        plan = result.plan
        if plan is not None:
            print(plan)
        else:
            print("No plan found.")


if __name__ == '__main__':
    main()
