from unified_planning.shortcuts import Problem, InstantaneousAction


class PlanManager:
    """
    Keeps tracks of the action and fluents.
    Updates the action costs every time a new plan is generated and by following custom rules.
    Updates the fluents to have different initial values every time a new plan is generated.
    """

    def __init__(self, problem: Problem):
        self.action_costs = {}
        for action in problem.actions:
            self.action_costs[action.name] = 0

        self.fluent_initial_values = {}
        for k, v in problem.fluents_defaults.items():
            self.fluent_initial_values[k.name] = v.simplify()

        print("PlanManager initialized")
        print("Action costs: ", self.action_costs)
        print("Fluent initial values: ", self.fluent_initial_values)

    def update_action_costs(self):
        """
        Updates the action costs.
        """
        for action in self.actions:
            self.action_costs[action] = action.score

    def get_action_costs(self, action_name):
        """
        Returns the action costs for the given action name, if it exists.
        """
        if action_name in self.action_costs:
            return self.action_costs[action_name]
        return None
