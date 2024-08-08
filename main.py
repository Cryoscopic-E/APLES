from unified_planning.shortcuts import *
from unified_planning.model.types import BOOL

Activity = UserType('Activity')
Difficulty = UserType('Difficulty')
Physical = UserType('Physical', Activity)

difficulty_lvl = Fluent('difficulty_lvl', IntType(), d=Difficulty)
can_do_activity = Fluent('CanDoActivity', BOOL, activity=Activity)

tutorial_action = InstantaneousAction('tutorial_video', activity=Activity, d=Difficulty)
# parameters
activity = tutorial_action.parameter('activity')
difficulty = tutorial_action.parameter('d')
# preconditions
tutorial_action.add_precondition(Not(can_do_activity(activity)))
# effects
tutorial_action.add_effect(can_do_activity(activity), True)
tutorial_action.add_increase_effect(difficulty_lvl(difficulty), 1)


class ActivityClass(InstantaneousAction):
    def __init__(self, name, score):
        self.name = name
        self.score = score
        super().__init__(self.name, activity=Activity, d=Difficulty)
        # parameters
        act = self.parameter('activity')
        d = self.parameter('d')
        # preconditions
        self.add_precondition(can_do_activity(act))
        # effects
        self.add_increase_effect(difficulty_lvl(d), self.score)


activities = [{'name': 'running', 'score': 3}, {'name': 'walking', 'score': 1}]
actions = []
for a in activities:
    actions.append(ActivityClass(a['name'], a['score']))

problem = Problem('health')

problem.add_fluent(can_do_activity, default_initial_value=False)
problem.add_fluent(difficulty_lvl, default_initial_value=0)

running_activity = Object('running_act', Physical)
diff = Object('counter', Difficulty)

problem.add_action(tutorial_action)
problem.add_actions(actions)

problem.add_object(running_activity)
problem.add_object(diff)
problem.add_goal(GE(difficulty_lvl(diff), 3))
print(problem)

with OneshotPlanner(name='enhsp') as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")
