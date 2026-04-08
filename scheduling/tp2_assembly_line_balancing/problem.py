"""
Resource-Constrained Assembly Line Balancing Problem (RC-ALBP)

This problem combines elements from:
- SALBP (Simple Assembly Line Balancing): Task assignment and precedence
- RCALBP/L: Resource constraints at workstations

Problem Definition:
-------------------
Given:
- A fixed number of workstations (stations)
- A set of tasks with processing times and precedence constraints
- Multiple resource types (e.g., workers, tools, space)
- Resource allocation to each workstation (pre-decided)
- Resource consumption by each task

Decision Variables:
- Assignment of tasks to workstations
- Start time of each task within the cycle

Objective:
- Minimize the cycle time (makespan)

Constraints:
1. Precedence: Predecessor tasks must finish before successors
2. Resource Capacity: Resource consumption at each station cannot exceed allocation
3. No overlap: Tasks on the same station cannot overlap in time
"""

from typing import Dict, List, Tuple, Optional, Hashable
from copy import deepcopy

from discrete_optimization.generic_tasks_tools.allocation import (
    AllocationProblem,
    AllocationSolution,
    UnaryResource,
)
from discrete_optimization.generic_tasks_tools.scheduling import (
    SchedulingProblem,
    SchedulingSolution,
)
from discrete_optimization.generic_tools.do_problem import (
    Problem,
    Solution,
    ModeOptim,
    ObjectiveDoc,
    ObjectiveHandling,
    ObjectiveRegister,
    TypeObjective,
)

# Type aliases for clarity
Task = Hashable
Station = Hashable
Resource = Hashable


class RCALBPSolution(SchedulingSolution[Task], AllocationSolution[Task, Station]):
    """
    Solution for RC-ALBP problem.

    Implements both SchedulingSolution and AllocationSolution interfaces
    following the discrete-optimization framework.

    Attributes:
        problem: Reference to the problem instance
        task_assignment: Dict mapping each task to its assigned station
        task_schedule: Dict mapping each task to its start time
        cycle_time: The computed cycle time (max end time across all stations)
    """

    problem: "RCALBPProblem"

    def __init__(
        self,
        problem: "RCALBPProblem",
        task_assignment: Dict[Task, Station],
        task_schedule: Optional[Dict[Task, int]] = None,
        cycle_time: Optional[int] = None,
    ):
        super().__init__(problem)
        self.task_assignment = task_assignment
        self.task_schedule = task_schedule if task_schedule is not None else {}
        self.cycle_time = cycle_time

    # SchedulingSolution interface
    def get_start_time(self, task: Task) -> int:
        """Return the start time of a task."""
        return self.task_schedule.get(task, 0)

    def get_end_time(self, task: Task) -> int:
        """Return the end time of a task."""
        start = self.get_start_time(task)
        return start + self.problem.task_times.get(task, 0)

    # AllocationSolution interface
    def is_allocated(self, task: Task, unary_resource: UnaryResource) -> bool:
        """Check if a task is allocated to a given station."""
        return self.task_assignment.get(task) == unary_resource

    def copy(self) -> "RCALBPSolution":
        """Create a deep copy of the solution."""
        return RCALBPSolution(
            problem=self.problem,
            task_assignment=deepcopy(self.task_assignment),
            task_schedule=deepcopy(self.task_schedule),
            cycle_time=self.cycle_time,
        )

    def change_problem(self, new_problem: Problem) -> Solution:
        """Change the problem instance."""
        return RCALBPSolution(
            problem=new_problem,
            task_assignment=deepcopy(self.task_assignment),
            task_schedule=deepcopy(self.task_schedule),
            cycle_time=self.cycle_time,
        )

    def __str__(self):
        return f"RCALBPSolution(cycle_time={self.cycle_time})"

    def __hash__(self):
        return hash((tuple(sorted(self.task_assignment.items())),
                     tuple(sorted(self.task_schedule.items()))))

    def __eq__(self, other):
        return (self.task_assignment == other.task_assignment and
                self.task_schedule == other.task_schedule)


