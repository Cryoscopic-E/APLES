import os
from unified_planning.shortcuts import *
from unified_planning.model.metrics import MinimizeActionCosts
from unified_planning.engines import PlanGenerationResultStatus
import custom_types as types
from exporter import create_levels, empty_sheets, export_plan_to_sheet, export_to_excel, get_executed_actions, push_to_gamebus, push_videos_to_gamebus
import fluents
import pandas as pd

from planning_problem import PlanningProblem
get_environment().credits_stream = None
from unified_planning.io import PDDLWriter

excel_data_path = './data/exampleactivities.csv'

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
    csv_data_path = os.path.join(os.path.dirname(__file__), 'data', 'exampleactivities.csv')

    # Create the planning problem
    p = PlanningProblem(csv=csv_data_path, social_score=social, physical_score=physical, cognitive_score=cognitive)

    # print(p)
    with OneshotPlanner(name='lpg', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
        result = planner.solve(p.problem) # type: ignore
        plan = result.plan

        if plan is not None:
            print(plan)
            # assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY
            return plan
        else:
            print("No plan found.")

def main():
    levels = pd.read_csv(level_structure_path)
    empty_sheets()

    current_level_ = 0
    for index, level in levels.iterrows():
        executed_plan = execute_planner(int(level['physical']), int(level['social']), int(level['cognitive']))
        current_level_ = export_plan_to_sheet(current_level_, executed_plan)
    
    create_levels()
    # export_to_excel()
    # push_to_gamebus()


if __name__ == '__main__':
    main()
