"""
LESSON 1: RCPSP - EXERCISES

Complete the following exercises to solidify your understanding of RCPSP and SGS.

EXERCISE 1: Implement the Serial Generation Scheme (SGS)
EXERCISE 2: Implement different priority rules
EXERCISE 3: Implement a simple random search to improve solutions

Instructions:
    - Fill in the TODO sections marked below
    - Run this file to test your implementation
    - Compare your results with solutions.py
"""
import random
from typing import List, Dict, Set, Hashable

from discrete_optimization.rcpsp.problem import RcpspProblem, RcpspSolution
from discrete_optimization.rcpsp.parser import get_data_available, parse_file
from discrete_optimization.datasets import fetch_data_from_psplib
from discrete_optimization.rcpsp.solvers.cpm import CpmRcpspSolver
from scheduling.utils.rcpsp_utils import (compute_predecessors,
    get_task_durations,
    get_resource_consumption,
    initialize_resource_availability,
    create_empty_schedule,
    compute_makespan,)

# =============================================================================
# EXERCISE 1: Implement the Serial Generation Scheme (SGS)
# =============================================================================

def sgs_algorithm(
    rcpsp_problem: RcpspProblem,
    permutation_of_tasks: List[Hashable]
) -> Dict[Hashable, Dict[str, int]]:
    """
    Implement the Serial Generation Scheme to build a feasible schedule.

    Given a permutation (priority ordering) of tasks, schedule them one by one
    at the earliest feasible time considering:
        1. Precedence constraints (all predecessors must be finished)
        2. Resource constraints (resources must be available)

    Args:
        rcpsp_problem: The RCPSP problem instance
        permutation_of_tasks: Ordered list of tasks (priority order)

    Returns:
        Schedule dictionary: {task_id: {"start_time": t1, "end_time": t2}}
    """

    # ----------------------------------------------------------------------
    # SETUP: Use utility functions to prepare data structures
    # ----------------------------------------------------------------------

    predecessors = compute_predecessors(rcpsp_problem)
    duration_task = get_task_durations(rcpsp_problem)
    resource_consumption = get_resource_consumption(rcpsp_problem)
    schedule = create_empty_schedule(rcpsp_problem)
    resource_availability = initialize_resource_availability(rcpsp_problem)

    # Track which tasks have been completed
    completed_tasks = set()

    # ----------------------------------------------------------------------
    # TODO 1.1: Schedule the source task at time 0
    # ----------------------------------------------------------------------
    source_task = rcpsp_problem.source_task

    # YOUR CODE HERE
    # Hint: Source task starts at 0, has duration 0

    raise NotImplementedError("TODO 1.1: Schedule source task")

    # ----------------------------------------------------------------------
    # TODO 1.2: Main loop - schedule remaining tasks
    # ----------------------------------------------------------------------

    while len(completed_tasks) < rcpsp_problem.n_jobs:

        # ------------------------------------------------------------------
        # TODO 1.3: Find the next eligible task from the permutation
        # ------------------------------------------------------------------
        # Eligibility: task not scheduled yet AND all predecessors completed
        # Hint: Use predecessors[task] to check if all predecessors are in completed_tasks
        # ------------------------------------------------------------------

        next_task = None

        # YOUR CODE HERE

        raise NotImplementedError("TODO 1.3: Find next eligible task")

        if next_task is None:
            raise ValueError("No eligible task found!")

        # ------------------------------------------------------------------
        # TODO 1.4: Compute earliest start time from precedence constraints
        # ------------------------------------------------------------------
        # The task must start after all its predecessors have finished
        # Hint: Look at schedule[pred]["end_time"] for each predecessor
        # ------------------------------------------------------------------

        earliest_start_by_precedence = 0

        # YOUR CODE HERE

        raise NotImplementedError("TODO 1.4: Compute earliest start by precedence")

        # ------------------------------------------------------------------
        # TODO 1.5: Find actual start time considering resource availability
        # ------------------------------------------------------------------
        # From earliest_start_by_precedence onwards, find first time slot
        # where all resources are available for the full task duration
        # Hint: Loop through time slots starting from earliest_start_by_precedence
        #       For each time t, check if resource_availability arrays have
        #       enough capacity from t to t+duration for all required resources
        # ------------------------------------------------------------------

        task_duration = duration_task[next_task]
        task_resources = resource_consumption[next_task]

        start_time = earliest_start_by_precedence

        # YOUR CODE HERE
        # Loop to find feasible start_time

        raise NotImplementedError("TODO 1.5: Find feasible start time")

        # ------------------------------------------------------------------
        # TODO 1.6: Schedule the task and update resources
        # ------------------------------------------------------------------
        # Schedule the task, then decrease resource_availability arrays
        # for the time period [start_time, start_time + task_duration)
        # ------------------------------------------------------------------

        schedule[next_task] = {
            "start_time": start_time,
            "end_time": start_time + task_duration
        }

        # YOUR CODE HERE
        # Update resource_availability arrays

        raise NotImplementedError("TODO 1.6: Update resource availability")

        # Mark task as completed
        completed_tasks.add(next_task)

    return schedule


# =============================================================================
# EXERCISE 2: Implement Priority Rules
# =============================================================================

