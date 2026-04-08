"""
TP2 - Part 1: CP-SAT Solver for Resource-Constrained Assembly Line Balancing

Implement a complete CP-SAT solver for the RC-ALBP problem.

KEY DIFFERENCES FROM RCPSP/JOB SHOP:
    - Fixed stations: Tasks must be assigned to specific stations
    - Two types of precedence:
        * Station precedence: pred_station ≤ succ_station
        * Temporal precedence: pred_end ≤ succ_start (if same station)
    - Resources per station: Each station has its own resource allocation

Complete the TODOs to build your solver.

This version uses discrete-optimization's OrtoolsCpSatSolver API for cleaner code.
"""

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpSolverSolutionCallback
from typing import Dict, List

from scheduling.tp2_assembly_line_balancing.problem import (
    RCALBPProblem,
    RCALBPSolution,
    Task,
    Station,
)
from scheduling.tp2_assembly_line_balancing.utils import (
    create_precedence_example,
    create_simple_instance,
    visualize_solution,
    print_solution_info,
)
from discrete_optimization.generic_tools.ortools_cpsat_tools import OrtoolsCpSatSolver
from discrete_optimization.generic_tools.cp_tools import ParametersCp


class RCALBPCpSatSolver(OrtoolsCpSatSolver):
    """
    CP-SAT Solver for Resource-Constrained Assembly Line Balancing.

    Students should complete the methods marked with TODO.

    Inherits from discrete-optimization's OrtoolsCpSatSolver for automatic solve() handling.
    You only need to implement init_model() and retrieve_solution()!
    """
    problem: RCALBPProblem
    def __init__(self, problem: RCALBPProblem):
        """
        Initialize the solver.

        Args:
            problem: RCALBPProblem instance
        """
        super().__init__(problem)
        self.variables = {}

    def init_model(self, **kwargs):
        """
        Initialize the CP model with variables and constraints.

        Note: When using discrete-optimization's OrtoolsCpSatSolver, you must:
        1. Call super().init_model(**kwargs) to create self.cp_model
        2. Use self.cp_model instead of self.model for all CP-SAT operations

        This method should:
        1. Compute a horizon (upper bound on cycle time)
        2. Create decision variables:
           - Task assignment to stations
           - Start times for tasks
           - Interval variables for tasks
        3. Add station precedence constraints
        4. Add temporal precedence constraints (same station)
        5. Add resource constraints (cumulative per station)
        6. Define objective (minimize cycle time)
        """
        # Call parent to create self.cp_model
        super().init_model(**kwargs)

        # ------------------------------------------------------------------
        # STEP 1: Compute Horizon
        # ------------------------------------------------------------------
        # Upper bound: all tasks on one station sequentially
        horizon = sum(self.problem.task_times.values())

        # ------------------------------------------------------------------
        # TODO 1.1: Create Task Assignment Variables
        # ------------------------------------------------------------------
        # For each task, create an integer variable indicating which station
        # it is assigned to.
        # Hint: Use NewIntVar with domain [0, nb_stations-1]
        # Hint: Store in self.variables["task_station"]
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.1: Create task assignment variables")

        # ------------------------------------------------------------------
        # TODO 1.2: Create Start Time and Interval Variables
        # ------------------------------------------------------------------
        # For each task, create:
        # - Start time variable
        # - End time variable (or compute from start + duration)
        # - Interval variable
        # Hint: Similar to RCPSP/Job Shop, but simpler (no modes)
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.2: Create start time and interval variables")

        # ------------------------------------------------------------------
        # TODO 1.3: Add Station Precedence Constraints
        # ------------------------------------------------------------------
        # For each precedence (pred, succ) in problem.precedences:
        #   station[pred] ≤ station[succ]
        # This ensures tasks flow forward through the assembly line.
        # Hint: Use model.Add() with the assignment variables
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.3: Add station precedence constraints")

        # ------------------------------------------------------------------
        # TODO 1.4: Add Temporal Precedence Constraints (Same Station)
        # ------------------------------------------------------------------
        # For each precedence (pred, succ):
        #   If both tasks are on the same station, then:
        #     end[pred] ≤ start[succ]
        # Hint: Use OnlyEnforceIf to make this conditional
        # Hint: Create a boolean variable: same_station = (station[pred] == station[succ])
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.4: Add temporal precedence for same station")

        # ------------------------------------------------------------------
        # TODO 1.5: Add Resource Constraints (Cumulative per Station)
        # ------------------------------------------------------------------
        # For each station s and each resource r:
        #   - Collect intervals of tasks assigned to station s
        #   - Collect their demands for resource r
        #   - Add cumulative constraint with station's capacity
        #
        # KEY CHALLENGE: How to filter tasks by station?
        # Hint: You cannot use Python if-statements in CP model building
        # Hint: Use optional intervals! Create interval per (task, station) pair
        # Hint: Interval is "present" only if task is assigned to that station
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.5: Add resource constraints per station")

        # ------------------------------------------------------------------
        # TODO 1.6: Define Objective (Minimize Cycle Time)
        # ------------------------------------------------------------------
        # Cycle time = maximum end time across all tasks
        # Hint: Create a makespan variable
        # Hint: Use AddMaxEquality to set it to max of all end times
        # Hint: Minimize this makespan
        # ------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 1.6: Define objective function")

    def retrieve_solution(self, cpsolvercb: CpSolverSolutionCallback) -> RCALBPSolution:
        """
        Extract solution from CP-SAT solver callback.

        This method is called automatically by discrete-optimization's OrtoolsCpSatSolver
        each time the CP-SAT solver finds a new solution.

        Args:
            cpsolvercb: CP-SAT solver callback object
                       Use cpsolvercb.Value(variable) to get variable values
                       Use cpsolvercb.ObjectiveValue() to get the objective value

        Returns:
            RCALBPSolution object containing:
                - task_assignment: dict mapping each task to its assigned station
                - task_schedule: dict mapping each task to its start time
                - cycle_time: the makespan (maximum end time)

        ------------------------------------------------------------------
        TODO: Extract Solution
        ------------------------------------------------------------------
        You need to:
        1. Get the stored variables from self.variables:
           - starts: dict of start time variables
           - task_station: dict of station assignment variables
           - idx_to_station: dict to map station indices to station identifiers

        2. For each task in self.problem.tasks:
           - Get station index using: cpsolvercb.Value(task_station[task])
           - Convert to station identifier using: idx_to_station[station_idx]
           - Get start time using: cpsolvercb.Value(starts[task])

        3. Get the cycle time using: cpsolvercb.ObjectiveValue()

        4. Return RCALBPSolution with the extracted data

        Hint: This is similar to what you did in TODO 1.7, but now using
              cpsolvercb.Value() instead of solver.Value()
        ------------------------------------------------------------------
        """

        # YOUR CODE HERE
        raise NotImplementedError("TODO: Implement retrieve_solution()")

        # After implementing, uncomment and complete this:
        # return RCALBPSolution(
        #     problem=self.problem,
        #     task_assignment=task_assignment,
        #     task_schedule=task_schedule,
        #     cycle_time=cycle_time,
        # )


