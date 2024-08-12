from unified_planning.shortcuts import *
from activity_class import ActivityClass
from activity_class import gen_activity_from_data
import custom_types as types
import fluents

get_environment().credits_stream = None

def problem():
    tutorial_action = InstantaneousAction('tutorial_video', activity=types.Activity, d=types.Difficulty)
    # parameters
    activity = tutorial_action.parameter('activity')
    difficulty = tutorial_action.parameter('d')
    # preconditions
    tutorial_action.add_precondition(Not(fluents.can_do_activity(activity)))
    # effects
    tutorial_action.add_effect(fluents.can_do_activity(activity), True)
    tutorial_action.add_increase_effect(fluents.difficulty_lvl(difficulty), 1)

    activities = [{'name': 'running', 'score': 3}, {'name': 'walking', 'score': 1}]
    actions = []
    for a in activities:
        actions.append(ActivityClass(a['name'], a['score']))
    p = Problem('health')

    p.add_fluent(fluents.can_do_activity, default_initial_value=False)
    p.add_fluent(fluents.difficulty_lvl, default_initial_value=0)

    running_activity = Object('running_act', types.Physical)
    diff = Object('counter', types.Difficulty)

    p.add_action(tutorial_action)
    p.add_actions(gen_activity_from_data('./data/exampleactivities.csv'))

    p.add_object(running_activity)
    p.add_object(diff)
    p.add_goal(Equals(fluents.difficulty_lvl(diff), 3))
    print(p)
    return p


def main():
    with OneshotPlanner(name='enhsp') as planner:
        p = problem()
        result = planner.solve(p)
        plan = result.plan
        if plan is not None:
            print(plan)
        else:
            print("No plan found.")


if __name__ == '__main__':
    main()