def create_priority_permutation(
    rcpsp_problem: RcpspProblem,
    rule: str = "random"
) -> List[Hashable]:
    """
    Create a task permutation based on a priority rule.

    Args:
        rcpsp_problem: The RCPSP problem instance
        rule: Priority rule name ("random", "esd", "efd", "lsd", "lfd")

    Returns:
        List of tasks in priority order
    """

    tasks = list(rcpsp_problem.tasks_list)

    if rule == "random":
        random.shuffle(tasks)
        return tasks

    elif rule in ["esd", "efd", "lsd", "lfd"]:
        # Compute CPM to get timing information
        cpm_solver = CpmRcpspSolver(rcpsp_problem)
        cpm_solver.run_classic_cpm()

        # TODO 2.1: Sort tasks based on the selected rule
        # Hint: Use cpm_solver.map_node[task]._ESD, _EFD, _LSD, or _LFD
        #       Return sorted(tasks, key=lambda x: ...)

        if rule == "esd":
            # YOUR CODE HERE - sort by Earliest Start Date
            raise NotImplementedError("TODO 2.1: Implement ESD rule")

        elif rule == "efd":
            # YOUR CODE HERE - sort by Earliest Finish Date
            raise NotImplementedError("TODO 2.1: Implement EFD rule")

        elif rule == "lsd":
            # YOUR CODE HERE - sort by Latest Start Date
            raise NotImplementedError("TODO 2.1: Implement LSD rule")

        elif rule == "lfd":
            # YOUR CODE HERE - sort by Latest Finish Date
            raise NotImplementedError("TODO 2.1: Implement LFD rule")

    else:
        raise ValueError(f"Unknown priority rule: {rule}")


# =============================================================================
# EXERCISE 3: Implement Simple Random Search
# =============================================================================

def random_search_sgs(
    rcpsp_problem: RcpspProblem,
    n_iterations: int = 1000
) -> RcpspSolution:
    """
    Improve SGS solutions through random search.

    Try many random permutations and keep the best solution found.

    Args:
        rcpsp_problem: The RCPSP problem instance
        n_iterations: Number of random permutations to try

    Returns:
        Best solution found
    """

    best_makespan = float('inf')
    best_schedule = None

    print(f"🔍 Running random search with {n_iterations} iterations...")

    for i in range(n_iterations):
        # TODO 3.1: Implement the random search loop
        # Hint:
        #   - Create a random permutation using create_priority_permutation()
        #   - Run sgs_algorithm() with that permutation
        #   - Compute makespan using compute_makespan() or schedule[sink_task]["end_time"]
        #   - Track and update best solution if current is better

        # YOUR CODE HERE

        raise NotImplementedError("TODO 3.1: Implement random search loop")

        if (i + 1) % 100 == 0:
            print(f"   Iteration {i+1}/{n_iterations}, Best makespan: {best_makespan}")

    solution = RcpspSolution(problem=rcpsp_problem, rcpsp_schedule=best_schedule)

    print(f"\n✓ Search complete! Best makespan: {best_makespan}")

    return solution


# =============================================================================
# TESTING YOUR IMPLEMENTATION
# =============================================================================

def test_sgs():
    """Test your SGS implementation."""

    print("\n" + "="*80)
    print("  TESTING YOUR SGS IMPLEMENTATION")
    print("="*80 + "\n")

    # Load a problem
    try:
        files = get_data_available()
    except:
        fetch_data_from_psplib()
        files = get_data_available()

    filepath = [f for f in files if "j301_1.sm" in f][0]
    rcpsp_problem = parse_file(filepath)

    print(f"📁 Loaded: {filepath.split('/')[-1]}")
    print(f"   Tasks: {rcpsp_problem.n_jobs}, Resources: {rcpsp_problem.resources}\n")

    # Test random permutation
    print("Test 1: Random permutation")
    print("-" * 40)
    random_perm = list(rcpsp_problem.tasks_list)
    random.shuffle(random_perm)

    try:
        schedule = sgs_algorithm(rcpsp_problem, random_perm)
        solution = RcpspSolution(problem=rcpsp_problem, rcpsp_schedule=schedule)
        makespan = rcpsp_problem.evaluate(solution)["makespan"]
        is_feasible = rcpsp_problem.satisfy(solution)

        print(f"✓ SGS completed! Makespan: {makespan}, Feasible: {is_feasible}\n")

        if not is_feasible:
            print("⚠️  Warning: Solution not feasible! Check your implementation.\n")

    except NotImplementedError as e:
        print(f"❌ {e}\n")
        return

    # Test priority rules
    print("Test 2: Priority rules")
    print("-" * 40)
    for rule in ["esd", "efd", "lsd", "lfd"]:
        try:
            perm = create_priority_permutation(rcpsp_problem, rule=rule)
            schedule = sgs_algorithm(rcpsp_problem, perm)
            solution = RcpspSolution(problem=rcpsp_problem, rcpsp_schedule=schedule)
            makespan = rcpsp_problem.evaluate(solution)["makespan"]
            print(f"   {rule.upper():4s}: makespan = {makespan}")
        except NotImplementedError:
            print(f"   {rule.upper():4s}: not implemented")
    print()


def main():
    """Main function to run exercises."""

    print("\n" + "="*80)
    print("  LESSON 1: RCPSP EXERCISES")
    print("="*80)

    print("\n📝 Complete the TODO sections in this file:")
    print("   1. Implement the Serial Generation Scheme (SGS)")
    print("   2. Implement priority rules for task ordering")
    print("   3. Implement random search to improve solutions\n")

    print("💡 Uncomment test_sgs() below to test your implementation\n")

    # Uncomment after completing exercises:
    # test_sgs()

    print("="*80)
    print("  Compare your solution with solutions.py when done.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