class RCALBPProblem(SchedulingProblem[Task], AllocationProblem[Task, Station]):
    """
    Resource-Constrained Assembly Line Balancing Problem.

    A hybrid between SALBP-2 (minimize cycle time with fixed stations) and
    RCALBP/L (resource constraints), but without the learning effect complexity.

    Follows the discrete-optimization framework by inheriting from:
    - SchedulingProblem[Task]: Provides scheduling-related methods
    - AllocationProblem[Task, Station]: Provides allocation-related methods

    Attributes:
        nb_stations: Fixed number of workstations
        nb_tasks: Number of tasks to assign
        task_times: Processing time for each task
        precedences: List of (predecessor, successor) pairs
        nb_resources: Number of resource types
        station_resources: Resource allocation per station {(resource, station): amount}
        task_resources: Resource consumption per task {(resource, task): amount}
    """

    # SchedulingProblem interface
    def get_makespan_upper_bound(self) -> int:
        """
        Return an upper bound on the makespan.
        Worst case: all tasks sequentially on one station.
        """
        return sum(self.task_times.values())

    @property
    def tasks_list(self) -> List[Task]:
        """Return the list of all tasks."""
        return self.tasks

    # AllocationProblem interface
    @property
    def unary_resources_list(self) -> List[UnaryResource]:
        """Return the list of all stations (unary resources)."""
        return self.stations

    def __init__(
        self,
        task_times: Dict[Task, int],
        precedences: List[Tuple[Task, Task]],
        stations: List[Station],
        resources: List[Resource],
        station_resources: Dict[Tuple[Resource, Station], int],
        task_resources: Dict[Tuple[Resource, Task], int],
    ):
        """
        Initialize RC-ALBP problem.

        Args:
            task_times: Processing time for each task {task: duration}
            precedences: List of (predecessor, successor) pairs
            stations: List of station identifiers (can be str or int)
            resources: List of resource identifiers (can be str or int)
            station_resources: Resource allocation {(resource, station): amount}
            task_resources: Resource consumption {(resource, task): amount}
        """
        self.task_times = task_times
        self.precedences = precedences
        self.station_resources = station_resources
        self.task_resources = task_resources

        # Derived properties
        self.tasks = sorted(list(task_times.keys()), key=str)
        self.stations = list(stations)
        self.resources = list(resources)

        # Backward compatibility
        self.nb_tasks = len(self.tasks)
        self.nb_stations = len(self.stations)
        self.nb_resources = len(self.resources)

        # Build adjacency lists for precedence graph
        self.successors = {t: [] for t in self.tasks}
        self.predecessors = {t: [] for t in self.tasks}
        for pred, succ in precedences:
            self.successors[pred].append(succ)
            self.predecessors[succ].append(pred)

    def get_objective_register(self) -> ObjectiveRegister:
        """
        Define objectives and penalties.

        Primary objective: Minimize cycle time
        Penalties: Precedence violations, resource capacity violations
        """
        return ObjectiveRegister(
            objective_sense=ModeOptim.MINIMIZATION,
            objective_handling=ObjectiveHandling.AGGREGATE,
            dict_objective_to_doc={
                "cycle_time": ObjectiveDoc(
                    type=TypeObjective.OBJECTIVE,
                    default_weight=1.0
                ),
                "penalty_precedence": ObjectiveDoc(
                    type=TypeObjective.PENALTY,
                    default_weight=10000.0
                ),
                "penalty_resource": ObjectiveDoc(
                    type=TypeObjective.PENALTY,
                    default_weight=10000.0
                ),
                "penalty_unscheduled": ObjectiveDoc(
                    type=TypeObjective.PENALTY,
                    default_weight=10000.0
                ),
            },
        )

    def evaluate(self, solution: RCALBPSolution) -> Dict[str, float]:
        """
        Evaluate the solution quality and constraint satisfaction.

        Returns:
            Dictionary with:
            - cycle_time: Maximum makespan across all stations
            - penalty_precedence: Number of precedence violations
            - penalty_resource: Amount of resource over-consumption
            - penalty_unscheduled: Number of tasks without valid schedule
        """
        penalty_precedence = 0.0
        penalty_resource = 0.0
        penalty_unscheduled = 0.0
        station_makespans = {s: 0 for s in self.stations}

        # Check if all tasks are assigned
        if len(solution.task_assignment) != self.nb_tasks:
            penalty_unscheduled = self.nb_tasks - len(solution.task_assignment)

        # 1. Check precedence constraints
        for pred, succ in self.precedences:
            if pred not in solution.task_assignment or succ not in solution.task_assignment:
                penalty_precedence += 1
                continue

            station_pred = solution.task_assignment[pred]
            station_succ = solution.task_assignment[succ]

            # Different stations: pred must be before succ
            if station_pred > station_succ:
                penalty_precedence += 1

            # Same station: check temporal precedence
            elif station_pred == station_succ:
                if pred in solution.task_schedule and succ in solution.task_schedule:
                    end_pred = solution.get_end_time(pred)
                    start_succ = solution.get_start_time(succ)
                    if end_pred > start_succ:
                        penalty_precedence += 1

        # 2. Compute cycle time and check resource constraints
        for station in self.stations:
            # Get tasks assigned to this station
            station_tasks = [t for t, s in solution.task_assignment.items() if s == station]

            if not station_tasks:
                continue

            # Check if tasks are scheduled
            if not all(t in solution.task_schedule for t in station_tasks):
                penalty_unscheduled += sum(1 for t in station_tasks if t not in solution.task_schedule)
                continue

            # Compute makespan for this station
            max_end = 0
            for task in station_tasks:
                start = solution.task_schedule[task]
                end = start + self.task_times[task]
                max_end = max(max_end, end)

            station_makespans[station] = max_end

            # 3. Check resource constraints using sweep-line algorithm
            # Create events for task start/end
            events = []
            for task in station_tasks:
                start_time = solution.task_schedule[task]
                duration = self.task_times[task]
                if duration > 0:
                    events.append((start_time, 'start', task))
                    events.append((start_time + duration, 'end', task))

            # Sort events: process 'end' before 'start' at same time
            events.sort(key=lambda x: (x[0], 0 if x[1] == 'end' else 1))

            # Sweep through time and check resource usage
            active_tasks = set()
            for time, event_type, task in events:
                if event_type == 'start':
                    active_tasks.add(task)

                    # Check resource capacity for each resource type
                    for resource in self.resources:
                        usage = sum(
                            self.task_resources.get((resource, t), 0)
                            for t in active_tasks
                        )
                        capacity = self.station_resources.get((resource, station), 0)

                        if usage > capacity:
                            penalty_resource += (usage - capacity)
                else:
                    active_tasks.remove(task)

        # Cycle time is the maximum makespan across all stations
        cycle_time = max(station_makespans.values()) if station_makespans else 0
        solution.cycle_time = cycle_time

        return {
            "cycle_time": float(cycle_time),
            "penalty_precedence": penalty_precedence,
            "penalty_resource": penalty_resource,
            "penalty_unscheduled": penalty_unscheduled,
        }

    def satisfy(self, solution: RCALBPSolution) -> bool:
        """
        Check if the solution satisfies all hard constraints.

        Returns:
            True if all tasks are scheduled and no constraints are violated
        """
        eval_dict = self.evaluate(solution)
        return (
            eval_dict["penalty_precedence"] == 0 and
            eval_dict["penalty_resource"] == 0 and
            eval_dict["penalty_unscheduled"] == 0
        )

    def get_solution_type(self) -> type[Solution]:
        """Return the solution class type."""
        return RCALBPSolution

    def get_dummy_solution(self) -> RCALBPSolution:
        """
        Create a trivial dummy solution (likely infeasible).
        Assigns all tasks to the first station sequentially.
        """
        first_station = self.stations[0]
        task_assignment = {t: first_station for t in self.tasks}
        task_schedule = {}

        current_time = 0
        for task in self.tasks:
            task_schedule[task] = current_time
            current_time += self.task_times[task]

        return RCALBPSolution(
            problem=self,
            task_assignment=task_assignment,
            task_schedule=task_schedule,
            cycle_time=current_time,
        )
