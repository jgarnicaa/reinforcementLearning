"""
Utility functions for TP2 - Resource-Constrained Assembly Line Balancing

Provides helpers for:
- Creating problem instances
- Visualizing solutions
- Computing lower bounds
"""

from typing import Dict, List, Tuple
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation

from discrete_optimization.rcpsp.problem import RcpspProblem
from discrete_optimization.rcpsp.parser import get_data_available, parse_file
from discrete_optimization.datasets import fetch_data_from_psplib

from scheduling.tp2_assembly_line_balancing.problem import (
    RCALBPProblem,
    RCALBPSolution,
    Task,
    Station,
    Resource,
)


def create_simple_instance(
    nb_stations: int = 3,
    nb_tasks: int = 10,
    nb_resources: int = 2,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Create a simple random RC-ALBP instance with readable names.

    Args:
        nb_stations: Number of workstations
        nb_tasks: Number of tasks
        nb_resources: Number of resource types
        seed: Random seed for reproducibility

    Returns:
        RCALBPProblem instance
    """
    random.seed(seed)

    # Create readable task names
    tasks = [f"T{i+1}" for i in range(nb_tasks)]
    stations = [f"WS{i+1}" for i in range(nb_stations)]
    resources = [f"R{i+1}" for i in range(nb_resources)]

    # Generate task processing times (1-10 time units)
    task_times = {t: random.randint(1, 10) for t in tasks}

    # Generate precedence constraints (ensure acyclic)
    precedences = []
    for i in range(nb_tasks - 1):
        # Each task can have 0-2 successors
        nb_successors = random.randint(0, min(2, nb_tasks - i - 1))
        successor_indices = random.sample(range(i + 1, nb_tasks), nb_successors)
        for succ_idx in successor_indices:
            precedences.append((tasks[i], tasks[succ_idx]))

    # Generate resource allocation to stations
    station_resources = {}
    for r in resources:
        for s in stations:
            # Random allocation between 2-5 units
            station_resources[(r, s)] = random.randint(2, 5)

    # Generate task resource consumption
    task_resources = {}
    for r in resources:
        for t in tasks:
            # 0-2 units consumption
            task_resources[(r, t)] = random.randint(0, 2)

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def create_precedence_example() -> RCALBPProblem:
    """
    Create a small example with clear precedence structure and meaningful names.

    Task structure:
        Prepare → Assemble → Test
           ↓         ↓        ↓
        Cut    →  Join  →  Package

    Returns:
        RCALBPProblem instance
    """
    # Define tasks with meaningful names
    tasks = ["Prepare", "Assemble", "Cut", "Join", "Test", "Package"]

    task_times = {
        "Prepare": 5,
        "Assemble": 3,
        "Cut": 4,
        "Join": 3,
        "Test": 2,
        "Package": 6,
    }

    precedences = [
        ("Prepare", "Assemble"),
        ("Prepare", "Cut"),
        ("Assemble", "Test"),
        ("Assemble", "Join"),
        ("Cut", "Join"),
        ("Test", "Package"),
        ("Join", "Package"),
    ]

    # Define stations and resources with names
    stations = ["Station_A", "Station_B"]
    resources = ["Worker", "Tool"]

    # Resource allocation: {(resource, station): amount}
    station_resources = {
        ("Worker", "Station_A"): 3,
        ("Worker", "Station_B"): 2,
        ("Tool", "Station_A"): 2,
        ("Tool", "Station_B"): 3,
    }

    # Task resource consumption: {(resource, task): amount}
    task_resources = {
        ("Worker", "Prepare"): 1,
        ("Worker", "Assemble"): 0,
        ("Worker", "Cut"): 1,
        ("Worker", "Join"): 0,
        ("Worker", "Test"): 1,
        ("Worker", "Package"): 2,
        ("Tool", "Prepare"): 0,
        ("Tool", "Assemble"): 1,
        ("Tool", "Cut"): 1,
        ("Tool", "Join"): 1,
        ("Tool", "Test"): 1,
        ("Tool", "Package"): 1,
    }

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def _compute_task_lanes(tasks_with_times):
    """
    Compute lanes (vertical stacking) for tasks to avoid visual overlap.

    Args:
        tasks_with_times: List of (task_id, start, end) tuples

    Returns:
        Tuple of (task_lanes dict, num_lanes int)
    """
    if not tasks_with_times:
        return {}, 0

    # Sort tasks by start time
    sorted_tasks = sorted(tasks_with_times, key=lambda x: x[1])

    # Track end time of last task in each lane
    lanes = []  # Each element is the end time of the last task in that lane
    task_lanes = {}  # Maps task_id to lane number

    for task_id, start, end in sorted_tasks:
        # Find first lane where this task fits (doesn't overlap)
        assigned = False
        for lane_idx, lane_end_time in enumerate(lanes):
            if start >= lane_end_time:  # No overlap
                lanes[lane_idx] = end
                task_lanes[task_id] = lane_idx
                assigned = True
                break

        if not assigned:
            # Create new lane
            lanes.append(end)
            task_lanes[task_id] = len(lanes) - 1

    return task_lanes, len(lanes)


def visualize_solution(
    problem: RCALBPProblem,
    solution: RCALBPSolution,
    show: bool = True,
) -> plt.Figure:
    """
    Visualize the assembly line solution as a Gantt chart with stacked tasks.

    Args:
        problem: Problem instance
        solution: Solution to visualize
        show: Whether to display the plot

    Returns:
        Matplotlib figure
    """
    # Color map for tasks
    colors = plt.cm.Set3(range(problem.nb_tasks))
    task_colors = {t: colors[i % len(colors)] for i, t in enumerate(problem.tasks)}

    # Compute lanes for each station to handle overlapping tasks
    station_lanes = {}
    station_num_lanes = {}

    for station in problem.stations:
        station_tasks = [
            t for t, s in solution.task_assignment.items() if s == station
        ]

        # Get task timing info
        tasks_with_times = []
        for task in station_tasks:
            if task in solution.task_schedule:
                start = solution.task_schedule[task]
                end = start + problem.task_times[task]
                tasks_with_times.append((task, start, end))
        task_lanes, num_lanes = _compute_task_lanes(tasks_with_times)
        station_lanes[station] = task_lanes
        station_num_lanes[station] = num_lanes

    # Calculate figure height based on total lanes
    total_lanes = sum(station_num_lanes.values())
    fig_height = max(6, total_lanes * 0.8 + 2)

    fig, ax = plt.subplots(figsize=(14, fig_height))

    # Track y positions for stations
    y_pos = 0
    station_y_positions = {}
    station_y_centers = {}

    for station in reversed(problem.stations):
        num_lanes = station_num_lanes.get(station, 1)
        lane_height = 0.8

        station_y_positions[station] = y_pos
        station_y_centers[station] = y_pos + (num_lanes * lane_height) / 2

        station_tasks = [
            t for t, s in solution.task_assignment.items() if s == station
        ]

        for task in station_tasks:
            if task not in solution.task_schedule:
                continue

            start = solution.task_schedule[task]
            duration = problem.task_times[task]

            # Get lane for this task
            lane = station_lanes[station].get(task, 0)
            y_position = y_pos + lane * lane_height

            # Draw task bar
            ax.barh(
                y_position,
                duration,
                left=start,
                height=lane_height * 0.85,
                color=task_colors[task],
                edgecolor='black',
                linewidth=1.2,
                alpha=0.8,
            )

            # Add task label
            ax.text(
                start + duration / 2,
                y_position,
                task,
                ha='center',
                va='center',
                fontsize=8,
                fontweight='bold',
            )

        y_pos += num_lanes * lane_height + 0.3  # Add spacing between stations

    # Format plot
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Station', fontsize=12)
    ax.set_title(f'Assembly Line Schedule (Cycle Time: {solution.cycle_time})', fontsize=14)

    # Set y-axis labels at station centers
    ax.set_yticks(list(station_y_centers.values()))
    ax.set_yticklabels([f'Station {s}' for s in reversed(problem.stations)])

    ax.set_ylim(-0.5, y_pos - 0.3)
    ax.grid(axis='x', alpha=0.3)

    # Add cycle time line
    if solution.cycle_time:
        ax.axvline(
            solution.cycle_time,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Cycle Time: {solution.cycle_time}',
        )
        ax.legend()

    plt.tight_layout()

    if show:
        plt.show()

    return fig


def visualize_interactive_flow(
    problem: RCALBPProblem,
    solution: RCALBPSolution,
):
    """
    Create an interactive visualization of assembly line flow with time slider.

    Shows:
    - Aircraft/product flow through stations over time
    - Active tasks at each station
    - Resource usage tracking per station
    - Constraint violation warnings

    Args:
        problem: Problem instance
        solution: Solution to visualize
    """
    # Validate solution first
    eval_dict = problem.evaluate(solution)
    has_violations = (
        eval_dict['penalty_precedence'] > 0 or
        eval_dict['penalty_resource'] > 0 or
        eval_dict['penalty_unscheduled'] > 0
    )

    if has_violations:
        print("\n[!] WARNING: Solution has constraint violations!")
        if eval_dict['penalty_precedence'] > 0:
            print(f"   - Precedence violations: {eval_dict['penalty_precedence']}")
        if eval_dict['penalty_resource'] > 0:
            print(f"   - Resource violations: {eval_dict['penalty_resource']}")
        if eval_dict['penalty_unscheduled'] > 0:
            print(f"   - Unscheduled tasks: {eval_dict['penalty_unscheduled']}")
        print()

    cycle_time = solution.cycle_time
    nb_stations = len(problem.stations)
    nb_periods = 5  # Show 5 cycles

    # Create dynamic layout that adapts to number of stations
    # Calculate resource plot grid (max 3 columns)
    n_res_cols = min(3, nb_stations)
    n_res_rows = (nb_stations + n_res_cols - 1) // n_res_cols  # Ceiling division

    # Create figure with dynamic grid
    # Rows: [Gantt (tall), Resource rows (shorter), Slider (thin)]
    total_rows = 1 + n_res_rows + 1
    fig = plt.figure(figsize=(18, 10))

    # Height ratios: Gantt gets most space, resources get less, slider minimal
    height_ratios = [4] + [1] * n_res_rows + [0.25]

    gs = fig.add_gridspec(
        total_rows, n_res_cols,
        height_ratios=height_ratios,
        hspace=0.4,
        wspace=0.3
    )

    # Gantt chart: full width at top (spans all columns)
    ax_gantt = fig.add_subplot(gs[0, :])

    # Resource usage plots: dynamic grid for ALL stations
    ax_resources = []
    for i in range(nb_stations):
        row = 1 + i // n_res_cols
        col = i % n_res_cols
        ax = fig.add_subplot(gs[row, col])
        ax_resources.append(ax)

    # Time slider: spans all columns at bottom
    ax_slider = fig.add_subplot(gs[-1, :])

    # Prepare data structures
    # Map tasks to stations
    station_to_tasks = {s: [] for s in problem.stations}
    for task, station in solution.task_assignment.items():
        if task in solution.task_schedule:
            station_to_tasks[station].append({
                'task': task,
                'start': solution.task_schedule[task],
                'end': solution.task_schedule[task] + problem.task_times[task],
                'duration': problem.task_times[task]
            })

    # Sort tasks by start time
    for station in station_to_tasks:
        station_to_tasks[station].sort(key=lambda x: x['start'])

    # Color map for tasks
    colors = plt.cm.Set3(range(problem.nb_tasks))
    task_colors = {t: colors[i % len(colors)] for i, t in enumerate(problem.tasks)}

    def get_active_tasks_at_time(station, time):
        """Get tasks active at given time on station."""
        active = []
        for task_info in station_to_tasks[station]:
            if task_info['start'] <= time < task_info['end']:
                active.append(task_info)
        return active

    def get_resource_usage_at_time(station, time):
        """Get resource usage at given time on station."""
        active_tasks = get_active_tasks_at_time(station, time)
        usage = {r: 0 for r in problem.resources}

        for task_info in active_tasks:
            task = task_info['task']
            for resource in problem.resources:
                usage[resource] += problem.task_resources.get((resource, task), 0)

        return usage

    def update_plot(current_time):
        """Update visualization for current time."""
        # Clear axes
        ax_gantt.clear()
        for ax in ax_resources:
            ax.clear()

        # Calculate current period and time within cycle
        period_idx = int(current_time // cycle_time)
        time_in_cycle = current_time % cycle_time

        # =====================================================================
        # Update Resource Usage Plots (ALL STATIONS)
        # =====================================================================
        for idx, ax in enumerate(ax_resources):
            station = problem.stations[idx]
            usage = get_resource_usage_at_time(station, time_in_cycle)

            # Plot bar chart
            resource_names = list(problem.resources)
            usages = [usage[r] for r in resource_names]
            capacities = [problem.station_resources.get((r, station), 0) for r in resource_names]

            x = np.arange(len(resource_names))
            bars1 = ax.bar(x - 0.2, usages, 0.4, label='Usage', color='steelblue', alpha=0.7)
            bars2 = ax.bar(x + 0.2, capacities, 0.4, label='Capacity', color='lightcoral', alpha=0.7)

            # Highlight violations
            for i, (u, c) in enumerate(zip(usages, capacities)):
                if u > c:
                    ax.bar(i - 0.2, u, 0.4, color='red', alpha=0.9)
                    ax.text(i - 0.2, u + 0.1, '[!]', ha='center', fontsize=10, color='red', fontweight='bold')

            ax.set_ylabel('Units', fontsize=9)
            ax.set_title(f'{station} - Resource Usage (t={time_in_cycle:.1f})', fontsize=10, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(resource_names, fontsize=8)
            ax.legend(fontsize=7, loc='upper right')
            ax.grid(axis='y', alpha=0.3)
            ax.set_ylim(0, max(max(capacities) * 1.2, 1) if capacities else 1)

        # =====================================================================
        # Draw Gantt Chart with Current Time Indicator and Lane-based Stacking
        # =====================================================================

        # Compute lanes for each station
        station_task_lanes = {}
        station_num_lanes = {}

        for station in problem.stations:
            tasks_with_times = [
                (info['task'], info['start'], info['end'])
                for info in station_to_tasks[station]
            ]
            task_lanes, num_lanes = _compute_task_lanes(tasks_with_times)
            station_task_lanes[station] = task_lanes
            station_num_lanes[station] = max(num_lanes, 1)

        # Draw tasks with lane-based stacking
        y_pos = 0
        station_y_positions = {}
        station_y_centers = {}
        lane_height = 0.7

        for station in reversed(problem.stations):
            num_lanes = station_num_lanes[station]
            station_y_positions[station] = y_pos
            station_y_centers[station] = y_pos + (num_lanes * lane_height) / 2

            # Get active tasks at current time
            active_tasks_now = get_active_tasks_at_time(station, time_in_cycle)
            active_task_ids = {t['task'] for t in active_tasks_now}

            # Get tasks for this station
            tasks_in_station = station_to_tasks[station]

            for task_info in tasks_in_station:
                task = task_info['task']
                start = task_info['start']
                duration = task_info['duration']

                # Get lane for this task
                lane = station_task_lanes[station].get(task, 0)
                y_position = y_pos + lane * lane_height

                # Check if task is active
                is_active = task in active_task_ids

                # Choose color and style based on activity
                if is_active:
                    color = 'gold'  # Highlight active tasks
                    edge_color = 'red'
                    edge_width = 2.5
                    alpha = 1.0
                else:
                    color = task_colors[task]
                    edge_color = 'black'
                    edge_width = 1
                    alpha = 0.7

                # Draw task bar
                ax_gantt.barh(
                    y_position,
                    duration,
                    left=start,
                    height=lane_height * 0.85,
                    color=color,
                    edgecolor=edge_color,
                    linewidth=edge_width,
                    alpha=alpha
                )

                # Add task label
                ax_gantt.text(
                    start + duration / 2,
                    y_position,
                    task,
                    ha='center',
                    va='center',
                    fontsize=7,
                    fontweight='bold',
                    color='black' if is_active else 'black'
                )

            y_pos += num_lanes * lane_height + 0.3

        # Draw vertical line at current time in cycle (resets at each cycle)
        ax_gantt.axvline(
            time_in_cycle,
            color='red',
            linestyle='--',
            linewidth=2.5,
            label=f't={time_in_cycle:.1f}',
            alpha=0.8,
            zorder=10
        )

        # Draw cycle time boundary
        ax_gantt.axvline(
            cycle_time,
            color='darkgreen',
            linestyle='-',
            linewidth=1.5,
            alpha=0.5,
            label=f'Cycle={cycle_time}',
            zorder=10
        )

        # Format Gantt chart
        ax_gantt.set_yticks(list(station_y_centers.values()))
        ax_gantt.set_yticklabels([s for s in reversed(problem.stations)], fontsize=10)
        ax_gantt.set_xlabel('Time within Cycle', fontsize=11)
        ax_gantt.set_title(
            f'Assembly Line Schedule - Time: {current_time:.1f} (Cycle {period_idx+1}, t={time_in_cycle:.1f}/{cycle_time})',
            fontsize=12, fontweight='bold'
        )
        ax_gantt.set_xlim(0, cycle_time * 1.05)
        ax_gantt.set_ylim(-0.5, y_pos - 0.3)
        ax_gantt.grid(axis='x', alpha=0.3)
        ax_gantt.legend(fontsize=8, loc='upper right')

    # Create slider
    slider = Slider(
        ax_slider,
        'Time',
        0,
        cycle_time * nb_periods,
        valinit=0,
        valstep=0.1
    )

    def update(val):
        update_plot(slider.val)
        fig.canvas.draw_idle()

    slider.on_changed(update)

    # Initial plot
    update_plot(0)

    plt.tight_layout()

    # Show the interactive plot
    print("  [Interactive plot ready - use the slider to explore different time periods]")
    print("  [Gantt chart shows active tasks (highlighted in gold) and time indicator (red line)]")
    print(f"  [Resource plots show usage vs capacity for all {nb_stations} stations]")
    plt.show()


def create_from_rcpsp(
    rcpsp_problem: RcpspProblem,
    nb_stations: int = 3,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Create a realistic RC-ALBP instance from an RCPSP problem.

    This converts a project scheduling problem into an assembly line balancing
    problem by:
    - Using RCPSP tasks, durations, and precedences
    - Splitting RCPSP global resources across stations
    - Using RCPSP resource consumption per task

    Args:
        rcpsp_problem: RCPSP problem instance
        nb_stations: Number of assembly line stations
        seed: Random seed for resource allocation

    Returns:
        RCALBPProblem instance
    """
    random.seed(seed)

    # Tasks: Use RCPSP tasks with string names
    task_times = {
        f"T{task}": rcpsp_problem.mode_details[task][1]["duration"]
        for task in rcpsp_problem.tasks_list
    }

    # Precedences: Convert RCPSP precedences
    precedences = []
    for task in rcpsp_problem.tasks_list:
        for succ in rcpsp_problem.successors.get(task, []):
            precedences.append((f"T{task}", f"T{succ}"))

    # Stations: Create station names
    stations = [f"WS{i+1}" for i in range(nb_stations)]

    # Resources: Use RCPSP resources
    resources = [f"R{r}" for r in rcpsp_problem.resources_list]

    # Resource allocation: Create tighter constraints
    # Strategy: Find max task requirement and set station capacity slightly above it
    # This makes the problem more challenging and realistic
    station_resources = {}

    for r_idx, r_name in enumerate(rcpsp_problem.resources_list):
        # Find maximum task requirement for this resource
        max_task_requirement = max(
            rcpsp_problem.mode_details[task][1].get(r_name, 0)
            for task in rcpsp_problem.tasks_list
        )

        # Set station capacity to max_requirement + small buffer (20-40%)
        # This ensures at least one task can run, but limits parallelism
        if max_task_requirement > 0:
            buffer_factor = 1.2 + random.random() * 0.2  # 1.2 to 1.4
            station_capacity = int(np.ceil(max_task_requirement * buffer_factor))
        else:
            station_capacity = 1  # Minimal capacity if no tasks use this resource

        for s_idx, station in enumerate(stations):
            # Add some variation between stations (±10%)
            variation = random.uniform(0.9, 1.1)
            capacity = max(1, int(station_capacity * variation))
            station_resources[(f"R{r_name}", station)] = capacity

    # Task resource consumption: Use RCPSP consumption
    task_resources = {}
    for task in rcpsp_problem.tasks_list:
        for r_name in rcpsp_problem.resources_list:
            consumption = rcpsp_problem.mode_details[task][1].get(r_name, 0)
            task_resources[(f"R{r_name}", f"T{task}")] = consumption

    return RCALBPProblem(
        task_times=task_times,
        precedences=precedences,
        stations=stations,
        resources=resources,
        station_resources=station_resources,
        task_resources=task_resources,
    )


def load_rcpsp_as_albp(
    instance_name: str = "j301_1",
    nb_stations: int = 3,
    seed: int = 42,
) -> RCALBPProblem:
    """
    Load an RCPSP instance from PSPLib and convert to RC-ALBP.

    Args:
        instance_name: Name of RCPSP instance (e.g., "j301_1")
        nb_stations: Number of assembly line stations
        seed: Random seed for resource allocation

    Returns:
        RCALBPProblem instance
    """
    # Load RCPSP instance
    try:
        files = get_data_available()
    except:
        fetch_data_from_psplib()
        files = get_data_available()

    matching_files = [f for f in files if instance_name in f]
    if not matching_files:
        raise ValueError(f"No RCPSP instance found matching '{instance_name}'")

    filepath = matching_files[0]
    rcpsp_problem = parse_file(filepath)

    # Convert to RC-ALBP
    return create_from_rcpsp(rcpsp_problem, nb_stations=nb_stations, seed=seed)


def print_solution_info(problem: RCALBPProblem, solution: RCALBPSolution):
    """
    Print detailed information about a solution.

    Args:
        problem: Problem instance
        solution: Solution to analyze
    """
    print("=" * 60)
    print("SOLUTION INFORMATION")
    print("=" * 60)

    # Evaluation
    eval_dict = problem.evaluate(solution)
    print(f"\nCycle Time: {solution.cycle_time}")
    print(f"Valid: {problem.satisfy(solution)}")

    if eval_dict['penalty_precedence'] > 0:
        print(f"⚠ Precedence violations: {eval_dict['penalty_precedence']}")
    if eval_dict['penalty_resource'] > 0:
        print(f"⚠ Resource violations: {eval_dict['penalty_resource']}")
    if eval_dict['penalty_unscheduled'] > 0:
        print(f"⚠ Unscheduled tasks: {eval_dict['penalty_unscheduled']}")

    # Station workload
    print("\nStation Workloads:")
    for station in problem.stations:
        station_tasks = [
            t for t, s in solution.task_assignment.items() if s == station
        ]
        if station_tasks:
            makespan = max(
                solution.task_schedule.get(t, 0) + problem.task_times[t]
                for t in station_tasks
            )
            total_work = sum(problem.task_times[t] for t in station_tasks)
            print(f"  Station {station}: {len(station_tasks)} tasks, "
                  f"total work={total_work}, makespan={makespan}")

            # Resource usage
            for resource in problem.resources:
                max_usage = 0
                for t in station_tasks:
                    usage = problem.task_resources.get((resource, t), 0)
                    max_usage = max(max_usage, usage)
                capacity = problem.station_resources.get((resource, station), 0)
                print(f"    Resource {resource}: max_usage={max_usage}, capacity={capacity}")

    print("=" * 60)
