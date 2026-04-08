"""
TP2 - Benchmarking: RC-ALBP Solver Performance Analysis

Run the CP-SAT solver on multiple realistic instances derived from RCPSP problems.
Collect results in a dataframe for analysis.

This script:
1. Loads RCPSP instances from PSPLib
2. Converts them to RC-ALBP problems
3. Solves with CP-SAT
4. Stores results for analysis
"""

import time
import pandas as pd
from typing import Dict, List, Optional

from discrete_optimization.generic_tools.cp_tools import ParametersCp

from scheduling.tp2_assembly_line_balancing.problem import RCALBPProblem, RCALBPSolution
from scheduling.tp2_assembly_line_balancing.utils import load_rcpsp_as_albp
from scheduling.tp2_assembly_line_balancing.solutions import RCALBPCpSatSolver


def benchmark_instance(
    instance_name: str,
    nb_stations: int = 3,
    time_limit: int = 60,
    seed: int = 42,
) -> Dict:
    """
    Benchmark a single instance.

    Args:
        instance_name: RCPSP instance name (e.g., "j301_1")
        nb_stations: Number of assembly line stations
        time_limit: CP-SAT time limit in seconds
        seed: Random seed

    Returns:
        Dictionary with results
    """
    print(f"\n{'='*80}")
    print(f"Benchmarking: {instance_name} with {nb_stations} stations")
    print(f"{'='*80}\n")

    result = {
        "instance": instance_name,
        "nb_stations": nb_stations,
        "nb_tasks": 0,
        "nb_resources": 0,
        "nb_precedences": 0,
        "best_bound": None,
        "cycle_time": None,
        "solve_time": None,
        "is_optimal": False,
        "is_feasible": False,
        "is_valid": False,
        "status": "UNKNOWN",
    }

    try:
        # Load and convert problem
        problem = load_rcpsp_as_albp(
            instance_name=instance_name,
            nb_stations=nb_stations,
            seed=seed,
        )

        result["nb_tasks"] = problem.nb_tasks
        result["nb_resources"] = problem.nb_resources
        result["nb_precedences"] = len(problem.precedences)

        print(f"Problem: {problem.nb_tasks} tasks, {problem.nb_resources} resources")

        # Solve using discrete-optimization API
        start_time = time.time()
        cp_solver = RCALBPCpSatSolver(problem)
        params_cp = ParametersCp.default_cpsat()
        result_storage = cp_solver.solve(
            parameters_cp=params_cp,
            time_limit=time_limit,
            ortools_cpsat_solver_kwargs={"log_search_progress": True}
        )
        solve_time = time.time() - start_time

        result["solve_time"] = solve_time

        if len(result_storage) > 0:
            solution: RCALBPSolution = result_storage.get_best_solution()
            result["status"] = "SOLVED"
            result["cycle_time"] = solution.cycle_time
            result["is_feasible"] = True

            # Get best objective bound from solver
            best_bound = cp_solver.get_current_best_internal_objective_bound()
            result["best_bound"] = best_bound

            # Check validity
            is_valid = problem.satisfy(solution)
            result["is_valid"] = is_valid

            # Check if optimal using solver status
            from discrete_optimization.generic_tools.do_solver import StatusSolver
            result["is_optimal"] = (cp_solver.status_solver == StatusSolver.OPTIMAL)

            # Compute gap from best bound
            gap = solution.cycle_time - best_bound
            result["gap"] = gap
            result["gap_percent"] = (gap / best_bound * 100) if best_bound > 0 else 0

            print(f"\n✓ Solution found!")
            print(f"  Cycle time: {solution.cycle_time}")
            print(f"  Best bound: {best_bound}")
            print(f"  Solve time: {solve_time:.2f}s")
            print(f"  Gap: {gap} ({result['gap_percent']:.1f}%)")
            print(f"  Optimal: {result['is_optimal']}")
            print(f"  Valid: {is_valid}")

        else:
            result["status"] = "NO_SOLUTION"
            print("\n✗ No solution found within time limit")

    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
        print(f"\n✗ Error: {e}")

    return result


def run_benchmark_suite(
    instances: Optional[List[str]] = None,
    nb_stations_list: Optional[List[int]] = None,
    time_limit: int = 60,
    output_file: str = "benchmark_results.csv",
) -> pd.DataFrame:
    """
    Run benchmarks on multiple instances and configurations.

    Args:
        instances: List of RCPSP instance names to test
        nb_stations_list: List of station counts to test
        time_limit: CP-SAT time limit per instance
        output_file: CSV file to save results

    Returns:
        DataFrame with all results
    """
    # Default instances: small to medium RCPSP problems
    if instances is None:
        instances = [
            "j301_1", "j301_2", "j301_3",  # 30 tasks
            "j601_1", "j601_2",             # 60 tasks
            "j1201_1",                       # 120 tasks (large)
        ]

    if nb_stations_list is None:
        nb_stations_list = [2, 3, 4]

    print("\n" + "="*80)
    print("  RC-ALBP BENCHMARKING SUITE")
    print("="*80)
    print(f"\nInstances: {len(instances)}")
    print(f"Station configurations: {nb_stations_list}")
    print(f"Time limit: {time_limit}s per instance")
    print(f"Total runs: {len(instances) * len(nb_stations_list)}")

    results = []

    for instance in instances:
        for nb_stations in nb_stations_list:
            result = benchmark_instance(
                instance_name=instance,
                nb_stations=nb_stations,
                time_limit=time_limit,
            )
            results.append(result)

    # Create DataFrame
    df = pd.DataFrame(results)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}\n")

    return df


