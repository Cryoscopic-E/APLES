from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import SequentialSimulator

class RobotProblem:
    
    def __init__(self):
        self.problem = Problem('robot-assistant')
        self._init_domain()
        self._init_state()

    def _init_domain(self):
        # Types
        self.Agent = UserType('Agent')
        self.Location = UserType('Location')
        self.Material = UserType('Material')
        self.Item = UserType('Item')

        # Fluents
        self.at = Fluent('at', BoolType(), agent=self.Agent, loc=self.Location)
        self.at_item = Fluent('at_item', BoolType(), item=self.Item, loc=self.Location)
        self.holding = Fluent('holding', BoolType(), agent=self.Agent, item=self.Item)
        self.hand_empty = Fluent('hand_empty', BoolType(), agent=self.Agent)
        self.has_material = Fluent('has_material', BoolType(), agent=self.Agent, material=self.Material)
        self.is_robot = Fluent('is_robot', BoolType(), agent=self.Agent)

        self.problem.add_fluent(self.at, default_initial_value=False)
        self.problem.add_fluent(self.at_item, default_initial_value=False)
        self.problem.add_fluent(self.holding, default_initial_value=False)
        self.problem.add_fluent(self.hand_empty, default_initial_value=True)
        self.problem.add_fluent(self.has_material, default_initial_value=False)
        self.problem.add_fluent(self.is_robot, default_initial_value=False)

        # Actions
        # Move
        move = InstantaneousAction('move', agent=self.Agent, l_from=self.Location, l_to=self.Location)
        agent = move.parameter('agent')
        l_from = move.parameter('l_from')
        l_to = move.parameter('l_to')
        move.add_precondition(self.at(agent, l_from))
        move.add_effect(self.at(agent, l_from), False)
        move.add_effect(self.at(agent, l_to), True)
        self.problem.add_action(move)

        # Prompt Text
        prompt = InstantaneousAction('prompt_text', source=self.Agent, target=self.Agent, loc=self.Location, mat=self.Material)
        source = prompt.parameter('source')
        target = prompt.parameter('target')
        loc = prompt.parameter('loc')
        mat = prompt.parameter('mat')
        prompt.add_precondition(self.is_robot(source))
        prompt.add_precondition(self.at(source, loc))
        prompt.add_precondition(self.at(target, loc))
        prompt.add_effect(self.has_material(target, mat), True)
        self.problem.add_action(prompt)

        # Pickup
        pickup = InstantaneousAction('pickup', agent=self.Agent, item=self.Item, loc=self.Location)
        agent = pickup.parameter('agent')
        item = pickup.parameter('item')
        loc = pickup.parameter('loc')
        pickup.add_precondition(self.at(agent, loc))
        pickup.add_precondition(self.at_item(item, loc))
        pickup.add_precondition(self.hand_empty(agent))
        pickup.add_effect(self.at_item(item, loc), False)
        pickup.add_effect(self.hand_empty(agent), False)
        pickup.add_effect(self.holding(agent, item), True)
        self.problem.add_action(pickup)

        # Drop
        drop = InstantaneousAction('drop_down', agent=self.Agent, item=self.Item, loc=self.Location)
        agent = drop.parameter('agent')
        item = drop.parameter('item')
        loc = drop.parameter('loc')
        drop.add_precondition(self.at(agent, loc))
        drop.add_precondition(self.holding(agent, item))
        drop.add_effect(self.holding(agent, item), False)
        drop.add_effect(self.hand_empty(agent), True)
        drop.add_effect(self.at_item(item, loc), True)
        self.problem.add_action(drop)

    def _init_state(self):
        # Add standard objects
        robot = Object('robot', self.Agent)
        human = Object('human', self.Agent)
        kitchen = Object('kitchen', self.Location)
        living_room = Object('living_room', self.Location)
        
        # Add to problem if not present
        if robot not in self.problem.all_objects: self.problem.add_object(robot)
        if human not in self.problem.all_objects: self.problem.add_object(human)
        if kitchen not in self.problem.all_objects: self.problem.add_object(kitchen)
        if living_room not in self.problem.all_objects: self.problem.add_object(living_room)

        # Set Initial State
        self.problem.set_initial_value(self.at(robot, kitchen), True)
        self.problem.set_initial_value(self.at(human, living_room), True)
        self.problem.set_initial_value(self.hand_empty(robot), True)
        self.problem.set_initial_value(self.is_robot(robot), True)

    def solve(self, goals):
        self.problem.clear_goals()
        
        # Process Goals and Dynamic Objects
        # goals is a list of dicts like [{'at(human)': True}, {'has_new_material(human)': 'new_phrase'}]
        for goal_dict in goals:
            for k, v in goal_dict.items():
                if 'has_new_material' in k:
                    # Assuming v is the material name
                    mat_name = v
                    mat_obj = Object(mat_name, self.Material)
                    if mat_obj not in self.problem.all_objects:
                        self.problem.add_object(mat_obj)
                    
                    # Extract agent from key if possible, or assume human based on usage
                    # k might be "has_new_material(human)"
                    agent_name = 'human' # Default
                    if 'human' in k: agent_name = 'human'
                    if 'robot' in k: agent_name = 'robot'
                    
                    agent_obj = self.problem.object(agent_name)

                    self.problem.add_goal(self.has_material(agent_obj, mat_obj))
                    
                elif 'at_item' in k:
                    # Format: "at_item(item_name)": "location_name"
                    # Extract item name from key. k might be "at_item(water)"
                    import re
                    match = re.search(r'at_item\((.*)\)', k)
                    if match:
                        item_name = match.group(1)
                        loc_name = v
                        
                        item_obj = Object(item_name, self.Item)
                        if item_obj not in self.problem.all_objects:
                            self.problem.add_object(item_obj)
                            # Default initial position for items created this way: kitchen
                            self.problem.set_initial_value(self.at_item(item_obj, self.problem.object('kitchen')), True)
                        
                        loc_obj = Object(loc_name, self.Location) 
                        if loc_obj in self.problem.all_objects:
                            self.problem.add_goal(self.at_item(item_obj, loc_obj))
                        else:
                             print(f"Warning: Location {loc_name} not found for goal {k}")

                elif 'holding' in k:
                     # Format: "holding(agent)": "item_name"
                     pass

        # Solve
        with OneshotPlanner(name='enhsp-opt', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
            result = planner.solve(self.problem)
            if result.plan:
                print(f"Robot Plan found: {result.plan}")
                self._apply_plan(result.plan)
                return result.plan
            else:
                print("No robot plan found.")
                return None

    def _apply_plan(self, plan):
        """
        Updates the initial state of the problem based on the plan execution.
        """
        simulator = SequentialSimulator(self.problem)
        
        current_state = simulator.get_initial_state()
        
        for action_instance in plan.actions:
            current_state = simulator.apply(current_state, action_instance.action, action_instance.actual_parameters)
            if current_state is None:
                print(f"Error simulating action: {action_instance}")
                return

        from itertools import product
        
        for fluent in self.problem.fluents:
            # Generate all parameter combinations for this fluent
            signature = fluent.signature
            # Get objects for each type
            # We assume all objects are in the problem
            
            type_objects = []
            for param in signature:
                type_objects.append(list(self.problem.objects(param.type)))
                
            # Cartesian product
            for args in product(*type_objects):
                fluent_instance = fluent(*args)
                new_value = current_state.get_value(fluent_instance)
                self.problem.set_initial_value(fluent_instance, new_value)