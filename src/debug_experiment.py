import time
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus
from planning_problem import PlanningProblem
import os

# Mock data paths (assuming they exist from previous runs)
current_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(current_dir, 'data')
activities_csv = os.path.join(data_folder, 'activities.yaml')
levels_csv = os.path.join(data_folder, 'level_flow.yaml')

def test_planning(level_idx, optimality=True):
    print(f"--- Testing Level {level_idx} (Optimal: {optimality}) ---")
    try:
        # Note: I need to make sure activities.yaml has enough activities.
        # The previous run might have left it with 15 or 3. 
        # I will rely on what's there or the previous tool call's state.
        p = PlanningProblem(activities_config=activities_csv, level_flow_config=levels_csv, level_index=level_idx)
        
        mode = PlanGenerationResultStatus.SOLVED_OPTIMALLY if optimality else PlanGenerationResultStatus.SOLVED_SATISFICING
        name = 'enhsp-opt' if optimality else 'enhsp'

        print(f"Problem constructed. Goals: {p.problem.goals}")
        
        start = time.time()
        # If we want to test satisficing with ENHSP, we might need to specify it or just remove the optimality requirement
        with OneshotPlanner(name=name, optimality_guarantee=mode) as planner:
            print(f"Using planner: {planner.name}")
            result = planner.solve(p.problem)
            print(f"Status: {result.status.name}")
            print(f"Time: {time.time() - start:.4f}s")
            if result.plan:
                print(f"Plan length: {len(result.plan.actions)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Try a middle difficulty
    test_planning(30, optimality=False)
