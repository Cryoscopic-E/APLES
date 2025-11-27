import os
from unified_planning.shortcuts import *
from unified_planning.model.metrics import *
from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import OneshotPlanner

from planning_problem import PlanningProblem

from unified_planning.io import PDDLWriter, PDDLReader

current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, 'data')
activities_csv = os.path.join(data_folder, 'activities.yaml')
levels_csv = os.path.join(data_folder, 'level_flow.yaml')


def create_level_structure(_lvl_path, csv_path):
    global csv_data_path
    global level_structure_path
    csv_data_path = csv_path
    level_structure_path = _lvl_path
    levels = pd.read_csv(level_structure_path)

    for index, level in levels.iterrows():
        executed_plan = execute_planner(int(level['physical']), int(level['social']), int(level['cognitive']), int(level['minigame']))

def execute_planner(physical, social, cognitive, minigame):
    # Create the planning problem
    p = PlanningProblem(csv=csv_data_path, social_score=social, physical_score=physical, cognitive_score=cognitive, minigame_score=minigame)
    #p.update_fluents_init(csv_fluents_path)
    # print(p.problem)
    with OneshotPlanner(name='enhsp', optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY) as planner:
        get_environment().credits_stream = None
        result = planner.solve(p.problem) # type: ignore
        plan = result.plan

        if plan is not None:
            print(plan)
            # assert result.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY
            return plan
        else:
            print("No plan found.")
            exit()

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
            return plan
        else:
            print("No plan found.")
            exit()


if __name__ == '__main__':
    main()
