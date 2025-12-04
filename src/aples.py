import os
import yaml
import time
import csv
import json
import random
import numpy as np
from unified_planning.shortcuts import *
from unified_planning.model.metrics import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner

from planning_problem import PlanningProblem
from robot_problem import RobotProblem
from plan_publisher import PlanPublisher

from unified_planning.io import PDDLWriter, PDDLReader

current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, 'data')
activities_csv = os.path.join(data_folder, 'activities.yaml')
levels_csv = os.path.join(data_folder, 'level_flow.yaml')

def generate_level_flow(filepath, num_levels=50):
    levels = {
        'physical': [],
        'social': [],
        'cognitive': []
    }
    
    # Generate increasing difficulty
    for i in range(num_levels):
        levels['physical'].append(5 + int(i * 1.5) + random.randint(0, 3))
        levels['social'].append(int(i * 1.2) + random.randint(0, 2))
        levels['cognitive'].append(int(i * 1.2) + random.randint(0, 2))

    with open(filepath, 'w') as f:
        yaml.dump(levels, f, default_flow_style=None)
    print(f"Generated {num_levels} levels in {filepath}")

def generate_synthetic_activities(filepath, count_per_category):
    base_activities = {
        'physical': [
            "Walk_5k", "Walk_10k", "Walk_Marathon", "Yoga_Session", "Stretching", 
            "Lift_Weights", "Swim_Laps", "Cycling_Indoor", "Cycling_Outdoor", "Hiking",
            "Jump_Rope", "Pilates", "Tai_Chi", "Gardening", "Dancing"
        ],
        'cognitive': [
            "Learn_Phrase", "Watch_Doc", "Brain_Game", "Read_Book", "Sudoku",
            "Crossword", "Chess", "Learn_Instrument", "Paint", "Write_Journal",
            "Listen_Podcast", "Solve_Puzzle", "Memory_Game", "Math_Practice", "History_Quiz"
        ],
        'social': [
            "Call_Friend", "Social_Event", "Talk_Family", "Write_Letter", "Video_Call",
            "Host_Dinner", "Join_Club", "Volunteer", "Park_Meetup", "Board_Game_Night",
            "Coffee_Chat", "Group_Class", "Visit_Neighbor", "Send_Gift", "Attend_Lecture"
        ]
    }

    activities_structure = {'physical': [], 'cognitive': [], 'social': []}

    for category, names in base_activities.items():
        # Ensure we don't exceed available names, loop if necessary (though 15 is enough for this exp)
        selected_names = names[:count_per_category]
        
        for name in selected_names:
            act_data = {
                'initial_cost': random.randint(5, 25),
                'cost_increase': random.randint(1, 5),
                'MET_score': random.randint(3, 15),
                'value': None,
                'requires_tutorial': random.choice([True, False]),
                'robot_goals': None
            }
            
            # Add some robot goals randomly
            if random.random() < 0.3:
                if category == 'physical':
                     act_data['robot_goals'] = [{'at_item(water_bottle)': 'living_room'}]
                elif category == 'social':
                     act_data['robot_goals'] = [{'has_new_material(human)': 'phone_number'}]
                elif category == 'cognitive':
                     act_data['robot_goals'] = [{'has_new_material(human)': 'puzzle'}]

            activities_structure[category].append({name: act_data})

    with open(filepath, 'w') as f:
        yaml.dump(activities_structure, f, default_flow_style=False, sort_keys=False)
    print(f"Generated {count_per_category} activities per category in {filepath}")

