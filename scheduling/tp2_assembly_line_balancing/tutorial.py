"""
TP2 - Tutorial: Resource-Constrained Assembly Line Balancing

This tutorial demonstrates:
1. Problem structure and data model
2. Creating problem instances
3. Understanding solutions
4. Basic visualization
"""

from scheduling.tp2_assembly_line_balancing.problem import RCALBPProblem, RCALBPSolution
from scheduling.tp2_assembly_line_balancing.utils import (
    create_precedence_example,
    visualize_solution,
    print_solution_info,
)


def main():
    print("\n" + "=" * 80)
    print("  TP2 TUTORIAL: RESOURCE-CONSTRAINED ASSEMBLY LINE BALANCING")
    print("=" * 80 + "\n")

    # =========================================================================
    # PART 1: Problem Structure
    # =========================================================================
    print("=" * 80)
    print("PART 1: Problem Structure")
    print("=" * 80 + "\n")

    problem = create_precedence_example()

    print("Problem Components:")
    print(f"  - Stations: {problem.nb_stations}")
    print(f"  - Tasks: {problem.nb_tasks}")
    print(f"  - Resources: {problem.nb_resources}")
    print(f"  - Precedences: {len(problem.precedences)} constraints")

    print("\nTask Processing Times:")
    for task in problem.tasks:
        print(f"  Task {task}: {problem.task_times[task]} time units")

    print("\nPrecedence Constraints:")
    for pred, succ in problem.precedences:
        print(f"  Task {pred} → Task {succ}")

    print("\nStation Resource Allocation:")
    for station in problem.stations:
        print(f"  Station {station}:")
        for resource in problem.resources:
            capacity = problem.station_resources.get((resource, station), 0)
            print(f"    Resource {resource}: {capacity} units")

    print("\nTask Resource Consumption:")
    for task in problem.tasks:
        print(f"  Task {task}:")
        for resource in problem.resources:
            consumption = problem.task_resources.get((resource, task), 0)
            if consumption > 0:
                print(f"    Resource {resource}: {consumption} units")

    # =========================================================================
    # PART 2: Solution Structure
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 2: Solution Structure")
    print("=" * 80 + "\n")

    # Get dummy solution
    solution = problem.get_dummy_solution()

    print("Solution Components:")
    print(f"  - Task Assignment: {len(solution.task_assignment)} tasks assigned")
    print(f"  - Task Schedule: {len(solution.task_schedule)} tasks scheduled")
    print(f"  - Cycle Time: {solution.cycle_time}")

    print("\nTask Assignments:")
    for task in problem.tasks:
        station = solution.task_assignment.get(task, -1)
        start = solution.task_schedule.get(task, -1)
        duration = problem.task_times[task]
        print(f"  Task {task}: Station {station}, Start={start}, Duration={duration}")

    # =========================================================================
    # PART 3: Solution Evaluation
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 3: Solution Evaluation")
    print("=" * 80 + "\n")

    eval_dict = problem.evaluate(solution)
    print("Evaluation Metrics:")
    for key, value in eval_dict.items():
        print(f"  {key}: {value}")

    is_valid = problem.satisfy(solution)
    print(f"\nSolution Valid: {is_valid}")

    # =========================================================================
    # PART 4: Visualization
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 4: Visualization")
    print("=" * 80 + "\n")

    print("Generating Gantt chart...")
    print_solution_info(problem, solution)

    # Visualize (close window to continue)
    visualize_solution(problem, solution, show=True)


    print("\n" + "=" * 80)
    print("  TUTORIAL COMPLETE")
    print("=" * 80 + "\n")

    print("Next Steps:")
    print("  1. Try the exercises in exercises.py")
    print("  2. Implement a greedy heuristic")
    print("  3. Implement a CP-SAT solver")
    print("  4. Compare different solving approaches\n")


if __name__ == "__main__":
    main()
