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
    
    # Generate increasing difficulty
    for i in range(num_levels):
        levels['physical'].append(5 + int(i * 1.5) + random.randint(0, 3))
        levels['social'].append(int(i * 1.2) + random.randint(0, 2))
        levels['cognitive'].append(int(i * 1.2) + random.randint(0, 2))

    with open(filepath, 'w') as f:
        yaml.dump(levels, f, default_flow_style=None)
    print(f"Generated {num_levels} levels in {filepath}")

# ... (generate_synthetic_activities definition remains but is unused) ...

def main():
    # Experiment Configurations
    domain_sizes = [3, 6, 9, 12, 15] # Activities per category
    domain_sizes = [15] # For quicker testing, focus on max size
    selected_levels = list(range(30)) # Run all 30 levels (Simulate a month)
    categories = ['physical', 'social', 'cognitive']
    
    experiment_file = 'experiment_scalability_results.csv'
    plans_file = 'experiment_plans.json'
    print(f"Running Scalability Experiment. Logging to {experiment_file} and {plans_file}")
    
    # Generate the level flow once
    generate_level_flow(levels_csv, num_levels=30)

    results = []
    all_plans_log = []

    monitor = PlanMonitor(activities_csv)

    save_pddl = True
    saved_categories = set()
    
    # Load initial activities state once
    with open(activities_csv, 'r') as f:
        master_activities_data = yaml.safe_load(f)

    with open(experiment_file, 'w', newline='') as csvfile:
        fieldnames = ['domain_size', 'level', 'category', 'plan_length', 'generation_time', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for size in domain_sizes:
            print(f"\n>>> Testing with Domain Size: {size} activities per category")
            # generate_synthetic_activities(activities_csv, count_per_category=size) 
            
            for lvl_idx in selected_levels:
                print(f"   Processing Level {lvl_idx}...", end='', flush=True)
                
                level_plans = {}
                
                for category in categories:
                    # Use the master data object
                    p = PlanningProblem(activities_config=activities_csv, level_flow_config=levels_csv, level_index=lvl_idx, category=category, activities_data=master_activities_data)
                    
                    if save_pddl and category not in saved_categories:
                        pddl_writer = PDDLWriter(p.problem)
                        pddl_writer.write_domain(f"domain_{category}.pddl")
                        pddl_writer.write_problem(f"problem_{category}.pddl")
                        saved_categories.add(category)
                        print(f" [PDDL saved for {category}]", end='', flush=True)
                    
                    get_environment().credits_stream = None
                    
                    start_time = time.time()
                    plan = None
                    robot_plans = []
                    status = "UNKNOWN"
                    generation_time = 0
                    plan_length = 0

                    try:
                        # switched to 'enhsp' (satisficing) for scalability experiment
                        with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)  as planner:
                            result = planner.solve(p.problem) # type: ignore
                            end_time = time.time()
                            generation_time = end_time - start_time
                            
                            plan = result.plan
                            status = result.status.name
                            plan_length = len(plan.actions) if plan and hasattr(plan, 'actions') else 0
                            
                            if plan:
                                 try:
                                     robot_plans = monitor.execute_robot_plans(plan, p.data['activities'])
                                 except Exception as rp_e:
                                     print(f" Robot Planning Error: {rp_e}")
                                 
                                 # Update the master data object and save it
                                 monitor.update_state(plan, master_activities_data)

                    except Exception as e:
                        print(f" Error [{category}]: {e}")
                        status = "ERROR"
                        
                    # print(f" [{category}: {generation_time:.4f}s]", end='')

                    writer.writerow({
                        'domain_size': size,
                        'level': lvl_idx,
                        'category': category,
                        'plan_length': plan_length,
                        'generation_time': generation_time,
                        'status': status
                    })
                    csvfile.flush()
                    
                    results.append({
                        'domain_size': size,
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
                    'domain_size': size,
                    'level': lvl_idx,
                    'plans': level_plans
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
        
        # Simple aggregation for correlation check (summing times per level might be better but this is rough)
        corr_size_time = np.corrcoef(sizes, times)[0, 1] if len(set(sizes)) > 1 else 0
        corr_lvl_time = np.corrcoef(levels, times)[0, 1] if len(set(levels)) > 1 else 0
        
        print(f"Correlation (Domain Size vs Time): {corr_size_time:.4f}")
        print(f"Correlation (Difficulty Level vs Time): {corr_lvl_time:.4f}")

if __name__ == '__main__':
    main()
