"""
TP1 - Part 2: Benchmarking Heuristics vs CP

Compare different solving approaches for RCPSP:
    - SGS with priority rules
    - Random search
    - CP-SAT exact solver

Complete code provided - your task is to:
    1. Run experiments on multiple instances
    2. Analyze results
    3. Draw conclusions about trade-offs
"""
import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from discrete_optimization.rcpsp.problem import RcpspProblem, RcpspSolution
from discrete_optimization.rcpsp.parser import get_data_available
from scheduling.tp1_rcpsp.utils import load_instance, print_problem_stats, compare_solutions
from scheduling.tp1_rcpsp.solutions_part1 import RcpspCpSatSolver
from scheduling.lesson1_rcpsp.solutions import sgs_algorithm, create_priority_permutation


# =============================================================================
# Benchmarking Functions (Complete Implementation)
# =============================================================================

def get_instance_list(max_per_size: int = 10) -> List[str]:
    """
    Get list of available RCPSP instances, grouped by size.

    Returns:
        List of instance names (e.g., ["j301_1", "j301_2", ...])
    """
    files = get_data_available()

    # Extract instance names for single-mode RCPSP (.sm files)
    instances = []
    for filepath in files:
        filename = Path(filepath).stem
        # Filter for j30, j60, j120 instances (single-mode)
        if filename.startswith(('j301_', 'j601_', 'j1201_')):
            instances.append(filename)

    # Group by size
    j30 = sorted([i for i in instances if i.startswith('j301_')])[:max_per_size]
    j60 = sorted([i for i in instances if i.startswith('j601_')])[:max_per_size]
    j120 = sorted([i for i in instances if i.startswith('j1201_')])[:max_per_size]

    return j30 + j60 + j120


def benchmark_instance(
    problem: RcpspProblem,
    instance_name: str,
    sgs_iterations: int = 500,
    cp_time_limit: int = 30
) -> Dict[str, dict]:
    """
    Run all methods on a single instance and collect results.

    Returns:
        Dictionary mapping method_name -> {
            'solution': RcpspSolution,
            'time': float,
            'makespan': float,
            'valid': bool,
            'status': str  # For CP-SAT: 'OPTIMAL', 'FEASIBLE', 'TIMEOUT', etc.
        }
    """
    print(f"\n{'='*80}")
    print(f"Benchmarking: {instance_name} ({problem.n_jobs} tasks)")
    print(f"{'='*80}")

    results = {}

    # Test priority rules (fast heuristics)
    for rule in ["esd", "efd", "lsd", "lfd"]:
        start_time = time.time()

        try:
            perm = create_priority_permutation(problem, rule=rule)
            schedule = sgs_algorithm(problem, perm)
            solution = RcpspSolution(problem=problem, rcpsp_schedule=schedule)
            elapsed = time.time() - start_time

            makespan = problem.evaluate(solution)["makespan"]
            is_valid = problem.satisfy(solution)

            results[f"SGS-{rule.upper()}"] = {
                'solution': solution,
                'time': elapsed,
                'makespan': makespan,
                'valid': is_valid,
                'status': 'HEURISTIC'
            }
            print(f"  SGS-{rule.upper()}: makespan={makespan:.0f}, time={elapsed:.3f}s")
        except Exception as e:
            print(f"  SGS-{rule.upper()}: FAILED ({e})")

    # Random search (more iterations)
    start_time = time.time()
    best_makespan = float('inf')
    best_schedule = None

    try:
        for _ in range(sgs_iterations):
            perm = create_priority_permutation(problem, rule="random")
            schedule = sgs_algorithm(problem, perm)
            makespan_val = schedule[problem.sink_task]["end_time"]

            if makespan_val < best_makespan:
                best_makespan = makespan_val
                best_schedule = schedule

        solution = RcpspSolution(problem=problem, rcpsp_schedule=best_schedule)
        elapsed = time.time() - start_time
        makespan = problem.evaluate(solution)["makespan"]
        is_valid = problem.satisfy(solution)

        results[f"Random({sgs_iterations})"] = {
            'solution': solution,
            'time': elapsed,
            'makespan': makespan,
            'valid': is_valid,
            'status': 'HEURISTIC'
        }
        print(f"  Random({sgs_iterations}): makespan={makespan:.0f}, time={elapsed:.3f}s")
    except Exception as e:
        print(f"  Random: FAILED ({e})")

    # CP-SAT solver (exact/optimal)
    start_time = time.time()
    try:
        solver = RcpspCpSatSolver(problem)
        solution = solver.solve(time_limit=cp_time_limit)[-1][0]
        elapsed = time.time() - start_time

        if solution is not None:
            makespan = problem.evaluate(solution)["makespan"]
            is_valid = problem.satisfy(solution)

            # Determine status from solver
            status = getattr(solver, 'status_solver', None)
            if status:
                from discrete_optimization.generic_tools.do_solver import StatusSolver
                status_str = 'OPTIMAL' if status == StatusSolver.OPTIMAL else 'FEASIBLE'
            else:
                status_str = 'FEASIBLE'

            results["CP-SAT"] = {
                'solution': solution,
                'time': elapsed,
                'makespan': makespan,
                'valid': is_valid,
                'status': status_str
            }
            print(f"  CP-SAT: makespan={makespan:.0f}, time={elapsed:.3f}s, status={status_str}")
        else:
            print(f"  CP-SAT: NO SOLUTION (time={elapsed:.3f}s)")
    except Exception as e:
        print(f"  CP-SAT: FAILED ({e})")

    return results


