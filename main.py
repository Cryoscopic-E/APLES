import random
import string
from unified_planning.shortcuts import *
from unified_planning.model.metrics import MinimizeActionCosts
from unified_planning.engines import PlanGenerationResultStatus
from activity_class import gen_activity_from_data
import custom_types as types
import fluents
import pandas as pd
get_environment().credits_stream = None
from unified_planning.io import PDDLWriter

# excel_data_path = './data/exampleactivities.csv'
excel_data_path = './data/example.csv'
sheet_data_path = './data/sheet1.csv' 

def fluents_actions_cost(all_actions):
    fluents = []
    for a in all_actions:
        # replace spaces with underscores
        a = a.replace(' ', '_')
        fluents.append(Fluent('cost_' + a, IntType()))
    return fluents


def problem(all_actions):
    tutorial_action = create_tutorial_action()

    p = Problem('health')

    p.add_fluent(fluents.can_do_activity_type, default_initial_value=False)
    p.add_fluent(fluents.difficulty_lvl, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_physical, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_social, default_initial_value=0)

    # get list of all actions names
    all_actions_names = [a.name for a in all_actions]

    f = fluents_actions_cost(all_actions_names)
    for fl in f:
        p.add_fluent(fl, default_initial_value=0)


    physical_act_type = Object('physical', types.Physical)
    social_act_type = Object('social', types.Social)

    diff = Object('counter', types.Difficulty)
    p.add_action(tutorial_action)
    p.add_actions(all_actions)
    
    p.add_object(diff)
    p.add_object(physical_act_type)
    p.add_object(social_act_type)

    p.add_goal(Equals(fluents.difficulty_lvl_physical(diff), 4))
    # p.add_goal(Equals(fluents.difficulty_lvl_social(diff), 5))

    # print(p)
    return p

def update_costs(executed_actions, problem=None):
    all_actions = gen_activity_from_data(excel_data_path)
    tutorial_action = create_tutorial_action()
    cost_dictionary = {}
    cost_dictionary.update({tutorial_action: 0})
    if len(executed_actions) > 0:
        df = pd.read_csv(excel_data_path)
        for a in all_actions:
            for ea in executed_actions:
                if a.name == ea:
                    df.loc[df['Activities'] == a.name, 'CurrentCost'] = df.loc[df['Activities'] == a.name, 'CurrentCost'] + df.loc[df['Activities'] == a.name, 'CostIncrease']
                    cost_dictionary.update({a: int(df.loc[df['Activities'] == a.name, 'CurrentCost'].iloc[0])})
        df.to_csv(excel_data_path, index=False)

    df = pd.read_csv(excel_data_path)
    for a in all_actions:

        cost_dictionary.update({a: int(df.loc[df['Activities'] == a.name, 'CurrentCost'].iloc[0])})

    if problem:
        problem.add_quality_metric(MinimizeActionCosts(cost_dictionary))
        return problem

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
            action_name = line
            if "tutorial" not in action_name:
                action_name = action_name.split('(')[0] 
            executed_actions.append(action_name)
    return executed_actions

def append_row_to_sheet(name, frequency):
    df = pd.read_csv(sheet_data_path)
    rand_secret = ''.join(random.choices(string.ascii_lowercase +
                                string.digits, k=random.randint(10,50)))
    new_row = {
        'challenge': 242,
        'name': name,
        'description': '',
        'image': 'https://campaigns.healthyw8.gamebus.eu/api/media/HW8-immutable/5ff935d3-d0ae-4dce-bfcd-d2f71bf2ca63.jpeg',
        'video': '',
        'h5p_slug': '',
        'max_times_fired': frequency,
        'min_days_between_fire': 7,
        'activityscheme_default': 'GENERAL_ACTIVITY',
        'activityschemes_allowed': 'GENERAL_ACTIVITY',
        'image_required': 1,
        'conditions': '[SECRET, EQUAL, {}]'.format(rand_secret),
        'points': 1,
        'dataproviders': 'GameBus Studio'
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(sheet_data_path, index=False)

def export_plan_to_sheet(p):
    actions = get_executed_actions(p)

    df_actions = pd.read_csv(excel_data_path)
    for a in actions:
        match = df_actions[df_actions['Activities'] == a]
        if not match.empty:
            activityname = match['Activities'].values[0]
            frequency = match['Frequency'].values[0]
            type_ = match['Type'].values[0]
            append_row_to_sheet(activityname, frequency)

def main():
    with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:

        all_actions = gen_activity_from_data(excel_data_path)
        planning_problem = problem(all_actions)
        planning_problem = update_costs([], planning_problem)
        # writer = PDDLWriter(planning_problem)
        # writer.write_domain('./domain.pddl')
        # writer.write_problem('./problem.pddl')

        result = planner.solve(planning_problem)
        plan = result.plan
        print(planning_problem)
        if plan is not None:
            # print(plan)
            update_costs(get_executed_actions(plan))
            # assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY

            # export_plan_to_sheet(plan)
        else:
            print("No plan found.")


if __name__ == '__main__':
    main()
