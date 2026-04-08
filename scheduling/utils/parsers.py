"""
Parsers for scheduling problem data files.
"""

from typing import List, Dict, Tuple


def parse_jobshop_file(filepath: str) -> Tuple[List[List[Dict]], int, int]:
    """
    Parse a jobshop problem file in standard format.

    File format:
        First line: nb_jobs nb_machines
        Following lines: machine_1 duration_1 machine_2 duration_2 ...

    Args:
        filepath: Path to the jobshop data file

    Returns:
        Tuple of (problem_data, nb_jobs, nb_machines)
        where problem_data is a list of jobs, each job is a list of operations
        as dictionaries with 'machine_id' and 'processing_time'
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    problem = []
    nb_jobs = 0
    nb_machines = 0
    processed_line = 0

    for line in lines:
        if line.startswith("#"):
            continue

        split_line = line.split()

        if processed_line == 0:
            nb_jobs = int(split_line[0])
            nb_machines = int(split_line[1])
        else:
            job = []
            for num, n in enumerate(split_line):
                if num % 2 == 0:
                    machine = int(n)
                else:
                    job.append({
                        "machine_id": machine,
                        "processing_time": int(n)
                    })
            problem.append(job)

        processed_line += 1

    return problem, nb_jobs, nb_machines
