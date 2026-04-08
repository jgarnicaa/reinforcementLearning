"""
Utility functions specific to RCPSP problems.

This module provides helper functions to extract and compute useful information
from RcpspProblem instances, making the code cleaner and more reusable.
"""

import numpy as np
from typing import Dict, Set, Hashable
from discrete_optimization.rcpsp.problem import RcpspProblem


def compute_predecessors(rcpsp_problem: RcpspProblem) -> Dict[Hashable, Set[Hashable]]:
    """
    Compute the predecessors mapping from the successors graph.

    While the RCPSP problem stores successors (task i → [j, k, ...]),
    many algorithms need predecessors ([j, k, ...] → task i).

    Args:
        rcpsp_problem: The RCPSP problem instance

    Returns:
        Dictionary mapping each task to its set of immediate predecessors

    Example:
        >>> predecessors = compute_predecessors(problem)
        >>> print(predecessors[5])  # {2, 3} - tasks that must finish before task 5
    """
    predecessors = {task: set() for task in rcpsp_problem.tasks_list}

    for task, successors in rcpsp_problem.successors.items():
        for successor in successors:
            predecessors[successor].add(task)

    return predecessors


def get_task_durations(
    rcpsp_problem: RcpspProblem,
    mode: int = 1
) -> Dict[Hashable, int]:
    """
    Extract task durations for a given mode.

    In single-mode RCPSP, all tasks have mode=1.
    In multi-mode RCPSP, tasks can have different execution modes.

    Args:
        rcpsp_problem: The RCPSP problem instance
        mode: Execution mode (default=1 for single-mode problems)

    Returns:
        Dictionary mapping task_id → duration

    Example:
        >>> durations = get_task_durations(problem)
        >>> print(durations[5])  # 3 - task 5 takes 3 time units
    """
    return {
        task: rcpsp_problem.mode_details[task][mode]["duration"]
        for task in rcpsp_problem.tasks_list
    }


def get_resource_consumption(
    rcpsp_problem: RcpspProblem,
    mode: int = 1
) -> Dict[Hashable, Dict[str, int]]:
    """
    Extract resource consumption for each task.

    Args:
        rcpsp_problem: The RCPSP problem instance
        mode: Execution mode (default=1)

    Returns:
        Nested dictionary: {task_id: {resource_name: consumption}}

    Example:
        >>> consumption = get_resource_consumption(problem)
        >>> print(consumption[5]["R1"])  # 2 - task 5 needs 2 units of resource R1
    """
    return {
        task: {
            resource: rcpsp_problem.mode_details[task][mode].get(resource, 0)
            for resource in rcpsp_problem.resources_list
        }
        for task in rcpsp_problem.tasks_list
    }


def initialize_resource_availability(
    rcpsp_problem: RcpspProblem,
    horizon: int = None
) -> Dict[str, np.ndarray]:
    """
    Initialize resource availability arrays for scheduling.

    Each resource has a capacity that's available at every time step.
    This creates arrays to track remaining capacity over time.

    Args:
        rcpsp_problem: The RCPSP problem instance
        horizon: Time horizon (if None, uses sum of all task durations)

    Returns:
        Dictionary mapping resource_name → availability_array

    Example:
        >>> avail = initialize_resource_availability(problem)
        >>> print(avail["R1"])  # array([4, 4, 4, ...]) - R1 has capacity 4
    """
    if horizon is None:
        # Use sum of all durations as upper bound
        durations = get_task_durations(rcpsp_problem)
        horizon = sum(durations.values())

    return {
        resource: np.array(rcpsp_problem.get_resource_availability_array(resource))
        for resource in rcpsp_problem.resources_list
    }


