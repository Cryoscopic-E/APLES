import os
import time
from unified_planning.shortcuts import *
from unified_planning.model.metrics import MinimizeActionCosts
from unified_planning.engines import PlanGenerationResultStatus
from .exporter import create_levels, empty_sheets, export_plan_to_sheet, export_to_excel, get_executed_actions, parse_video_url, push_to_gamebus, push_videos_to_gamebus, reset_fluents_csv
from unified_planning.shortcuts import Fluent, IntType, Problem, UserType, InstantaneousAction, MinimizeActionCosts, Object, OneshotPlanner
import pandas as pd

from .planning_problem import PlanningProblem
get_environment().credits_stream = None
from unified_planning.io import PDDLWriter

csv_data_path = os.path.join(os.path.dirname(__file__), 'data', 'exampleactivities.csv')
csv_fluents_path = os.path.join(os.path.dirname(__file__), 'data', 'fluents.csv')
level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure.csv')

def create_level_structure(_lvl_path, csv_path):
    global csv_data_path
    global level_structure_path
    csv_data_path = csv_path
    level_structure_path = _lvl_path
    levels = pd.read_csv(level_structure_path)
    empty_sheets()

    current_level_ = 0
    for index, level in levels.iterrows():
        executed_plan = execute_planner(int(level['physical']), int(level['social']), int(level['cognitive']))
        current_level_ = export_plan_to_sheet(current_level_, executed_plan)

    
    create_levels()
    reset_fluents_csv()
    export_to_excel()
    push_to_gamebus()

def execute_planner(physical, social, cognitive):
    # Create the planning problem
    p = PlanningProblem(csv=csv_data_path, social_score=social, physical_score=physical, cognitive_score=cognitive)
    p.update_fluents_init(csv_fluents_path)
    # print(p.problem)
    with OneshotPlanner(name='lpg', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
        result = planner.solve(p.problem) # type: ignore
        plan = result.plan

        if plan is not None:
            print(plan)
            # assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY
            return plan
        else:
            print("No plan found.")

# def main():
#     create_level_structure()
    


# if __name__ == '__main__':
#     main()
