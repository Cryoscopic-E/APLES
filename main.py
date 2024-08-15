from unified_planning.shortcuts import *
from unified_planning.model.metrics import MinimizeActionCosts
from unified_planning.engines import PlanGenerationResultStatus
from activity_class import gen_activity_from_data
import custom_types as types
from exporter import empty_sheets, export_plan_to_sheet, export_to_excel, get_executed_actions, push_to_gamebus
import fluents
import pandas as pd
get_environment().credits_stream = None
from unified_planning.io import PDDLWriter

# excel_data_path = './data/exampleactivities.csv'
excel_data_path = './data/example.csv'

level_structure_path = './data/level_structure.csv'
def fluents_actions_cost(all_actions):
    fluents = []
    for a in all_actions:
        # replace spaces with underscores
        a = a.replace(' ', '_')
        fluents.append(Fluent('cost_' + a, IntType()))
    return fluents


def problem(all_actions, physical = 0, social =0, cognitive =0):
    tutorial_action = create_tutorial_action()

    p = Problem('health')

    p.add_fluent(fluents.can_do_activity_type, default_initial_value=False)
    p.add_fluent(fluents.difficulty_lvl, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_physical, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_social, default_initial_value=0)
    p.add_fluent(fluents.difficulty_lvl_cognitive, default_initial_value=0)

    # get list of all actions names
    all_actions_names = [a.name for a in all_actions]

    f = fluents_actions_cost(all_actions_names)
    for fl in f:
        p.add_fluent(fl, default_initial_value=0)


    physical_act_type = Object('physical', types.Physical)
    social_act_type = Object('social', types.Social)
    cognitive_act_type = Object('cognitive', types.Cognitive)

    diff = Object('counter', types.Difficulty)
    p.add_action(tutorial_action)
    p.add_actions(all_actions)
    
    p.add_object(diff)
    p.add_object(physical_act_type)
    p.add_object(social_act_type)
    p.add_object(cognitive_act_type)

    p.add_goal(GE(fluents.difficulty_lvl_physical(diff), physical))
    p.add_goal(GE(fluents.difficulty_lvl_social(diff), social))
    p.add_goal(GE(fluents.difficulty_lvl_cognitive(diff), cognitive))

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

def execute_planner(physical, social, cognitive):
    with OneshotPlanner(name='lpg', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
        all_actions = gen_activity_from_data(excel_data_path)
        planning_problem = problem(all_actions, physical, social, cognitive)
        planning_problem = update_costs([], planning_problem)

        # writer = PDDLWriter(planning_problem)
        # writer.write_domain('./domain.pddl')
        # writer.write_problem('./problem.pddl')

        result = planner.solve(planning_problem)
        plan = result.plan
        # print(planning_problem)
        if plan is not None:
            print(plan)
            update_costs(get_executed_actions(plan))
            # assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY

            return plan
        else:
            print("No plan found.")

def main():
    levels = pd.read_csv(level_structure_path)
    empty_sheets()

    for index, level in levels.iterrows():
        executed_plan = execute_planner(int(level['physical']), int(level['social']), int(level['cognitive']))
        export_plan_to_sheet(executed_plan)
    
    export_to_excel()
    push_to_gamebus()



if __name__ == '__main__':
    main()
