from unified_planning.shortcuts import *
from activity_class import ActivityClass
from activity_class import gen_activity_from_data
import custom_types as types
import fluents
import pandas as pd
get_environment().credits_stream = None

def problem(all_actions):
    tutorial_action = create_tutorial_action()

    p = Problem('health')

    p.add_fluent(fluents.can_do_activity_type, default_initial_value=False)
    p.add_fluent(fluents.difficulty_lvl, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_physical, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_social, default_initial_value=0)

    physical_act_type = Object('physical', types.Physical)
    social_act_type = Object('social', types.Social)

    diff = Object('counter', types.Difficulty)
    p.add_action(tutorial_action)
    p.add_actions(all_actions)
    
    p.add_object(diff)
    p.add_object(physical_act_type)
    p.add_object(social_act_type)

    p.add_goal(GE(fluents.difficulty_lvl_physical(diff), 3))
    p.add_goal(Equals(fluents.difficulty_lvl_social(diff), 5))

    # print(p)
    return p

def update_costs(executed_actions):
    all_actions = gen_activity_from_data('./data/exampleactivities.csv')
    cost_dictionary = {}
    if len(executed_actions) > 0:
        df = pd.read_csv('data/exampleactivities.csv')
        for a in all_actions:
            for ea in executed_actions:
                if a.name == ea:
                    cost_dictionary.update({a: (a.cost + 1)})
                    df.loc[df['Activities'] == a.name, 'CurrentCost'] = df.loc[df['Activities'] == a.name, 'CurrentCost'] + df.loc[df['Activities'] == a.name, 'CostIncrease']
        df.to_csv('data/exampleactivities.csv', index=False)

    df = pd.read_csv('data/exampleactivities.csv')
    for a in all_actions:
        cost_dictionary.update({ a: a.cost})
    up.model.metrics.MinimizeActionCosts(cost_dictionary)

def create_tutorial_action():
    tutorial_action = InstantaneousAction('tutorial_video', activity_type=types.Activity, d=types.Difficulty)
    # parameters
    activity_type = tutorial_action.parameter('activity_type')
    difficulty = tutorial_action.parameter('d')
    # preconditions
    tutorial_action.add_precondition(Not(fluents.can_do_activity_type(activity_type)))
    # effects
    tutorial_action.add_effect(fluents.can_do_activity_type(activity_type), True)
    tutorial_action.add_increase_effect(fluents.difficulty_lvl(difficulty), 1)
    return tutorial_action

def get_executed_actions(plan):
    executed_actions = []
    lines = str(plan).splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.endswith(':'):
            action_name = line.split('(')[0] 
            executed_actions.append(action_name)
    return executed_actions

def main():
    with OneshotPlanner(name='lpg') as planner:
        update_costs([])
        all_actions = gen_activity_from_data('./data/exampleactivities.csv')
        result = planner.solve(problem(all_actions))
        plan = result.plan
        if plan is not None:
            print(plan)
            update_costs(get_executed_actions(plan))
        else:
            print("No plan found.")


if __name__ == '__main__':
    main()
