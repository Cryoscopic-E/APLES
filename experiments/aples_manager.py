import os
import time
from unified_planning.shortcuts import *
from unified_planning.model.metrics import MinimizeActionCosts
from unified_planning.engines import PlanGenerationResultStatus
from exporter import create_levels, empty_sheets, export_plan_to_sheet, export_to_excel, get_executed_actions, parse_video_url, push_to_gamebus, push_videos_to_gamebus, reset_fluents_csv
from unified_planning.shortcuts import Fluent, IntType, Problem, UserType, InstantaneousAction, MinimizeActionCosts, Object, OneshotPlanner
import pandas as pd

from planning_problem import PlanningProblem
get_environment().credits_stream = None
from unified_planning.io import PDDLWriter


csv_fluents_path = os.path.join(os.path.dirname(__file__), 'data', 'fluents.csv')

def create_level_structure(_lvl_path, csv_path):
    global csv_data_path
    global level_structure_path
    csv_data_path = csv_path
    level_structure_path = _lvl_path
    levels = pd.read_csv(level_structure_path)
    #empty_sheets()
    total_actions_in_plan = []
    current_level_ = 0
    start_time = time.time()
    for index, level in levels.iterrows():
        executed_plan = execute_planner(int(level['physical']), int(level['social']), int(level['cognitive']))
        total_actions_in_plan.append(len(executed_plan.actions))
        #current_level_ = export_plan_to_sheet(current_level_, executed_plan)
    end_time = time.time()
    
    #create csv with time performance
    #x: total number of activities y: number of levels  z: time
    n_levels = pd.read_csv(level_structure_path)

    #use csv_data_path to get the number of activities
    a = pd.read_csv(csv_data_path)

    n_social_activities = a[a['Type'] == 'social']
    n_physical_activities = a[a['Type'] == 'physical']
    n_cognitive_activities = a[a['Type'] == 'cognitive']
    n_general_activities = a[a['Type'] == 'general']
    tot = len(n_social_activities) + len(n_physical_activities) + len(n_cognitive_activities) + len(n_general_activities)
    df_t = pd.DataFrame([[tot, len(n_physical_activities), len(n_social_activities),len(n_cognitive_activities),len(n_general_activities),len(n_levels), end_time - start_time]], columns=['activities','phy_n','social_n','cog_n','general_n', 'levels', 'time'])
    df_t.to_csv('time_performance.csv', mode='a', header=False, index=False)
    
    #save the number of actions in each plan in a txt file
    with open('actions.txt', 'a') as f:
        f.write(str(total_actions_in_plan) + '\n')

    #create_levels()
    # reset_fluents_csv()
    
    #export_to_excel()
    #push_to_gamebus()

def execute_planner(physical, social, cognitive):
    # Create the planning problem
    p = PlanningProblem(csv=csv_data_path, social_score=social, physical_score=physical, cognitive_score=cognitive)
    p.update_fluents_init(csv_fluents_path)
    # print(p.problem)
    with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
        
        result = planner.solve(p.problem) # type: ignore
        
        plan = result.plan

        if plan is not None:
            print(plan)
            assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY
            return plan
        else:
            print("No plan found.")

def main():
    for a in range(3, 6):
        csv_data_path = os.path.join(os.path.dirname(__file__), 'data', 'exampleactivities_'+str(a)+'.csv')
        reset_fluents_csv()
        for l in range(2, 5):
            level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_'+str(l)+'.csv')
            create_level_structure(level_structure_path, csv_data_path)
    


if __name__ == '__main__':
    main()
