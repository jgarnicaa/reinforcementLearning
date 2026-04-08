"""
LESSON 1: Introduction to Resource Constrained Project Scheduling Problems (RCPSP)

This tutorial introduces the fundamentals of RCPSP through a hands-on exploration:
    - Loading and parsing problem instances from the PSPLib benchmark library
    - Understanding problem structure (tasks, precedences, resources)
    - Visualizing precedence graphs
    - Computing the critical path (lower bound on project duration)
    - Understanding the Serial Generation Scheme (SGS) heuristic

Author: g-poveda powered by Claude.
"""

import logging
from typing import List, Dict, Set, Tuple, Hashable
import networkx as nx

from discrete_optimization.datasets import fetch_data_from_psplib
from discrete_optimization.rcpsp.problem import RcpspProblem
from discrete_optimization.rcpsp.parser import get_data_available, parse_file
from discrete_optimization.rcpsp.solvers.cpm import CpmRcpspSolver

from scheduling.utils.visualization import plot_predecessors_graph, plot_gantt_chart
from scheduling.utils.rcpsp_utils import compute_predecessors, get_task_durations

logging.basicConfig(level=logging.INFO)


# =============================================================================
# PART 1: Data Loading and Problem Exploration
# =============================================================================

def ensure_datasets_available(required_datasets: List[str] = None) -> None:
    """
    Check if required PSPLib datasets are available locally.
    Download them if necessary.

    PSPLib is a standard benchmark library for project scheduling problems:
    https://www.om-db.wi.tum.de/psplib/

    Args:
        required_datasets: List of dataset names (e.g., ["j301_1.sm"])
    """
    if required_datasets is None:
        required_datasets = ["j301_1.sm"]

    download_needed = False

    try:
        files_available = get_data_available()
        for dataset in required_datasets:
            if not any(dataset in f for f in files_available):
                download_needed = True
                break
    except Exception:
        download_needed = True

    if download_needed:
        print("📥 Downloading PSPLib datasets (this may take a moment)...")
        fetch_data_from_psplib()
        print("✓ Download complete!\n")
    else:
        print("✓ Datasets already available\n")


def load_and_inspect_problem(instance_name: str = "j301_1.sm") -> RcpspProblem:
    """
    Load a RCPSP instance and display its key characteristics.

    The file format (PSPLib standard):
        - Section 1: Precedence constraints (which tasks must finish before others)
        - Section 2: Resource requirements and durations for each task

    Args:
        instance_name: Name of the instance file to load

    Returns:
        Parsed RcpspProblem object
    """
    # Find the file path
    files = get_data_available()
    filepath = next((f for f in files if instance_name in f), None)

    if filepath is None:
        raise FileNotFoundError(f"Instance {instance_name} not found")

    print(f"📁 Loading instance: {instance_name}")
    print(f"   Path: {filepath}\n")

    # Show a preview of the raw file content
    print("File preview (first 20 lines):")
    print("-" * 60)
    with open(filepath, "rt") as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            print(f"  {line.rstrip()}")
    print("-" * 60 + "\n")

    # Parse the file into a structured problem object
    rcpsp_problem = parse_file(filepath)

    # Display key problem characteristics
    print("📊 Problem Characteristics:")
    print(f"   • Number of tasks: {rcpsp_problem.n_jobs}")
    print(f"   • Resources: {rcpsp_problem.resources}")
    print(f"   • Source task (dummy start): {rcpsp_problem.source_task}")
    print(f"   • Sink task (dummy end): {rcpsp_problem.sink_task}\n")

    # Show example precedence constraints
    print("🔗 Example precedence constraints:")
    for i, task in enumerate(list(rcpsp_problem.tasks_list)[:5]):
        successors = rcpsp_problem.successors.get(task, [])
        if successors:
            print(f"   Task {task:2d} must complete before: {successors}")
    print()

    # Use our utility function to show predecessors too
    predecessors = compute_predecessors(rcpsp_problem)
    print("🔙 Example predecessors (reverse view):")
    for i, task in enumerate(list(rcpsp_problem.tasks_list)[2:7]):
        preds = predecessors.get(task, set())
        if preds:
            print(f"   Task {task:2d} requires completion of: {preds}")
    print()

    return rcpsp_problem


# =============================================================================
# PART 2: Critical Path Analysis
# =============================================================================

