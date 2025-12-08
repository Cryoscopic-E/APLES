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
from monitor import PlanMonitor

from unified_planning.io import PDDLWriter, PDDLReader

current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, 'data')
activities_csv = os.path.join(data_folder, 'activities.yaml')
levels_csv = os.path.join(data_folder, 'level_flow.yaml')

def generate_level_flow(filepath, num_levels=30):
    levels = {
        'physical': [],
        'social': [],
        'cognitive': []
    }
    
    for i in range(num_levels):
        levels['physical'].append(5 + int(i * 1.5) + random.randint(0, 3))
        levels['social'].append(int(i * 1.2) + random.randint(0, 2))
        levels['cognitive'].append(int(i * 1.2) + random.randint(0, 2))

    with open(filepath, 'w') as f:
        yaml.dump(levels, f, default_flow_style=None)
    print(f"Generated {num_levels} levels in {filepath}")

def main():
    
    selected_levels = list(range(30))
    categories = ['physical', 'social', 'cognitive']
    
    experiment_file = 'experiment_scalability_results.csv'
    plans_file = 'experiment_plans.json'
    
    # Generate the level flow once
    generate_level_flow(levels_csv, num_levels=30)

    results = []
    all_plans_log = []

    monitor = PlanMonitor(activities_csv)

    save_pddl = True
    saved_categories = set()
    
    pddl_output_dir = "pddl"
    os.makedirs(pddl_output_dir, exist_ok=True)
    
    # Load initial activities state once
    with open(activities_csv, 'r') as f:
        activities_data = yaml.safe_load(f)

    with open(experiment_file, 'w', newline='') as csvfile:
        fieldnames = ['domain_size', 'level', 'category', 'plan_length', 'plan_cost', 'generation_time', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for lvl_idx in selected_levels:
            print(f"   Processing Level {lvl_idx}...", end='', flush=True)
            
            level_plans = {}
            
            for category in categories:
                
                p = PlanningProblem(activities_config=activities_csv, level_flow_config=levels_csv, level_index=lvl_idx, category=category, activities_data=activities_data)
                
                if save_pddl and category not in saved_categories:
                    pddl_writer = PDDLWriter(p.problem)
                    pddl_writer.write_domain(os.path.join(pddl_output_dir, f"domain_{category}.pddl"))
                    pddl_writer.write_problem(os.path.join(pddl_output_dir, f"problem_{category}.pddl"))
                    saved_categories.add(category)
                    print(f" [PDDL saved for {category} in {pddl_output_dir}/]", end='', flush=True)
                    save_pddl = False
                
                get_environment().credits_stream = None
                
                start_time = time.time()
                plan = None
                robot_plans = []
                status = "UNKNOWN"
                generation_time = 0
                plan_length = 0
                plan_cost = 0

                try:
                    with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)  as planner:
                        result = planner.solve(p.problem)
                        end_time = time.time()
                        generation_time = end_time - start_time
                        
                        plan = result.plan
                        status = result.status.name
                        if plan and hasattr(plan, 'actions'):
                            plan_length = len(plan.actions)

                            for action_instance in plan.actions:
                                act_name = action_instance.action.name

                                if act_name.startswith('tutorial_'):
                                    plan_cost += 1
                                elif act_name in p.data['activities']:
                                    plan_cost += p.data['activities'][act_name]['current_cost'] 
                        if plan:
                                try:
                                    robot_plans = monitor.execute_robot_plans(plan, p.data['activities'])
                                except Exception as rp_e:
                                    print(f" Robot Planning Error: {rp_e}")
                                
                                monitor.update_state(plan, activities_data)

                except Exception as e:
                    print(f" Error [{category}]: {e}")
                    status = "ERROR"
                    
               

                writer.writerow({
                    'level': lvl_idx,
                    'category': category,
                    'plan_length': plan_length,
                    'plan_cost': plan_cost,
                    'generation_time': generation_time,
                    'status': status
                })
                csvfile.flush()
                
                results.append({
                    'level': lvl_idx,
                    'category': category,
                    'time': generation_time,
                    'len': plan_length
                })

                level_plans[category] = {
                    'activity_plan': str(plan) if plan else None,
                    'robot_plans': robot_plans,
                    'status': status
                }

            print(" Done.")
            all_plans_log.append({
                'level': lvl_idx,
                'plans': level_plans
            })

    with open(plans_file, 'w') as f:
        json.dump(all_plans_log, f, indent=2)
    print(f"Detailed plans saved to {plans_file}")


    print("\n=== Statistical Evaluation ===")
    if len(results) > 0:
        for category in categories:
            cat_results = [r for r in results if r['category'] == category]
            if not cat_results:
                continue
                
            times = [r['time'] for r in cat_results]
            levels = [r['level'] for r in cat_results]
            
            
            if len(set(levels)) > 1 and np.std(times) > 0:
                corr_lvl_time = np.corrcoef(levels, times)[0, 1]
                print(f"Category: {category.capitalize()}")
                print(f"Correlation (Level vs Time): {corr_lvl_time:.4f}")
            else:
                print(f"Category: {category.capitalize()} - Insufficient variance for correlation.")
                
        
        all_times = [r['time'] for r in results]
        all_levels = [r['level'] for r in results]
        if len(set(all_levels)) > 1 and np.std(all_times) > 0:
             glob_corr = np.corrcoef(all_levels, all_times)[0, 1]
             print(f"Global Correlation (Level vs Time): {glob_corr:.4f}")

if __name__ == '__main__':
    main()