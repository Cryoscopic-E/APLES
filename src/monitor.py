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
        - Updates max_repetitions: usage decreases it, passage of time (decay) increases it.
        """
        
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

        try:
            with open(self.activities_yaml_path, 'r') as f:
                original_data = yaml.safe_load(f)
        except FileNotFoundError:
            original_data = {} # Should not happen if data loaded

        executed_actions = []
        if hasattr(plan, 'actions'):
            for action_instance in plan.actions:
                executed_actions.append(action_instance.action.name)
        
        
        updated = False
        if data:
            for category, activities in data.items():
                if activities:
                    for activity_dict in activities:
                        for activity_name, activity_data in activity_dict.items():
                            
                            # Get original max reps
                            original_max_reps = 99 # Default fallback
                            # Find in original data
                            if original_data and category in original_data:
                                for oa in original_data[category]:
                                    if activity_name in oa:
                                        original_max_reps = oa[activity_name].get('max_repetitions', original_max_reps)
                                        # Fallback to current if original not found (e.g. key mismatch)
                                        if original_max_reps is None: 
                                            original_max_reps = activity_data.get('max_repetitions', 99)

                            #Update Costs & Repetitions
                            count = executed_actions.count(activity_name)
                            if count > 0:
                                cost_increase = activity_data.get('cost_increase', 0)
                                initial_cost = activity_data.get('initial_cost', 0)
                                new_cost = initial_cost + (cost_increase * count)
                                activity_data['initial_cost'] = new_cost
                                
                                # Decrease max repetitions (Fatigue)
                                max_reps = activity_data.get('max_repetitions', None)
                                if max_reps is not None:
                                    # Decrease by usage
                                    new_max_reps = max(0, max_reps - count)
                                    activity_data['max_repetitions'] = new_max_reps
                                
                                updated = True
                            
                            
                            
                            recovery_rate = activity_data.get('recovery_rate', 1.0)
                            current_max = activity_data.get('max_repetitions', 0)
                            if current_max is not None:
                                # We only recover if we are below original limit
                                if current_max < original_max_reps:
                                    recovered_max = min(original_max_reps, current_max + recovery_rate)
                                    activity_data['max_repetitions'] = recovered_max
                                    # print(f"  Recovered {activity_name}: {current_max} -> {recovered_max}")

                            
                            tutorial_action_name = f"tutorial_{activity_name}"
                            if tutorial_action_name in executed_actions:
                                # print(f"DEBUG: Found action {tutorial_action_name} in plan")
                                if activity_data.get('requires_tutorial', False):
                                    activity_data['requires_tutorial'] = False
                                    updated = True
                                    print(f"  Tutorial completed for {activity_name}")


    def execute_robot_plans(self, plan, activities_data):
        """
        Monitors the execution of the plan and triggers robot planning if needed.
        Returns a list of generated robot plans (as strings).
        """
        robot_plans_log = []
        if not hasattr(plan, 'actions'):
            return robot_plans_log
        
        robot_problem = RobotProblem()
        publisher = PlanPublisher()

        try:
            for action_instance in plan.actions:
                act_name = action_instance.action.name
                
                if act_name in activities_data:
                    activity_info = activities_data[act_name]
                    robot_goals = activity_info.get('robot_goals')
                    
                    if robot_goals:
                        robot_plan = robot_problem.solve(robot_goals, planner_name='fast-downward')
                        if robot_plan:
                            robot_plans_log.append({
                                'activity': act_name,
                                'robot_plan': str(robot_plan)
                            })
                            publisher.publish(robot_problem.problem, robot_plan)
        finally:
            publisher.close()
            
        return robot_plans_log