def compute_critical_path_networkx(rcpsp_problem: RcpspProblem):
    """
    Compute the critical path using NetworkX's longest path algorithm.

    The critical path represents the longest sequence of dependent tasks
    and provides a LOWER BOUND on the project duration (assuming infinite resources).

    Algorithm:
        1. Convert precedence graph to NetworkX format
        2. Add edge weights = task durations
        3. Find longest path using dynamic programming

    Args:
        rcpsp_problem: The RCPSP problem instance

    Returns:
        Tuple of (critical_path, critical_path_duration)
    """
    print("🔍 Computing Critical Path (Method 1: NetworkX)...")

    # Convert to NetworkX graph
    graph_nx = rcpsp_problem.graph.to_networkx()

    # Use our utility function to get durations
    durations = get_task_durations(rcpsp_problem)

    # Add edge weights based on minimum task duration
    for edge in graph_nx.edges():
        task = edge[1]
        graph_nx[edge[0]][edge[1]]["min_duration"] = durations[task]

        # Special case: edges to sink task have duration 0
        if task == rcpsp_problem.sink_task:
            graph_nx[edge[0]][edge[1]]["min_duration"] = 0

    # Find longest path (critical path)
    path = nx.dag_longest_path(G=graph_nx, weight='min_duration', default_weight=1)

    # Compute total duration
    edges = [(n1, n2) for n1, n2 in zip(path[:-1], path[1:])]
    duration = sum(graph_nx[n[0]][n[1]]["min_duration"] for n in edges)

    print(f"   ✓ Critical path: {path[:10]}{'...' if len(path) > 10 else ''}")
    print(f"   ✓ Duration (lower bound): {duration}\n")

    return path, duration