def run_benchmark_study(
    max_instances_per_size: int = 10,
    sgs_iterations: int = 500,
    cp_time_limit: int = 30
) -> pd.DataFrame:
    """
    Run a complete benchmarking study on multiple instances.

    Args:
        max_instances_per_size: Maximum instances per size category
        sgs_iterations: Number of iterations for random search
        cp_time_limit: Time limit in seconds for CP-SAT

    Returns:
        DataFrame with all benchmark results
    """
    print("\n" + "="*80)
    print("  TP1 - PART 2: COMPREHENSIVE BENCHMARKING STUDY")
    print("="*80 + "\n")

    # Get instance list
    instances = get_instance_list(max_per_size=max_instances_per_size)
    print(f"Selected {len(instances)} instances:")
    print(f"  - j30x: {len([i for i in instances if i.startswith('j301_')])} instances (30 tasks)")
    print(f"  - j60x: {len([i for i in instances if i.startswith('j601_')])} instances (60 tasks)")
    print(f"  - j120x: {len([i for i in instances if i.startswith('j1201_')])} instances (120 tasks)")

    # Collect all results
    all_results = []

    for idx, instance_name in enumerate(instances, 1):
        print(f"\n[{idx}/{len(instances)}] Processing {instance_name}...")

        try:
            # Load problem
            problem = load_instance(instance_name=instance_name)

            # Get instance size
            if instance_name.startswith('j301_'):
                size_category = '30_tasks'
            elif instance_name.startswith('j601_'):
                size_category = '60_tasks'
            else:
                size_category = '120_tasks'

            # Run benchmark
            results = benchmark_instance(
                problem,
                instance_name,
                sgs_iterations=sgs_iterations,
                cp_time_limit=cp_time_limit
            )

            # Store results
            for method_name, result_data in results.items():
                all_results.append({
                    'instance': instance_name,
                    'size_category': size_category,
                    'n_tasks': problem.n_jobs,
                    'method': method_name,
                    'makespan': result_data['makespan'],
                    'time': result_data['time'],
                    'valid': result_data['valid'],
                    'status': result_data['status']
                })

        except Exception as e:
            print(f"  ✗ Error processing {instance_name}: {e}")
            continue

    # Convert to DataFrame
    df = pd.DataFrame(all_results)

    # Compute best makespan per instance
    best_makespans = df.groupby('instance')['makespan'].min().to_dict()
    df['best_makespan'] = df['instance'].map(best_makespans)
    df['gap_to_best'] = ((df['makespan'] - df['best_makespan']) / df['best_makespan'] * 100)
    df['is_best'] = df['makespan'] == df['best_makespan']

    print("\n" + "="*80)
    print("  BENCHMARK COMPLETE")
    print("="*80)

    return df


