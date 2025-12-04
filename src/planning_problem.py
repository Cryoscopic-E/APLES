from unified_planning.shortcuts import Fluent, IntType, Problem, UserType, InstantaneousAction, MinimizeActionCosts, Object
from unified_planning.shortcuts import GE, Not, Plus
from unified_planning.model.types import BOOL

from components import *
import yaml

class PlanningProblem:
    """
    Class representing the planning problem for the heal intervention domain

    :param csv: path to the csv file containing the activities
    """
    
    def __init__(self, activities_config : str, level_flow_config : str):
        # loaded data
        self.data = {}
        self.all_activity_actions = {}
        self.all_activity_actions_cost_expressions = {}
        self.all_objects = []
        self._read_data(activities_config, level_flow_config)
        self.level_index = 2

        # up problem
        self.problem = Problem('health-intervention')

        self.all_types = {}
        self._init_types()
        
        self.all_fluents = {}
        self._init_fluents()
        

        
        #self._create_tutorial_action()
        self._init_activity_actions()
        self._set_metrics()

        
        self._init_objects()


        
        self._init_goal(p=self.data['physical_flow'][self.level_index], s=self.data['social_flow'][self.level_index],  c=self.data['cognitive_flow'][self.level_index]) 


    def _read_data(self, activities_config : str, level_flow_config : str):
        """
        Loads the domain config from the yaml file
        """
        with open(activities_config, 'r') as f:
            activities_data = yaml.safe_load(f)
            activities_types = list(activities_data.keys())
            self.data['activities_types'] = activities_types
            
            activities_types = list(activities_data.keys())
            
            self.data['activities'] = {}

            for activity_type in activities_types:
                activity_list = activities_data[activity_type]
                for activity in activity_list:
                    for key, value in activity.items():
                        self.data['activities'][key] = {
                            'activity_type': activity_type,
                            'met_score': value.get('MET_score', 0),
                            'cost_increase': value.get('cost_increase', 0),
                            'current_cost': value.get('initial_cost', 0),
                            'value': value.get('value', None),
                            'requires_tutorial': value.get('requires_tutorial', False),
                            'robot_goals': value.get('robot_goals', None)
                        }

        with open(level_flow_config, 'r') as f:
            level_flows = yaml.safe_load(f)
            activities_types = level_flows.keys()
            for activity_type in activities_types:
                flow_list = level_flows[activity_type]
                self.data[activity_type + '_flow'] = flow_list



    def _init_types(self):
        """
        Initializes all types
        """
        
        self.all_types['activity'] = UserType('activity')
        self.all_types['general'] = UserType('general', self.all_types['activity'])

        for activity_type in self.data['activities_types']:
            self.all_types[activity_type] = UserType(activity_type, self.all_types['activity'])

    def _init_fluents(self):
        """
        Initializes all fluents
        """
        ## Counter fluents for activity levels difficulties
        counter_fluents = ['difficulty_lvl','difficulty_lvl_social', 'difficulty_lvl_physical', 'difficulty_lvl_cognitive']
        for fluent in counter_fluents:
            self.all_fluents[fluent] = Fluent(fluent, IntType())
        
        # add fluents to the problem
        for fluent in self.all_fluents.values():
            if fluent.type == BOOL:
                self.problem.add_fluent(fluent, default_initial_value=False)
            else:
                self.problem.add_fluent(fluent, default_initial_value=0)


        ## Boolean fluents for tutorial actions (Only certain activities might have tutorial actions)
        for k,v in self.data['activities'].items():
        
            fluent_name = f'can_do_{k}'
            tutorial_fluent = Fluent(fluent_name, BOOL)
            self.all_fluents[fluent_name] = tutorial_fluent

        
            if v['requires_tutorial']:
                self.problem.add_fluent(tutorial_fluent, default_initial_value=False)
                # Create tutorial action for this activity
                tutorial_action = InstantaneousAction(f'tutorial_{k}')
                
                # preconditions
                tutorial_action.add_precondition(Not(tutorial_fluent))
                # effects
                tutorial_action.add_effect(tutorial_fluent, True)

                self.problem.add_action(tutorial_action)
                self.all_activity_actions_cost_expressions[tutorial_action] = 1
            else:
                self.problem.add_fluent(tutorial_fluent, default_initial_value=True)


        
    
    def _init_activity_actions(self):
        """
        Initializes the actions
        """
        for activity_name, activity_data in self.data['activities'].items():
            activity_type = activity_type_mapping[activity_data['activity_type']]
            activity_score = activity_data['met_score']
            activity_cost = activity_data['current_cost']
            activity_cost_increase = activity_data['cost_increase']
            
            # add a fluents for the current cost of the action
            self.all_fluents['cost_' + activity_name] = Fluent('cost_' + activity_name, IntType())

            # add the fluents for the action cost to the problem
            self.problem.add_fluent(self.all_fluents['cost_' + activity_name], default_initial_value=activity_cost)

            try:
                action = ActivityAction(activity_name, activity_score, activity_cost_increase, activity_type, self.all_fluents, self.all_types, requires_tutorial=activity_data['requires_tutorial'])
                
            except ValueError as e:
                print(f"Error creating action for activity '{activity_name}': {e}")
            
            # add action to dictionary
            # if the activity is already in the dictionary, it will fail and raise an error
            if activity_name in self.all_activity_actions:
                raise ValueError('Activity already exists in the dictionary of actions')
            self.all_activity_actions[activity_name] = action

            # add the cost expression for the action
            self.all_activity_actions_cost_expressions[action] = Plus(self.all_fluents['cost_' + activity_name], activity_score)

            # add action to the problem
            self.problem.add_action(action)
    
    def _set_metrics(self):
        """
        Sets the metrics for the problem
        """
        self.problem.quality_metrics.clear()
        self.problem.add_quality_metric(MinimizeActionCosts(self.all_activity_actions_cost_expressions))

    def _create_tutorial_action(self):
        tutorial_action = InstantaneousAction('tutorial_video', activity_type=self.all_types['activity'])
        # parameters
        activity_type = tutorial_action.parameter('activity_type')

        # preconditions
        tutorial_action.add_precondition(Not(self.all_fluents['can_do_activity_type'](activity_type)))

        # effects
        tutorial_action.add_effect(self.all_fluents['can_do_activity_type'](activity_type), True)
        tutorial_action.add_increase_effect(self.all_fluents['difficulty_lvl'], 1)

        self.all_activity_actions_cost_expressions[tutorial_action] = 0
        
        # add action to the problem
        self.problem.add_action(tutorial_action)
    
    def _init_objects(self):
        physical_act_type = Object('physical_activity', self.all_types['physical'])
        social_act_type = Object('social_activity', self.all_types['social'])
        cognitive_act_type = Object('cognitive_activity', self.all_types['cognitive'])
        self.all_objects.append(physical_act_type)
        self.all_objects.append(social_act_type)
        self.all_objects.append(cognitive_act_type)

        self.problem.add_object(physical_act_type)
        self.problem.add_object(social_act_type)
        self.problem.add_object(cognitive_act_type)

    def _init_goal(self, p=0, s=0, c=0, m=0):
        self.problem.add_goal(GE(self.all_fluents['difficulty_lvl_physical'], p))
        self.problem.add_goal(GE(self.all_fluents['difficulty_lvl_social'], s))
        self.problem.add_goal(GE(self.all_fluents['difficulty_lvl_cognitive'], c))

    def __repr__(self) -> str:
        return str(self.problem)

