import yaml
from unified_planning.engines import PlanGenerationResultStatus
from plan_publisher import PlanPublisher
from robot_problem import RobotProblem

class PlanMonitor:
    def __init__(self, activities_yaml_path):
        self.activities_yaml_path = activities_yaml_path

    def update_state(self, plan, activities_data_override=None):
        """
        Updates the state of activities in the YAML file based on the actions in the plan.
        - Increases cost by 'cost_increase' for each occurrence.
        - Sets 'requires_tutorial' to False if a tutorial action is performed.
        """
        print(f"Updating state in {self.activities_yaml_path}...")
        
        data = None
        if activities_data_override:
            data = activities_data_override
        else:
            try:
                with open(self.activities_yaml_path, 'r') as f:
                    data = yaml.safe_load(f)
            except FileNotFoundError:
                print(f"Error: File {self.activities_yaml_path} not found.")
                return

        executed_actions = []
        if hasattr(plan, 'actions'):
            for action_instance in plan.actions:
                executed_actions.append(action_instance.action.name)
        
        if not executed_actions:
            return

        updated = False
        if data:
            for category, activities in data.items():
                if activities:
                    for activity_dict in activities:
                        for activity_name, activity_data in activity_dict.items():
                            
                            # 1. Update Costs
                            count = executed_actions.count(activity_name)
                            if count > 0:
                                cost_increase = activity_data.get('cost_increase', 0)
                                initial_cost = activity_data.get('initial_cost', 0)
                                new_cost = initial_cost + (cost_increase * count)
                                activity_data['initial_cost'] = new_cost
                                updated = True
                            
                            # 2. Update Tutorial State
                            # The tutorial action is named "tutorial_{activity_name}"
                            tutorial_action_name = f"tutorial_{activity_name}"
                            if tutorial_action_name in executed_actions:
                                # print(f"DEBUG: Found action {tutorial_action_name} in plan")
                                if activity_data.get('requires_tutorial', False):
                                    activity_data['requires_tutorial'] = False
                                    updated = True
                                    print(f"  Tutorial completed for {activity_name}")

        if updated:
            with open(self.activities_yaml_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            print("State updated successfully.")

    def execute_robot_plans(self, plan, activities_data):
        """
        Monitors the execution of the plan and triggers robot planning if needed.
        Returns a list of generated robot plans (as strings).
        """
        robot_plans_log = []
        if not hasattr(plan, 'actions'):
            return robot_plans_log
        
        # Initialize Robot Problem and Publisher once per execution batch if needed, 
        # or we can instantiate them here. 
        # To follow the original pattern:
        robot_problem = RobotProblem()
        publisher = PlanPublisher()

        try:
            for action_instance in plan.actions:
                act_name = action_instance.action.name
                
                if act_name in activities_data:
                    activity_info = activities_data[act_name]
                    robot_goals = activity_info.get('robot_goals')
                    
                    if robot_goals:
                        robot_plan = robot_problem.solve(robot_goals, planner_name='enhsp')
                        if robot_plan:
                            robot_plans_log.append({
                                'activity': act_name,
                                'robot_plan': str(robot_plan)
                            })
                            publisher.publish(robot_problem.problem, robot_plan)
        finally:
            publisher.close()
            
        return robot_plans_log
