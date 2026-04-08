"""
LESSON 2: Job Shop Problem - EXERCISES

Implement a CP-SAT solver for the Job Shop Scheduling Problem.

EXERCISE: Complete the SolverJobShop class
    - Create decision variables (start, end, interval)
    - Add precedence constraints
    - Add resource constraints
    - Define objective function
    - Extract solution from solver

Instructions:
    - Fill in the TODO sections marked below
    - Run this file to test your implementation
    - Compare your results with solutions.py
"""

from ortools.sat.python import cp_model
from typing import Dict, Tuple

from scheduling.lesson2_cpsat.jobshop_problem import JobShopProblem, SolutionJobshop, Subjob, check_solution
from scheduling.lesson2_cpsat.jobshop_utils import create_simple_example, load_instance, plot_solution, print_problem_stats


class SolverJobShop:
    """
    CP-SAT Solver for Job Shop Scheduling Problem.

    This class encapsulates the CP model for job shop scheduling.
    Students should complete the methods marked with TODO.
    """

    def __init__(self, jobshop_problem: JobShopProblem):
        """
        Initialize the solver with a problem instance.

        Args:
            jobshop_problem: The job shop problem to solve
        """
        self.jobshop_problem = jobshop_problem
        self.model = cp_model.CpModel()
        self.variables = {}

    def init_model(self, **kwargs):
        """
        Initialize the CP model with variables and constraints.

        This method should:
        1. Compute a horizon (upper bound on makespan)
        2. Create decision variables (starts, ends, intervals)
        3. Add precedence constraints (within each job)
        4. Add resource constraints (no overlap on machines)
        5. Define objective (minimize makespan)
        """

        # ----------------------------------------------------------------------
        # STEP 1: Compute Horizon
        # ----------------------------------------------------------------------
        # A safe upper bound for the makespan is the sum of all processing times
        # (assuming all operations are done sequentially)

        horizon = sum(
            subjob.processing_time
            for job in self.jobshop_problem.list_jobs
            for subjob in job
        )

        # ----------------------------------------------------------------------
        # TODO 2.1: Create Decision Variables
        # ----------------------------------------------------------------------
        # For each job and each operation (subjob), create:
        #   - start variable: when the operation starts
        #   - end variable: when the operation ends
        #   - interval variable: represents the operation [start, duration, end]
        #
        # Hint: Loop through jobs and subjobs, use model.NewIntVar and model.NewIntervalVar
        # ----------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 2.1: Create decision variables")

        # ----------------------------------------------------------------------
        # TODO 2.2: Add Precedence Constraints
        # ----------------------------------------------------------------------
        # Within each job, operations must be executed in order.
        # Ensure that operation i+1 starts after operation i ends.
        # Hint: Compare start times and end times of consecutive operations
        # ----------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 2.2: Add precedence constraints")

        # ----------------------------------------------------------------------
        # TODO 2.3: Add Resource Constraints (No Overlap)
        # ----------------------------------------------------------------------
        # Each machine can only process one operation at a time.
        # Use AddNoOverlap constraint on interval variables.
        # Hint: Use self.jobshop_problem.job_per_machines to get operations per machine
        # ----------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 2.3: Add resource (NoOverlap) constraints")

        # ----------------------------------------------------------------------
        # TODO 2.4: Define Objective (Minimize Makespan)
        # ----------------------------------------------------------------------
        # The makespan is the maximum end time across all operations.
        # Hint: Create a makespan variable, use AddMaxEquality, then minimize it
        # ----------------------------------------------------------------------

        # YOUR CODE HERE
        raise NotImplementedError("TODO 2.4: Define objective function")

    def solve(self, max_time_in_seconds: int = 10) -> SolutionJobshop:
        """
        Solve the Job Shop problem using CP-SAT.

        Args:
            max_time_in_seconds: Time limit for the solver

        Returns:
            SolutionJobshop object if a solution is found, None otherwise
        """
        # Initialize the model
        self.init_model()

        # Configure the solver
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_time_in_seconds
        solver.parameters.log_search_progress = True

        # Solve
        print(f"\n{'='*60}")
        print("Solving Job Shop Problem...")
        print(f"{'='*60}")
        status = solver.Solve(self.model)
        status_name = solver.StatusName(status)

        print(f"\nSolver Status: {status_name}")

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"Makespan: {solver.ObjectiveValue()}")

            # ----------------------------------------------------------------------
            # TODO 2.5: Extract Solution
            # ----------------------------------------------------------------------
            # Retrieve variable values from the solver and build the schedule.
            # Structure: schedule[job_id][subjob_id] = (start_time, end_time)
            # Hint: Use solver.Value() on your start/end variables
            # ----------------------------------------------------------------------

            # YOUR CODE HERE
            raise NotImplementedError("TODO 2.5: Extract solution from solver")

        else:
            print("No solution found.")
            return None


# =============================================================================
# TESTING YOUR IMPLEMENTATION
# =============================================================================

def test_simple_example():
    """Test on the simple 3-job, 3-machine example."""

    print("\n" + "="*80)
    print("  TESTING JOB SHOP SOLVER - SIMPLE EXAMPLE")
    print("="*80 + "\n")

    # Create the simple example problem
    problem = create_simple_example()
    print_problem_stats(problem)

    # Create solver and solve
    try:
        solver = SolverJobShop(jobshop_problem=problem)
        solution = solver.solve(max_time_in_seconds=10)

        if solution is not None:
            print("\n" + "="*60)
            print("Validating Solution...")
            print("="*60)
            is_valid = check_solution(solution, problem, verbose=True)

            if is_valid:
                print(f"\n✓ Solution is valid!")
                print(f"  Makespan: {solution.get_makespan()}")

                # Uncomment to show visualization:
                # print("\nGenerating visualization...")
                import matplotlib.pyplot as plt
                fig, ax = plot_solution(solution, problem)
                plt.show()
            else:
                print("\n❌ Solution is NOT valid. Check your implementation!")

    except NotImplementedError as e:
        print(f"\n❌ {e}")
        print("\nComplete the TODO sections in the SolverJobShop class.")


def main():
    """Main function to run exercises."""

    print("\n" + "="*80)
    print("  LESSON 2: JOB SHOP SCHEDULING - EXERCISES")
    print("="*80)

    print("\n📝 Complete the TODO sections in the SolverJobShop class:")
    print("   1. Create decision variables (starts, ends, intervals)")
    print("   2. Add precedence constraints")
    print("   3. Add resource constraints (NoOverlap)")
    print("   4. Define objective function (minimize makespan)")
    print("   5. Extract solution from solver\n")

    print("💡 Uncomment test_simple_example() below to test:\n")

    # Uncomment after completing the exercises:
    # test_simple_example()

    print("="*80)
    print("  Compare your solution with solutions.py when done.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
