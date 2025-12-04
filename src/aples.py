import os
import yaml
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
    """
    print("--- Starting Execution Monitor ---")
    if not hasattr(plan, 'actions'):
        return

    for action_instance in plan.actions:
        act_name = action_instance.action.name
        print(f"Executing activity: {act_name}")
        
        if act_name in activities_data:
             activity_info = activities_data[act_name]
             robot_goals = activity_info.get('robot_goals')
             
             if robot_goals:
                 print(f"  Activity {act_name} has robot goals: {robot_goals}")
                 robot_plan = robot_problem.solve(robot_goals)
                 if robot_plan and publisher:
                     publisher.publish(robot_problem.problem, robot_plan)
             else:
                 print(f"  No robot goals for {act_name}")

def main():
    #create_level_structure(levels_csv, activities_csv)
    p = PlanningProblem(activities_config=activities_csv, level_flow_config=levels_csv)
    #print(p.problem)
    PDDLWriter(p.problem).write_problem('health_intervention_problem.pddl')
    PDDLWriter(p.problem).write_domain('health_intervention_domain.pddl')

    get_environment().credits_stream = None
    with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY)  as planner:
        result = planner.solve(p.problem) # type: ignore
        plan = result.plan

        if plan is not None:
            print(plan)
            assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY
            update_activities_yaml(plan, activities_csv)
            
            robot_problem = RobotProblem()
            publisher = PlanPublisher()
            try:
                execute_monitor(plan, p.data['activities'], robot_problem, publisher)
            finally:
                publisher.close()
            return plan
        else:
            print("No plan found.")
            exit()


if __name__ == '__main__':
    main()
