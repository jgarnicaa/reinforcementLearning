"""
TP1 - Part 1: CP-SAT Model for RCPSP

Implement a complete CP-SAT solver for Resource Constrained Project Scheduling.

KEY DIFFERENCE FROM JOB SHOP:
    - Job Shop: NoOverlap (machine capacity = 1)
    - RCPSP: AddCumulative (resource capacity >= 1)

Complete the TODOs to build your solver.
Uses discrete-optimization's OrtoolsCpSatSolver API.
"""

import os
os.environ["DO_SKIP_MZN_CHECK"] = "1"

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpSolverSolutionCallback
from typing import Dict, Tuple

from discrete_optimization.rcpsp.problem import RcpspProblem, RcpspSolution
from discrete_optimization.generic_tools.ortools_cpsat_tools import OrtoolsCpSatSolver
from discrete_optimization.generic_tools.cp_tools import ParametersCp

from scheduling.tp1_rcpsp.utils import (
    load_instance,
    print_problem_stats,
    visualize_solution,
    compute_simple_lower_bound,
)
from scheduling.utils.rcpsp_utils import (
    compute_predecessors,
    get_task_durations,
    get_resource_consumption,
)


class RcpspCpSatSolver(OrtoolsCpSatSolver):
    """
    CP-SAT Solver for RCPSP.

    Students should complete the methods marked with TODO.
    Inherits from OrtoolsCpSatSolver - you only need to implement init_model() and retrieve_solution()!
    """

    def __init__(self, problem: RcpspProblem):
        """
        Initialize the solver.

        Args:
            problem: RcpspProblem from discrete-optimization
        """
        super().__init__(problem)
        self.variables = {}

    def init_model(self, **kwargs):
        """
        Initialize the CP model with variables and constraints.

        Note: Must call super().init_model(**kwargs) to create self.cp_model
        Use self.cp_model instead of self.model for all CP-SAT operations.

        This method should:
        1. Compute a horizon (upper bound on makespan)
        2. Create decision variables (starts, ends, intervals)
        3. Add precedence constraints
        4. Add resource constraints (AddCumulative!)
        5. Define objective (minimize makespan)
        """

        # ------------------------------------------------------------------
        # STEP 1: Compute Horizon
        # ------------------------------------------------------------------
        # Use the same approach as Job Shop: sum of all durations
        # Hint: Use get_task_durations() utility

        horizon = sum(get_task_durations(self.problem).values())

        # ------------------------------------------------------------------
        # TODO 1.1: Create Decision Variables
        # ------------------------------------------------------------------
        # Create starts, ends, and intervals for each task
        # Hint: Similar to Job Shop
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.1: Create decision variables")

        # ------------------------------------------------------------------
        # TODO 1.2: Add Precedence Constraints
        # ------------------------------------------------------------------
        # Ensure tasks start after their predecessors finish
        # Hint: compute_predecessors() utility
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.2: Add precedence constraints")

        # ------------------------------------------------------------------
        # TODO 1.3: Add Resource Constraints (CUMULATIVE!)
        # ------------------------------------------------------------------
        # KEY: Use AddCumulative, NOT AddNoOverlap!
        # For each resource: collect intervals, demands, then add constraint
        # Hint: get_resource_consumption() utility
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.3: Add cumulative resource constraints")

        # ------------------------------------------------------------------
        # TODO 1.4: Define Objective (Minimize Makespan)
        # ------------------------------------------------------------------
        # Makespan = max of all end times
        # Hint: AddMaxEquality, then Minimize
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.4: Define objective function")

    def retrieve_solution(self, cpsolvercb: CpSolverSolutionCallback) -> RcpspSolution:
        """
        Extract solution from CP-SAT callback.

        This method is called automatically by discrete-optimization's OrtoolsCpSatSolver
        each time the CP-SAT solver finds a new solution.

        Args:
            cpsolvercb: CP-SAT solver callback
                       Use cpsolvercb.Value(variable) to get variable values
                       Use cpsolvercb.ObjectiveValue() to get the objective value

        Returns:
            RcpspSolution object

        ------------------------------------------------------------------
        TODO: Extract Solution
        ------------------------------------------------------------------
        Build a schedule dict with format: {task_id: {"start_time": s, "end_time": e}}

        1. For each task in self.problem.tasks_list:
           - Get start time: cpsolvercb.Value(self.variables["starts"][task_id])
           - Get end time: cpsolvercb.Value(self.variables["ends"][task_id])
           - Store in schedule dict

        2. Return RcpspSolution(problem=self.problem, rcpsp_schedule=schedule)

        Hint: This is similar to the old TODO 1.5, but using cpsolvercb.Value()
              instead of solver.Value()
        ------------------------------------------------------------------
        """

        # YOUR CODE HERE
        raise NotImplementedError("TODO: Implement retrieve_solution()")

        # After implementing, uncomment this:
        # return RcpspSolution(problem=self.problem, rcpsp_schedule=schedule)


# =============================================================================
# TESTING YOUR IMPLEMENTATION
# =============================================================================

def test_cp_solver():
    """Test your CP-SAT solver on a small instance."""

    print("\n" + "="*80)
    print("  TESTING RCPSP CP-SAT SOLVER")
    print("="*80 + "\n")

    # Load a small instance
    problem = load_instance(instance_name="j301_1")
    print_problem_stats(problem, detailed=True)

    # Compute lower bound
    lower_bound = compute_simple_lower_bound(problem)
    print(f"\nTheoretical lower bound: {lower_bound}\n")

    # Create and solve using discrete-optimization API
    try:
        solver = RcpspCpSatSolver(problem)
        params_cp = ParametersCp.default_cpsat()
        result_storage = solver.solve(
            parameters_cp=params_cp,
            time_limit=30,
            ortools_cpsat_solver_kwargs={"log_search_progress": True}
        )

        if len(result_storage) > 0:
            solution = result_storage.get_best_solution()
            print("\n" + "="*60)
            print("Validating Solution...")
            print("="*60)

            makespan = problem.evaluate(solution)
            is_valid = problem.satisfy(solution)

            print(f"\n✓ Solution found!")
            print(f"  Makespan: {makespan}")
            print(f"  Valid: {is_valid}")
            print(f"  Gap from lower bound: {makespan - lower_bound}")

            if not is_valid:
                print("\n❌ WARNING: Solution is not valid!")
                print("   Check your constraints implementation.")

            # Uncomment to visualize:
            # visualize_solution(problem, solution)
        else:
            print("\n✗ No solution found")

    except NotImplementedError as e:
        print(f"\n❌ {e}")
        print("\nComplete the TODO sections in the RcpspCpSatSolver class.")


def main():
    """Main function to run exercises."""

    print("\n" + "="*80)
    print("  TP1 - PART 1: CP-SAT MODEL FOR RCPSP")
    print("="*80)

    print("\n📝 Complete the TODO sections in RcpspCpSatSolver:")
    print("   1. Create decision variables")
    print("   2. Add precedence constraints")
    print("   3. Add cumulative resource constraints ⭐")
    print("   4. Define objective function")
    print("   5. Extract solution\n")

    print("💡 Key difference from Job Shop:")
    print("   Job Shop → AddNoOverlap (capacity = 1)")
    print("   RCPSP → AddCumulative (capacity >= 1)\n")

    print("Uncomment test_cp_solver() below to test:\n")

    # Uncomment after completing the TODOs:
    # test_cp_solver()

    print("="*80)
    print("  Compare with solutions_part1.py when done.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