def analyze_results(df: pd.DataFrame):
    """
    Analyze and print summary statistics from benchmark results.

    Args:
        df: DataFrame with benchmark results
    """
    print("\n" + "="*80)
    print("  BENCHMARK ANALYSIS")
    print("="*80 + "\n")

    # Overall statistics
    total_runs = len(df)
    solved = df[df['status'] == 'SOLVED'].shape[0]
    valid = df[df['is_valid'] == True].shape[0]
    optimal = df[df['is_optimal'] == True].shape[0]

    print(f"Total runs: {total_runs}")
    print(f"Solved: {solved}/{total_runs} ({solved/total_runs*100:.1f}%)")
    print(f"Valid: {valid}/{total_runs} ({valid/total_runs*100:.1f}%)")
    print(f"Optimal: {optimal}/{total_runs} ({optimal/total_runs*100:.1f}%)")

    # Solve time statistics
    solved_df = df[df['status'] == 'SOLVED']
    if not solved_df.empty:
        print(f"\nSolve Time Statistics:")
        print(f"  Mean: {solved_df['solve_time'].mean():.2f}s")
        print(f"  Median: {solved_df['solve_time'].median():.2f}s")
        print(f"  Min: {solved_df['solve_time'].min():.2f}s")
        print(f"  Max: {solved_df['solve_time'].max():.2f}s")

    # Gap statistics
    valid_df = df[df['is_valid'] == True]
    if not valid_df.empty and 'gap_percent' in valid_df.columns:
        print(f"\nOptimality Gap Statistics:")
        print(f"  Mean: {valid_df['gap_percent'].mean():.2f}%")
        print(f"  Median: {valid_df['gap_percent'].median():.2f}%")
        print(f"  Min: {valid_df['gap_percent'].min():.2f}%")
        print(f"  Max: {valid_df['gap_percent'].max():.2f}%")

    # Performance by instance size
    if 'nb_tasks' in df.columns:
        print(f"\nPerformance by Instance Size:")
        size_analysis = df.groupby('nb_tasks').agg({
            'is_valid': 'mean',
            'solve_time': 'mean',
            'gap_percent': 'mean'
        }).round(2)
        print(size_analysis)

    # Performance by number of stations
    if 'nb_stations' in df.columns:
        print(f"\nPerformance by Number of Stations:")
        station_analysis = df.groupby('nb_stations').agg({
            'is_valid': 'mean',
            'solve_time': 'mean',
            'gap_percent': 'mean'
        }).round(2)
        print(station_analysis)

    print("\n" + "="*80)


def main():
    """Main benchmarking function."""

    print("\n" + "="*80)
    print("  TP2 - RC-ALBP BENCHMARK")
    print("="*80)

    # Define test instances (start small!)
    instances = [
        "j301_1", "j301_2", "j301_3",  # 30 tasks, 4 resources
    ]

    nb_stations_list = [2, 3, 4]
    time_limit = 30  # seconds per instance

    print("\n📊 This script will:")
    print("   1. Load RCPSP instances from PSPLib")
    print("   2. Convert to RC-ALBP problems")
    print("   3. Solve with CP-SAT")
    print("   4. Collect results in DataFrame")
    print("   5. Save to CSV for analysis")

    print("\n⚠️  IMPORTANT: Implement the solver in solutions.py first!")
    print("   The solver must be working to run this benchmark.\n")

    # Run benchmark
    try:
        df = run_benchmark_suite(
            instances=instances,
            nb_stations_list=nb_stations_list,
            time_limit=time_limit,
            output_file="tp2_benchmark_results.csv",
        )

        # Analyze results
        analyze_results(df)

        # Display DataFrame
        print("\nDetailed Results:")
        print(df.to_string(index=False))

        print("\n💡 Next steps:")
        print("   - Analyze results in Jupyter notebook")
        print("   - Plot cycle time vs instance size")
        print("   - Compare different station configurations")
        print("   - Identify which instances are hardest")

    except ImportError:
        print("\n❌ Error: Solver not implemented yet!")
        print("   Complete solutions.py first, then run this benchmark.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()