def create_empty_schedule(rcpsp_problem: RcpspProblem) -> Dict[Hashable, Dict[str, int]]:
    """
    Create an empty schedule structure.

    Args:
        rcpsp_problem: The RCPSP problem instance

    Returns:
        Dictionary with structure: {task_id: {"start_time": None, "end_time": None}}

    Example:
        >>> schedule = create_empty_schedule(problem)
        >>> schedule[1] = {"start_time": 0, "end_time": 5}
    """
    return {
        task: {"start_time": None, "end_time": None}
        for task in rcpsp_problem.tasks_list
    }


def compute_makespan(schedule: Dict[Hashable, Dict[str, int]]) -> int:
    """
    Compute the makespan (total project duration) from a schedule.

    The makespan is the maximum end_time across all tasks.

    Args:
        schedule: Schedule dictionary

    Returns:
        Makespan value

    Example:
        >>> makespan = compute_makespan(schedule)
        >>> print(makespan)  # 42 - project completes at time 42
    """
    return max(
        task_schedule["end_time"]
        for task_schedule in schedule.values()
        if task_schedule["end_time"] is not None
    )


def is_task_eligible(
    task: Hashable,
    completed_tasks: Set[Hashable],
    predecessors: Dict[Hashable, Set[Hashable]]
) -> bool:
    """
    Check if a task is eligible to be scheduled.

    A task is eligible if all its predecessors have been completed.

    Args:
        task: Task ID to check
        completed_tasks: Set of already completed tasks
        predecessors: Predecessors mapping

    Returns:
        True if task can be scheduled, False otherwise

    Example:
        >>> if is_task_eligible(5, completed, preds):
        >>>     # Schedule task 5
    """
    return predecessors[task].issubset(completed_tasks)


def get_earliest_precedence_start(
    task: Hashable,
    predecessors: Dict[Hashable, Set[Hashable]],
    schedule: Dict[Hashable, Dict[str, int]]
) -> int:
    """
    Compute the earliest start time based on precedence constraints.

    The task must start after all its predecessors have finished.

    Args:
        task: Task ID
        predecessors: Predecessors mapping
        schedule: Current schedule

    Returns:
        Earliest start time satisfying precedence constraints

    Example:
        >>> earliest = get_earliest_precedence_start(5, preds, schedule)
        >>> print(earliest)  # 10 - can start at time 10 (after predecessors)
    """
    if not predecessors[task]:
        return 0

    return max(
        schedule[pred]["end_time"]
        for pred in predecessors[task]
    )


def check_resource_availability(
    start_time: int,
    duration: int,
    resource_requirements: Dict[str, int],
    resource_availability: Dict[str, np.ndarray]
) -> bool:
    """
    Check if resources are available for a task at a given start time.

    Args:
        start_time: Proposed start time
        duration: Task duration
        resource_requirements: Resources needed by the task
        resource_availability: Current resource availability arrays

    Returns:
        True if all resources are available, False otherwise

    Example:
        >>> can_schedule = check_resource_availability(
        >>>     start_time=10, duration=5,
        >>>     resource_requirements={"R1": 2},
        >>>     resource_availability=availability_arrays
        >>> )
    """
    end_time = start_time + duration

    for resource, required in resource_requirements.items():
        if required > 0:
            available = resource_availability[resource][start_time:end_time]
            if np.any(available < required):
                return False

    return True


def update_resource_availability(
    start_time: int,
    duration: int,
    resource_requirements: Dict[str, int],
    resource_availability: Dict[str, np.ndarray]
) -> None:
    """
    Update resource availability after scheduling a task.

    This modifies the resource_availability arrays in-place.

    Args:
        start_time: Task start time
        duration: Task duration
        resource_requirements: Resources consumed by the task
        resource_availability: Resource availability arrays (modified in-place)

    Example:
        >>> update_resource_availability(
        >>>     start_time=10, duration=5,
        >>>     resource_requirements={"R1": 2},
        >>>     resource_availability=availability_arrays
        >>> )
    """
    end_time = start_time + duration

    for resource, required in resource_requirements.items():
        if required > 0:
            resource_availability[resource][start_time:end_time] -= required
