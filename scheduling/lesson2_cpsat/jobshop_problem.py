"""
Job Shop Scheduling Problem - Data Structures

This module defines the core data structures for representing
Job Shop Scheduling Problems and their solutions.
"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Subjob:
    """
    A single operation (task) in a job shop problem.

    Attributes:
        machine_id: ID of the machine required for this operation
        processing_time: Duration needed to complete this operation
    """
    machine_id: int
    processing_time: int

    def __str__(self):
        return f"Machine {self.machine_id}, Duration {self.processing_time}"


class JobShopProblem:
    """
    Complete definition of a Job Shop Scheduling Problem.

    A job shop consists of:
    - Multiple jobs, each with a sequence of operations (subjobs)
    - Each operation requires a specific machine and has a duration
    - Operations within a job must be executed in order
    - Machines can only process one operation at a time
    """

    def __init__(
        self,
        list_jobs: List[List[Subjob]],
        n_jobs: int = None,
        n_machines: int = None
    ):
        """
        Initialize a Job Shop Problem.

        Args:
            list_jobs: List of jobs, where each job is a list of Subjob operations
            n_jobs: Number of jobs (auto-computed if None)
            n_machines: Number of machines (auto-computed if None)
        """
        self.list_jobs = list_jobs
        self.n_jobs = n_jobs if n_jobs is not None else len(list_jobs)

        # Auto-compute number of machines if not provided
        if n_machines is None:
            all_machines = {
                subjob.machine_id
                for job in list_jobs
                for subjob in job
            }
            self.n_machines = len(all_machines)
        else:
            self.n_machines = n_machines

        # Pre-compute mapping: machine -> list of (job_id, subjob_id) using that machine
        # This is very useful for adding NoOverlap constraints per machine
        self.job_per_machines = {i: [] for i in range(self.n_machines)}
        for job_id in range(self.n_jobs):
            for subjob_id in range(len(list_jobs[job_id])):
                machine = list_jobs[job_id][subjob_id].machine_id
                self.job_per_machines[machine].append((job_id, subjob_id))

    def __str__(self):
        return (f"JobShopProblem(jobs={self.n_jobs}, machines={self.n_machines}, "
                f"total_operations={sum(len(job) for job in self.list_jobs)})")


class SolutionJobshop:
    """
    Solution to a Job Shop Problem.

    A solution specifies the start and end times for each operation.
    """

    def __init__(self, schedule: List[List[Tuple[int, int]]]):
        """
        Initialize a solution.

        Args:
            schedule: For each job and subjob, the (start_time, end_time) tuple
                     Structure: schedule[job_id][subjob_id] = (start, end)
        """
        self.schedule = schedule

    def get_makespan(self) -> int:
        """
        Compute the makespan (total completion time).

        Returns:
            Maximum end time across all operations
        """
        return max(
            end_time
            for job_schedule in self.schedule
            for _, end_time in job_schedule
        )

    def is_valid(self, problem: JobShopProblem, verbose: bool = True) -> bool:
        """
        Check if this solution is valid for the given problem.

        Verifies:
        1. Schedule structure matches problem structure
        2. Operation durations match problem specification
        3. Precedence constraints within jobs are respected
        4. No overlap on machines

        Args:
            problem: The job shop problem to check against
            verbose: If True, print detailed error messages

        Returns:
            True if solution is valid, False otherwise
        """
        return check_solution(self, problem, verbose=verbose)

    def __str__(self):
        return f"SolutionJobshop(makespan={self.get_makespan()})"


def check_solution(
    solution: SolutionJobshop,
    problem: JobShopProblem,
    verbose: bool = True
) -> bool:
    """
    Verify that a solution satisfies all Job Shop constraints.

    This function checks:
    1. **Structure**: Schedule has correct number of jobs and operations
    2. **Durations**: Each operation's duration matches the problem
    3. **Precedence**: Within each job, operations respect sequential order
    4. **No Overlap**: On each machine, operations don't overlap in time

    Args:
        solution: The solution to verify
        problem: The problem specification
        verbose: If True, print detailed error messages

    Returns:
        True if all constraints are satisfied, False otherwise

    Example:
        >>> problem = JobShopProblem([...])
        >>> solution = SolutionJobshop([...])
        >>> is_valid = check_solution(solution, problem)
        Constraint satisfied
        >>> print(is_valid)
        True
    """

    # Check 1: Correct number of jobs
    if len(solution.schedule) != problem.n_jobs:
        if verbose:
            print(f"❌ Structure error: Solution has {len(solution.schedule)} jobs, "
                  f"but problem has {problem.n_jobs} jobs")
        return False

    # Check 2 & 3: For each job, verify structure, durations, and precedence
    for job_id in range(problem.n_jobs):
        n_operations = len(problem.list_jobs[job_id])

        if len(solution.schedule[job_id]) != n_operations:
            if verbose:
                print(f"❌ Structure error: Job {job_id} has {n_operations} operations, "
                      f"but solution has {len(solution.schedule[job_id])}")
            return False

        for subjob_id in range(n_operations):
            start, end = solution.schedule[job_id][subjob_id]
            expected_duration = problem.list_jobs[job_id][subjob_id].processing_time
            actual_duration = end - start

            # Check duration
            if actual_duration != expected_duration:
                if verbose:
                    print(f"❌ Duration error: Job {job_id}, Operation {subjob_id} "
                          f"has duration {actual_duration}, expected {expected_duration}")
                return False

            # Check precedence (operation must start after previous one ends)
            if subjob_id > 0:
                prev_end = solution.schedule[job_id][subjob_id - 1][1]
                if start < prev_end:
                    if verbose:
                        print(f"❌ Precedence error: Job {job_id}, Operation {subjob_id} "
                              f"starts at {start}, but previous operation ends at {prev_end}")
                    return False

    # Check 4: No overlap on machines
    for machine_id in problem.job_per_machines:
        # Get all operations scheduled on this machine
        machine_operations = problem.job_per_machines[machine_id]

        # Extract their (start, end) times and sort by start time
        scheduled_operations = [
            solution.schedule[job_id][subjob_id]
            for job_id, subjob_id in machine_operations
        ]
        sorted_operations = sorted(scheduled_operations, key=lambda x: x[0])

        # Check consecutive operations don't overlap
        for i in range(len(sorted_operations) - 1):
            current_end = sorted_operations[i][1]
            next_start = sorted_operations[i + 1][0]

            if next_start < current_end:
                if verbose:
                    print(f"❌ Overlap error: On machine {machine_id}, "
                          f"operations overlap at time {next_start} "
                          f"(one ends at {current_end}, next starts at {next_start})")
                return False

    # All checks passed!
    if verbose:
        print("✓ All constraints satisfied")
    return True