# =============================================================================
# TESTING YOUR IMPLEMENTATION
# =============================================================================

def run_cp_solver():
    """Test your CP-SAT solver on the example instance."""

    print("\n" + "="*80)
    print("  TESTING RC-ALBP CP-SAT SOLVER")
    print("="*80 + "\n")

    # Load the precedence example
    problem = create_precedence_example()

    print("Problem:")
    print(f"  Tasks: {problem.tasks}")
    print(f"  Stations: {problem.stations}")
    print(f"  Resources: {problem.resources}")
    print(f"  Precedences: {len(problem.precedences)} constraints")

    # Create and solve using discrete-optimization API
    try:
        solver = RCALBPCpSatSolver(problem)
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

            eval_dict = problem.evaluate(solution)
            is_valid = problem.satisfy(solution)

            print(f"\n✓ Solution found!")
            print(f"  Cycle Time: {solution.cycle_time}")
            print(f"  Valid: {is_valid}")

            if not is_valid:
                print("\n❌ WARNING: Solution is not valid!")
                print("   Violations:")
                for key, value in eval_dict.items():
                    if 'penalty' in key and value > 0:
                        print(f"     {key}: {value}")

            # Print detailed info
            print_solution_info(problem, solution)

            # Uncomment to visualize:
            # visualize_solution(problem, solution)
        else:
            print("\n✗ No solution found")

    except NotImplementedError as e:
        print(f"\n❌ {e}")
        print("\nComplete the TODO sections in the RCALBPCpSatSolver class.")


def main():
    """Main function to run exercises."""

    print("\n" + "="*80)
    print("  TP2 - PART 1: CP-SAT MODEL FOR RC-ALBP")
    print("="*80)

    print("\n📝 Complete the TODO sections in RCALBPCpSatSolver:")
    print("   1. Create task assignment variables")
    print("   2. Create start time and interval variables")
    print("   3. Add station precedence constraints")
    print("   4. Add temporal precedence (same station)")
    print("   5. Add resource constraints (cumulative per station) ⭐")
    print("   6. Define objective function")
    print("   7. Extract solution\n")

    print("💡 Key difference from RCPSP:")
    print("   - RCPSP: Global resources")
    print("   - RC-ALBP: Resources per station (use optional intervals!)\\n")

    print("💡 Key modeling challenge:")
    print("   How to filter tasks by station in constraints?")
    print("   → Use optional intervals!")
    print("   → Create interval per (task, station) pair")
    print("   → Mark as 'present' only if task assigned to that station\\n")

    print("Uncomment test_cp_solver() below to test:\\n")

    # Uncomment after completing the TODOs:
    # run_cp_solver()

    print("="*80)
    print("  Compare with solutions.py when done.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