def update_activities_yaml(plan, yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    
    executed_actions = set()
    if hasattr(plan, 'actions'):
        for action_instance in plan.actions:
            executed_actions.add(action_instance.action.name)
            
    updated = False
    if data:
        for category, activities in data.items():
            if activities:
                for activity_dict in activities:
                    for activity_name, activity_data in activity_dict.items():
                        if activity_name in executed_actions:
                            cost_increase = activity_data.get('cost_increase', 0)
                            initial_cost = activity_data.get('initial_cost', 0)
                            activity_data['initial_cost'] = initial_cost + cost_increase
                            updated = True

    if updated:
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def execute_monitor(plan, activities_data, robot_problem, publisher=None):
    """
    Monitors the execution of the plan and triggers robot planning if needed.
    Returns a list of generated robot plans (as strings).
    """
    # print("--- Starting Execution Monitor ---") # Reduced verbosity for experiment
    robot_plans_log = []
    if not hasattr(plan, 'actions'):
        return robot_plans_log

    for action_instance in plan.actions:
        act_name = action_instance.action.name
        # print(f"Executing activity: {act_name}")
        
        if act_name in activities_data:
             activity_info = activities_data[act_name]
             robot_goals = activity_info.get('robot_goals')
             
             if robot_goals:
                 # print(f"  Activity {act_name} has robot goals: {robot_goals}")
                 robot_plan = robot_problem.solve(robot_goals)
                 if robot_plan:
                     robot_plans_log.append({
                         'activity': act_name,
                         'robot_plan': str(robot_plan)
                     })
                     if publisher:
                        publisher.publish(robot_problem.problem, robot_plan)
             else:
                 pass
                 # print(f"  No robot goals for {act_name}")
    return robot_plans_log

def main():
    # Experiment Configurations
    domain_sizes = [3, 6, 9, 12, 15] # Activities per category
    selected_levels = list(range(50)) # Run all 50 levels
    
    experiment_file = 'experiment_scalability_results.csv'
    plans_file = 'experiment_plans.json'
    print(f"Running Scalability Experiment. Logging to {experiment_file} and {plans_file}")
    
    # Generate the level flow once
    generate_level_flow(levels_csv, num_levels=50)

    results = []
    all_plans_log = []

    with open(experiment_file, 'w', newline='') as csvfile:
        fieldnames = ['domain_size', 'level', 'plan_length', 'generation_time', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for size in domain_sizes:
            print(f"\n>>> Testing with Domain Size: {size} activities per category")
            generate_synthetic_activities(activities_csv, count_per_category=size)
            
            for lvl_idx in selected_levels:
                print(f"   Processing Level {lvl_idx}...", end='', flush=True)
                
                p = PlanningProblem(activities_config=activities_csv, level_flow_config=levels_csv, level_index=lvl_idx)
                
                get_environment().credits_stream = None
                
                start_time = time.time()
                plan = None
                robot_plans = []
                status = "UNKNOWN"
                generation_time = 0
                plan_length = 0

                try:
                    # switched to 'enhsp' (satisficing) for scalability experiment
                    with OneshotPlanner(name='enhsp', optimality_guarantee=PlanGenerationResultStatus.SOLVED_SATISFICING)  as planner:
                        result = planner.solve(p.problem) # type: ignore
                        end_time = time.time()
                        generation_time = end_time - start_time
                        
                        plan = result.plan
                        status = result.status.name
                        plan_length = len(plan.actions) if plan and hasattr(plan, 'actions') else 0
                        
                        if plan:
                             robot_problem = RobotProblem()
                             publisher = PlanPublisher()
                             try:
                                 # We don't strictly need to update costs for this scalability test as we re-gen activities
                                 # but we can if we want to simulate evolution within a size block.
                                 # For now, keeping it simple (stateless per level).
                                 robot_plans = execute_monitor(plan, p.data['activities'], robot_problem, publisher)
                             finally:
                                 publisher.close()

                except Exception as e:
                    print(f" Error: {e}")
                    status = "ERROR"
                    
                print(f" Done. Time: {generation_time:.4f}s, Actions: {plan_length}")

                writer.writerow({
                    'domain_size': size,
                    'level': lvl_idx,
                    'plan_length': plan_length,
                    'generation_time': generation_time,
                    'status': status
                })
                csvfile.flush()
                
                results.append({
                    'domain_size': size,
                    'level': lvl_idx,
                    'time': generation_time,
                    'len': plan_length
                })

                all_plans_log.append({
                    'domain_size': size,
                    'level': lvl_idx,
                    'activity_plan': str(plan) if plan else None,
                    'robot_plans': robot_plans
                })

    # Save detailed plans to JSON
    with open(plans_file, 'w') as f:
        json.dump(all_plans_log, f, indent=2)
    print(f"Detailed plans saved to {plans_file}")

    # Statistical Evaluation
    print("\n=== Statistical Evaluation ===")
    if len(results) > 0:
        times = [r['time'] for r in results]
        sizes = [r['domain_size'] for r in results]
        levels = [r['level'] for r in results]
        
        corr_size_time = np.corrcoef(sizes, times)[0, 1]
        corr_lvl_time = np.corrcoef(levels, times)[0, 1]
        
        print(f"Correlation (Domain Size vs Time): {corr_size_time:.4f}")
        print(f"Correlation (Difficulty Level vs Time): {corr_lvl_time:.4f}")
        
        if abs(corr_size_time) < 0.5:
            print("-> Observation: Planning time is relatively independent of domain size (Scalable).")
        else:
            print("-> Observation: Planning time shows correlation with domain size.")

if __name__ == '__main__':
    main()