def compute_head_to_head_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute head-to-head comparison matrix between methods.

    Returns:
        DataFrame where cell (i,j) shows: wins/ties/losses of method i vs method j
    """
    methods = sorted(df['method'].unique())
    instances = df['instance'].unique()

    # Create matrix to store results
    comparison_matrix = pd.DataFrame(
        index=methods,
        columns=methods,
        dtype=object
    )

    for method_a in methods:
        for method_b in methods:
            if method_a == method_b:
                comparison_matrix.loc[method_a, method_b] = '-'
                continue

            wins = 0
            ties = 0
            losses = 0

            for instance in instances:
                # Get makespans for both methods on this instance
                makespan_a = df[(df['instance'] == instance) & (df['method'] == method_a)]['makespan']
                makespan_b = df[(df['instance'] == instance) & (df['method'] == method_b)]['makespan']

                if len(makespan_a) > 0 and len(makespan_b) > 0:
                    ma = makespan_a.values[0]
                    mb = makespan_b.values[0]

                    if ma < mb:
                        wins += 1
                    elif ma == mb:
                        ties += 1
                    else:
                        losses += 1

            comparison_matrix.loc[method_a, method_b] = f"{wins}/{ties}/{losses}"

    return comparison_matrix


def print_aggregated_statistics(df: pd.DataFrame):
    """
    Print comprehensive aggregated statistics tables.
    """
    print("\n" + "="*80)
    print("  AGGREGATED STATISTICS TABLES")
    print("="*80 + "\n")

    # Table 1: Overall performance per method
    print("TABLE 1: Overall Performance per Method")
    print("-" * 80)

    stats_overall = df.groupby('method').agg({
        'makespan': ['mean', 'median', 'std', 'min', 'max'],
        'time': ['mean', 'median', 'std'],
        'gap_to_best': ['mean', 'median', 'std'],
        'is_best': 'sum'
    }).round(2)

    stats_overall.columns = ['_'.join(col).strip() for col in stats_overall.columns.values]
    stats_overall = stats_overall.rename(columns={'is_best_sum': 'num_best'})
    print(stats_overall.to_string())

    # Table 2: Performance by instance size
    print("\n\nTABLE 2: Performance by Instance Size")
    print("-" * 80)

    stats_by_size = df.groupby(['size_category', 'method']).agg({
        'makespan': 'mean',
        'time': 'mean',
        'gap_to_best': 'mean',
        'is_best': 'sum'
    }).round(2)

    stats_by_size = stats_by_size.rename(columns={'is_best': 'num_best'})
    print(stats_by_size.to_string())

    # Table 3: Win rates
    print("\n\nTABLE 3: Win Rate (% of instances where method found best solution)")
    print("-" * 80)

    total_instances = df['instance'].nunique()
    win_rates = df[df['is_best']].groupby('method').size() / total_instances * 100
    win_rates = win_rates.sort_values(ascending=False)

    for method, rate in win_rates.items():
        print(f"  {method:<20s}: {rate:5.1f}%")

    # Table 4: Speed comparison
    print("\n\nTABLE 4: Speed Ranking (fastest to slowest)")
    print("-" * 80)

    speed_rank = df.groupby('method')['time'].mean().sort_values()
    for rank, (method, avg_time) in enumerate(speed_rank.items(), 1):
        print(f"  {rank}. {method:<20s}: {avg_time:8.4f}s (avg)")

    # Table 5: Quality-Time Efficiency (lower gap per second is better)
    print("\n\nTABLE 5: Quality-Time Efficiency (Gap % per Second - lower is better)")
    print("-" * 80)

    efficiency = df.groupby('method').apply(
        lambda x: (x['gap_to_best'].mean() / x['time'].mean() if x['time'].mean() > 0 else float('inf'))
    ).sort_values()

    for method, eff in efficiency.items():
        print(f"  {method:<20s}: {eff:8.2f}")

    # Table 6: CP-SAT optimality rate
    print("\n\nTABLE 6: CP-SAT Optimality Analysis")
    print("-" * 80)

    cpsat_data = df[df['method'] == 'CP-SAT']
    if len(cpsat_data) > 0:
        total = len(cpsat_data)
        optimal = (cpsat_data['status'] == 'OPTIMAL').sum()
        feasible = (cpsat_data['status'] == 'FEASIBLE').sum()

        print(f"  Total instances:     {total}")
        print(f"  Optimal solutions:   {optimal} ({optimal/total*100:.1f}%)")
        print(f"  Feasible solutions:  {feasible} ({feasible/total*100:.1f}%)")

        # By size
        print("\n  Optimality by instance size:")
        for size in ['30_tasks', '60_tasks', '120_tasks']:
            size_data = cpsat_data[cpsat_data['size_category'] == size]
            if len(size_data) > 0:
                opt_count = (size_data['status'] == 'OPTIMAL').sum()
                print(f"    {size:<15s}: {opt_count}/{len(size_data)} ({opt_count/len(size_data)*100:.1f}%)")

    print("\n" + "="*80 + "\n")


def analyze_and_visualize(df: pd.DataFrame, save_plots: bool = True):
    """
    Analyze benchmark results and create visualizations.

    Args:
        df: DataFrame with benchmark results
        save_plots: If True, save plots to files
    """
    print("\n" + "="*80)
    print("  ANALYSIS AND VISUALIZATION")
    print("="*80 + "\n")

    methods = sorted(df['method'].unique())
    size_order = ['30_tasks', '60_tasks', '120_tasks']
    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    # =========================================================================
    # FIGURE 1: Main Performance Plots (2x3 grid)
    # =========================================================================
    fig1 = plt.figure(figsize=(18, 11))

    # -------------------------------------------------------------------------
    # 1. Quality vs Time (Scatter Plot)
    # -------------------------------------------------------------------------
    ax1 = plt.subplot(2, 3, 1)

    for method, color in zip(methods, colors):
        method_data = df[df['method'] == method]
        ax1.scatter(
            method_data['time'],
            method_data['makespan'],
            label=method,
            alpha=0.6,
            s=50,
            color=color
        )

    ax1.set_xlabel('Computation Time (s)', fontsize=10)
    ax1.set_ylabel('Makespan', fontsize=10)
    ax1.set_title('Quality vs Computation Time', fontsize=12, fontweight='bold')
    ax1.set_xscale('log')
    ax1.legend(fontsize=7, loc='best')
    ax1.grid(True, alpha=0.3)

    # -------------------------------------------------------------------------
    # 2. Gap Distribution per Method and Size (Boxplot)
    # -------------------------------------------------------------------------
    ax2 = plt.subplot(2, 3, 2)

    # Create boxplot data grouped by method and size
    boxplot_data = []
    boxplot_labels = []
    boxplot_colors = []

    size_color_map = {'30_tasks': '#9ecae1', '60_tasks': '#74c476', '120_tasks': '#fc9272'}

    for size in size_order:
        for method in methods:
            subset = df[(df['method'] == method) & (df['size_category'] == size)]
            if len(subset) > 0:
                boxplot_data.append(subset['gap_to_best'].values)
                boxplot_labels.append(f"{method}\n({size.split('_')[0]})")
                boxplot_colors.append(size_color_map[size])

    positions = list(range(len(boxplot_data)))
    bp = ax2.boxplot(boxplot_data, positions=positions, widths=0.6, patch_artist=True, showfliers=False)

    for patch, color in zip(bp['boxes'], boxplot_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax2.set_ylabel('Gap to Best (%)', fontsize=10)
    ax2.set_title('Gap Distribution per Method and Size', fontsize=12, fontweight='bold')
    ax2.set_xticklabels([])
    ax2.grid(True, axis='y', alpha=0.3)

    # Add legend for sizes
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, alpha=0.7, label=size.replace('_', ' '))
                      for size, color in size_color_map.items()]
    ax2.legend(handles=legend_elements, loc='upper right', fontsize=8)

    # -------------------------------------------------------------------------
    # 3. Win Rate per Method
    # -------------------------------------------------------------------------
    ax3 = plt.subplot(2, 3, 3)
    total_instances = df['instance'].nunique()
    win_counts = df[df['is_best']].groupby('method').size().sort_values(ascending=False)
    win_rates = (win_counts / total_instances * 100)

    bars = ax3.bar(range(len(win_rates)), win_rates.values, color='steelblue', alpha=0.7)
    ax3.set_xticks(range(len(win_rates)))
    ax3.set_xticklabels(win_rates.index, rotation=45, ha='right', fontsize=8)
    ax3.set_ylabel('Win Rate (%)', fontsize=10)
    ax3.set_title('% of Instances with Best Solution', fontsize=12, fontweight='bold')
    ax3.grid(True, axis='y', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=8)

    # -------------------------------------------------------------------------
    # 4. Average Gap per Method
    # -------------------------------------------------------------------------
    ax4 = plt.subplot(2, 3, 4)
    avg_gap = df.groupby('method')['gap_to_best'].mean().sort_values()

    bars = ax4.barh(range(len(avg_gap)), avg_gap.values, color='coral', alpha=0.7)
    ax4.set_yticks(range(len(avg_gap)))
    ax4.set_yticklabels(avg_gap.index, fontsize=9)
    ax4.set_xlabel('Average Gap to Best (%)', fontsize=10)
    ax4.set_title('Average Solution Quality', fontsize=12, fontweight='bold')
    ax4.grid(True, axis='x', alpha=0.3)

    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax4.text(width, bar.get_y() + bar.get_height()/2.,
                f'{width:.1f}%',
                ha='left', va='center', fontsize=8)

    # -------------------------------------------------------------------------
    # 5. Average Time per Method
    # -------------------------------------------------------------------------
    ax5 = plt.subplot(2, 3, 5)
    avg_time = df.groupby('method')['time'].mean().sort_values()

    bars = ax5.barh(range(len(avg_time)), avg_time.values, color='lightgreen', alpha=0.7)
    ax5.set_yticks(range(len(avg_time)))
    ax5.set_yticklabels(avg_time.index, fontsize=9)
    ax5.set_xlabel('Average Time (s)', fontsize=10)
    ax5.set_title('Average Computation Time', fontsize=12, fontweight='bold')
    ax5.set_xscale('log')
    ax5.grid(True, axis='x', alpha=0.3)

    # -------------------------------------------------------------------------
    # 6. Performance by Instance Size
    # -------------------------------------------------------------------------
    ax6 = plt.subplot(2, 3, 6)

    gap_by_size = df.groupby(['method', 'size_category'])['gap_to_best'].mean().unstack(fill_value=0)
    gap_by_size = gap_by_size[size_order]

    x = np.arange(len(gap_by_size.index))
    width = 0.25

    for i, size in enumerate(size_order):
        if size in gap_by_size.columns:
            ax6.bar(x + i * width, gap_by_size[size], width,
                   label=size.replace('_', ' '), alpha=0.7, color=size_color_map[size])

    ax6.set_ylabel('Average Gap (%)', fontsize=10)
    ax6.set_title('Gap by Method and Instance Size', fontsize=12, fontweight='bold')
    ax6.set_xticks(x + width)
    ax6.set_xticklabels(gap_by_size.index, rotation=45, ha='right', fontsize=8)
    ax6.legend(fontsize=8)
    ax6.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()

    if save_plots:
        plot_path = Path(__file__).parent / 'benchmark_results_main.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✓ Main plots saved to: {plot_path}")

    plt.show()

    # =========================================================================
    # FIGURE 2: Head-to-Head Comparison Matrix
    # =========================================================================
    fig2, (ax_wins, ax_heatmap) = plt.subplots(1, 2, figsize=(18, 8))

    h2h_matrix = compute_head_to_head_matrix(df)

    # -------------------------------------------------------------------------
    # Extract win counts for heatmap
    # -------------------------------------------------------------------------
    win_matrix = np.zeros((len(methods), len(methods)))

    for i, method_a in enumerate(methods):
        for j, method_b in enumerate(methods):
            if i != j:
                result = h2h_matrix.loc[method_a, method_b]
                wins = int(result.split('/')[0])
                win_matrix[i, j] = wins

    # Plot heatmap
    im = ax_heatmap.imshow(win_matrix, cmap='RdYlGn', aspect='auto',
                           vmin=0, vmax=df['instance'].nunique())

    cbar = plt.colorbar(im, ax=ax_heatmap)
    cbar.set_label('Number of Wins', rotation=270, labelpad=20, fontsize=10)

    ax_heatmap.set_xticks(np.arange(len(methods)))
    ax_heatmap.set_yticks(np.arange(len(methods)))
    ax_heatmap.set_xticklabels(methods, rotation=45, ha='right', fontsize=9)
    ax_heatmap.set_yticklabels(methods, fontsize=9)

    # Add text annotations
    for i in range(len(methods)):
        for j in range(len(methods)):
            if i != j:
                text = ax_heatmap.text(j, i, h2h_matrix.iloc[i, j],
                                      ha="center", va="center", color="black", fontsize=8)
            else:
                ax_heatmap.text(j, i, "-", ha="center", va="center", color="gray", fontsize=10)

    ax_heatmap.set_title('Head-to-Head: Wins/Ties/Losses\n(row vs column)',
                         fontsize=12, fontweight='bold')
    ax_heatmap.set_xlabel('Opponent', fontsize=10)
    ax_heatmap.set_ylabel('Method', fontsize=10)

    # -------------------------------------------------------------------------
    # Total wins bar chart
    # -------------------------------------------------------------------------
    total_wins = []
    for method in methods:
        wins = 0
        for other in methods:
            if method != other:
                result = h2h_matrix.loc[method, other]
                wins += int(result.split('/')[0])
        total_wins.append(wins)

    sorted_idx = np.argsort(total_wins)[::-1]
    sorted_methods = [methods[i] for i in sorted_idx]
    sorted_wins = [total_wins[i] for i in sorted_idx]

    bars = ax_wins.barh(range(len(sorted_methods)), sorted_wins, color='steelblue', alpha=0.7)
    ax_wins.set_yticks(range(len(sorted_methods)))
    ax_wins.set_yticklabels(sorted_methods, fontsize=10)
    ax_wins.set_xlabel('Total Head-to-Head Wins', fontsize=10)
    ax_wins.set_title('Total Wins Against All Other Methods', fontsize=12, fontweight='bold')
    ax_wins.grid(True, axis='x', alpha=0.3)

    for bar in bars:
        width = bar.get_width()
        ax_wins.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}',
                    ha='left', va='center', fontsize=9, fontweight='bold')

    plt.tight_layout()

    if save_plots:
        plot_path = Path(__file__).parent / 'benchmark_results_h2h.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✓ Head-to-head comparison saved to: {plot_path}")

    plt.show()

    # =========================================================================
    # Print head-to-head matrix
    # =========================================================================
    print("\n" + "="*80)
    print("  HEAD-TO-HEAD COMPARISON MATRIX (Wins/Ties/Losses)")
    print("="*80 + "\n")
    print("Format: Wins/Ties/Losses (row method vs column method)\n")
    print(h2h_matrix.to_string())
    print("\n" + "="*80 + "\n")

    # Print aggregated statistics
    print_aggregated_statistics(df)


def export_results_to_csv(df: pd.DataFrame, filename: str = "tp1_benchmark_results.csv"):
    """
    Export benchmark results to CSV file.

    Args:
        df: DataFrame with results
        filename: Output filename
    """
    csv_path = Path(__file__).parent / filename
    df.to_csv(csv_path, index=False)
    print(f"✓ Results exported to: {csv_path}")


def main():
    """Main function to run comprehensive benchmark study."""

    print("\n" + "="*80)
    print("  TP1 - PART 2: COMPREHENSIVE BENCHMARKING STUDY")
    print("="*80)

    print("\n📊 This benchmark will:")
    print("   1. Test multiple RCPSP instances (small, medium, large)")
    print("   2. Compare SGS heuristics vs CP-SAT exact solver")
    print("   3. Analyze quality vs computation time trade-offs")
    print("   4. Generate comprehensive visualizations")
    print("   5. Export results to CSV\n")

    print("⚙️  Configuration:")
    print("   - Instance sizes: 30, 60, 120 tasks")
    print("   - Methods: SGS (4 rules), Random Search, CP-SAT")
    print("   - CP-SAT timeout: 30s per instance")
    print("   - Random search iterations: 500\n")

    print("⏱️  Estimated time: 5-15 minutes depending on instance count\n")

    input("Press Enter to start the benchmark...")

    # Run the comprehensive benchmark
    df = run_benchmark_study(
        max_instances_per_size=10,  # Adjust for more/fewer instances
        sgs_iterations=500,
        cp_time_limit=10
    )

    # Analyze and visualize results
    analyze_and_visualize(df, save_plots=True)

    # Export to CSV
    export_results_to_csv(df)

    print("\n" + "="*80)
    print("  ANALYSIS QUESTIONS FOR YOUR REPORT")
    print("="*80)
    print("\n1. Solution Quality:")
    print("   - Which method found the most best solutions?")
    print("   - How does CP-SAT compare to heuristics in terms of gap?")
    print("   - Are there instances where heuristics beat CP-SAT?")
    print("\n2. Computation Time:")
    print("   - Which methods are fastest?")
    print("   - Is the extra time for CP-SAT worth it?")
    print("   - How does time scale with instance size?")
    print("\n3. Trade-offs:")
    print("   - Plot the Pareto frontier (quality vs time)")
    print("   - When would you recommend each method?")
    print("   - Does the best method depend on instance size?")
    print("\n4. Insights:")
    print("   - Which priority rule performs best?")
    print("   - How many iterations does random search need?")
    print("   - What percentage of instances reach optimality?")
    print("\n" + "="*80 + "\n")

    print("💡 Next Steps:")
    print("   - Open benchmark_results.png to view all plots")
    print("   - Open tp1_benchmark_results.csv for detailed data")
    print("   - Write your analysis and conclusions")
    print("   - Consider running with more instances or different timeouts\n")


if __name__ == "__main__":
    main()