"""
LESSON 2: Job Shop Problem - SOLUTIONS

Complete reference implementation of the CP-SAT solver for Job Shop Scheduling.
"""

from ortools.sat.python import cp_model

from scheduling.lesson2_cpsat.jobshop_problem import JobShopProblem, SolutionJobshop, check_solution
from scheduling.lesson2_cpsat.jobshop_utils import create_simple_example, load_instance, plot_solution, print_problem_stats


class SolverJobShop:
    """Complete CP-SAT solver implementation for Job Shop Scheduling."""

    def __init__(self, jobshop_problem: JobShopProblem):
        self.jobshop_problem = jobshop_problem
        self.model = cp_model.CpModel()
        self.variables = {}

    def init_model(self, **kwargs):
        """Initialize the complete CP model."""

        # Compute horizon (upper bound on makespan)
        horizon = sum(
            subjob.processing_time
            for job in self.jobshop_problem.list_jobs
            for subjob in job
        )

        # Create decision variables
        starts = {}
        ends = {}
        intervals = {}

        for job_id in range(self.jobshop_problem.n_jobs):
            for subjob_id in range(len(self.jobshop_problem.list_jobs[job_id])):
                duration = self.jobshop_problem.list_jobs[job_id][subjob_id].processing_time

                start = self.model.NewIntVar(0, horizon, f"start_{job_id}_{subjob_id}")
                end = self.model.NewIntVar(0, horizon, f"end_{job_id}_{subjob_id}")
                interval = self.model.NewIntervalVar(
                    start, duration, end, f"interval_{job_id}_{subjob_id}"
                )

                starts[(job_id, subjob_id)] = start
                ends[(job_id, subjob_id)] = end
                intervals[(job_id, subjob_id)] = interval

        self.variables["starts"] = starts
        self.variables["ends"] = ends
        self.variables["intervals"] = intervals

        # Add precedence constraints
        for job_id in range(self.jobshop_problem.n_jobs):
            for subjob_id in range(1, len(self.jobshop_problem.list_jobs[job_id])):
                self.model.Add(
                    starts[(job_id, subjob_id)] >= ends[(job_id, subjob_id - 1)]
                )

        # Add resource constraints (NoOverlap per machine)
        for machine_id in range(self.jobshop_problem.n_machines):
            machine_intervals = [
                intervals[(job_id, subjob_id)]
                for (job_id, subjob_id) in self.jobshop_problem.job_per_machines[machine_id]
            ]
            self.model.AddNoOverlap(machine_intervals)

        # Define objective (minimize makespan)
        makespan = self.model.NewIntVar(0, horizon, 'makespan')
        self.model.AddMaxEquality(makespan, list(ends.values()))
        self.model.Minimize(makespan)

    def solve(self, max_time_in_seconds: int = 10) -> SolutionJobshop:
        """Solve the Job Shop problem."""

        self.init_model()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_time_in_seconds
        solver.parameters.log_search_progress = True

        print(f"\n{'='*60}")
        print("Solving Job Shop Problem...")
        print(f"{'='*60}")
        status = solver.Solve(self.model)
        status_name = solver.StatusName(status)

        print(f"\nSolver Status: {status_name}")

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            print(f"Makespan: {solver.ObjectiveValue()}")

            # Extract solution
            schedule = []
            for job_id in range(self.jobshop_problem.n_jobs):
                job_schedule = []
                for subjob_id in range(len(self.jobshop_problem.list_jobs[job_id])):
                    start_val = solver.Value(self.variables["starts"][(job_id, subjob_id)])
                    end_val = solver.Value(self.variables["ends"][(job_id, subjob_id)])
                    job_schedule.append((start_val, end_val))
                schedule.append(job_schedule)

            return SolutionJobshop(schedule=schedule)
        else:
            print("No solution found.")
            return None


def demonstrate_solution():
    """Demonstrate the complete solution."""

    print("\n" + "="*80)
    print("  JOB SHOP SOLVER - SOLUTION DEMONSTRATION")
    print("="*80 + "\n")

    # Test 1: Simple example
    print("="*80)
    print("TEST 1: Simple 3x3 Example")
    print("="*80 + "\n")

    problem = create_simple_example()
    print_problem_stats(problem)

    solver = SolverJobShop(jobshop_problem=problem)
    solution = solver.solve(max_time_in_seconds=10)

    if solution is not None:
        print("\n" + "="*60)
        print("Validating Solution...")
        print("="*60)
        is_valid = check_solution(solution, problem, verbose=True)

        print(f"\n✓ Solution validated!")
        print(f"  Makespan: {solution.get_makespan()}")

    # Test 2: Benchmark instance from file
    print("\n" + "="*80)
    print("TEST 2: Fisher & Thompson 6x6 Instance (ft06)")
    print("="*80 + "\n")

    try:
        problem2 = load_instance("ft06")
        print(f"✓ Loaded instance: {problem2}")
        print_problem_stats(problem2)

        solver2 = SolverJobShop(jobshop_problem=problem2)
        solution2 = solver2.solve(max_time_in_seconds=30)

        if solution2 is not None:
            print("\n" + "="*60)
            is_valid2 = check_solution(solution2, problem2, verbose=False)

            print(f"\n✓ Solution validated!")
            print(f"  Makespan: {solution2.get_makespan()}")
            print(f"  Valid: {is_valid2}")

            # Uncomment to show visualization:
            # print("\nGenerating visualization...")
            fig, ax = plot_solution(solution2, problem2)
            import matplotlib.pyplot as plt
            plt.show()

    except FileNotFoundError as e:
        print(f"✗ Could not load instance: {e}")

    print("\n" + "="*80)
    print("  DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    demonstrate_solution()