def compute_critical_path_cpm(rcpsp_problem: RcpspProblem) -> CpmRcpspSolver:
    """
    Compute the critical path using the Critical Path Method (CPM).

    CPM performs a forward and backward pass through the precedence graph to compute:
        - ESD (Earliest Start Date): earliest time a task can start
        - EFD (Earliest Finish Date): earliest time a task can finish
        - LSD (Latest Start Date): latest time a task can start without delaying project
        - LFD (Latest Finish Date): latest time a task can finish without delaying project

    Tasks where ESD = LSD (no slack) form the critical path.

    Args:
        rcpsp_problem: The RCPSP problem instance

    Returns:
        CpmRcpspSolver instance with computed values
    """
    print("🔍 Computing Critical Path (Method 2: CPM Algorithm)...")

    solver = CpmRcpspSolver(rcpsp_problem)
    critical_path = solver.run_classic_cpm()

    min_project_duration = solver.map_node[rcpsp_problem.sink_task]._EFD

    print(f"   ✓ Critical path: {critical_path[:10]}{'...' if len(critical_path) > 10 else ''}")
    print(f"   ✓ Minimum project duration: {min_project_duration}\n")

    # Display scheduling information for a few tasks
    print("   Task scheduling information (sample):")
    print(f"   {'Task':<8} {'ESD':<8} {'EFD':<8} {'LSD':<8} {'LFD':<8} {'Slack':<8}")
    print(f"   {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    for task in list(rcpsp_problem.tasks_list)[1:6]:  # Skip source task
        node = solver.map_node[task]
        slack = node._LSD - node._ESD  # Slack = how much delay is tolerable
        print(f"   {task:<8} {node._ESD:<8} {node._EFD:<8} "
              f"{node._LSD:<8} {node._LFD:<8} {slack:<8}")
    print()

    return solver


# =============================================================================
# PART 3: Serial Generation Scheme (SGS) - The Foundation of Heuristics
# =============================================================================

def explain_sgs_algorithm():
    """
    Print an explanation of the Serial Generation Scheme (SGS).

    SGS is a fundamental constructive heuristic for RCPSP that builds
    a feasible schedule incrementally.
    """
    explanation = """
╔════════════════════════════════════════════════════════════════════════╗
║                SERIAL GENERATION SCHEME (SGS)                         ║
╚════════════════════════════════════════════════════════════════════════╝

The SGS is a CONSTRUCTIVE HEURISTIC that builds a feasible schedule one task
at a time, guided by a PRIORITY RULE (task permutation).

📋 ALGORITHM STEPS:

    Input: A permutation (priority ordering) of all tasks

    1. Initialize:
       - Set start time of source task to 0
       - Mark only source task as completed
       - Initialize resource availability arrays

    2. While tasks remain to be scheduled:

       a) SELECT next task from permutation:
          - Must be unscheduled
          - All predecessors must be completed (precedence feasibility)

       b) FIND earliest feasible start time t where:
          - t >= max(finish_time of all predecessors)  [precedence]
          - Resources available for entire duration [t, t+duration]  [resources]

       c) SCHEDULE the task:
          - Set start_time = t, end_time = t + duration
          - Update resource availability
          - Mark task as completed

    3. Return complete schedule

🔑 KEY INSIGHT:
   The QUALITY of the solution depends heavily on the task ordering!
   Different permutations → different schedules → different makespans

📊 COMMON PRIORITY RULES:
   • Random ordering (baseline)
   • Earliest Start Date (ESD) - from CPM
   • Earliest Finish Date (EFD) - from CPM
   • Longest path to sink
   • Most successors first
   • Most resources required first
"""
    print(explanation)


def demonstrate_priority_rules(rcpsp_problem: RcpspProblem, cpm_solver: CpmRcpspSolver):
    """
    Show how different priority rules affect the task ordering for SGS.

    Args:
        rcpsp_problem: The problem instance
        cpm_solver: CPM solver with computed ESD/EFD values
    """
    print("📊 Demonstrating Different Priority Rules:\n")

    # Rule 1: Sort by Earliest Start Date (ESD)
    perm_esd = sorted(
        rcpsp_problem.tasks_list,
        key=lambda x: cpm_solver.map_node[x]._ESD
    )
    print(f"   Priority Rule 1 - Earliest Start Date (ESD):")
    print(f"      First 10 tasks: {perm_esd[:10]}\n")

    # Rule 2: Sort by Earliest Finish Date (EFD)
    perm_efd = sorted(
        rcpsp_problem.tasks_list,
        key=lambda x: cpm_solver.map_node[x]._EFD
    )
    print(f"   Priority Rule 2 - Earliest Finish Date (EFD):")
    print(f"      First 10 tasks: {perm_efd[:10]}\n")

    # Rule 3: Sort by Latest Start Date (LSD)
    perm_lsd = sorted(
        rcpsp_problem.tasks_list,
        key=lambda x: cpm_solver.map_node[x]._LSD
    )
    print(f"   Priority Rule 3 - Latest Start Date (LSD):")
    print(f"      First 10 tasks: {perm_lsd[:10]}\n")


# =============================================================================
# PART 4: Solution Visualization
# =============================================================================

def visualize_solution(rcpsp_problem: RcpspProblem):
    """
    Generate and visualize a solution to the RCPSP.

    Args:
        rcpsp_problem: The problem instance
    """
    print("📈 Generating a Solution...\n")

    # Get a dummy solution (built-in heuristic)
    solution = rcpsp_problem.get_dummy_solution()

    # Evaluate the solution
    makespan = rcpsp_problem.evaluate(solution)
    is_feasible = rcpsp_problem.satisfy(solution)

    print(f"   Solution Statistics:")
    print(f"      • Makespan (project duration): {makespan}")
    print(f"      • Feasible? {is_feasible}")
    print(f"      • Solution type: {type(solution).__name__}\n")

    # Visualize (uncomment to show plots)
    print("   💡 To visualize this solution, uncomment the plotting lines in the code")
    # plot_gantt_chart(rcpsp_problem, solution)


# =============================================================================
# MAIN TUTORIAL FLOW
# =============================================================================

def main():
    """
    Main tutorial execution - walks through all concepts step by step.
    """
    print("\n" + "="*80)
    print("  LESSON 1: INTRODUCTION TO RCPSP")
    print("="*80 + "\n")

    # Step 1: Ensure data is available
    ensure_datasets_available(["j301_1.sm"])

    # Step 2: Load and inspect a problem instance
    rcpsp_problem = load_and_inspect_problem("j301_1.sm")

    # Step 3: Compute critical path (two methods)
    critical_path_nx, duration_nx = compute_critical_path_networkx(rcpsp_problem)
    cpm_solver = compute_critical_path_cpm(rcpsp_problem)

    # Step 4: Explain SGS algorithm
    explain_sgs_algorithm()

    # Step 5: Demonstrate priority rules
    demonstrate_priority_rules(rcpsp_problem, cpm_solver)

    # Step 6: Visualize a solution
    visualize_solution(rcpsp_problem)

    # Summary
    print("="*80)
    print("  TUTORIAL COMPLETE!")
    print("="*80)
    print("\n✓ You've learned:")
    print("   1. How to load RCPSP instances from PSPLib")
    print("   2. How to compute the critical path (lower bound)")
    print("   3. The structure and logic of the SGS algorithm")
    print("   4. How different priority rules affect scheduling")
    print("\n📝 Next Steps:")
    print("   → Complete exercises.py to implement your own SGS")
    print("   → Try different priority rules and compare results")
    print("   → Move on to Lesson 2: Constraint Programming\n")


if __name__ == "__main__":
    main()