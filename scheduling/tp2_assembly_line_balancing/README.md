# TP2: Resource-Constrained Assembly Line Balancing (RC-ALBP)

## Overview

This practical work (TP) focuses on a simplified variant of Assembly Line Balancing that combines:
- **SALBP-2** (Simple Assembly Line Balancing - Type 2): Minimize cycle time with fixed stations
- **Resource constraints**: Tasks consume resources that are allocated to workstations

Unlike the full RC-ALBP/L problem (with learning effects), this version focuses on the core scheduling and resource allocation challenges.

## The Assembly Line Concept

### Why "Cycle Time" Matters

An assembly line is **repetitive** - products (e.g., aircraft, cars) flow through stations continuously. Every **cycle time** units, a new product enters the line:

```
TIME ──────────────────────────────────────────────────────────────────►

Cycle 1:     |◄── Cycle Time = 15 ──►|
             ✈️ enters                ✈️ exits
             Station_A → Station_B → Station_C

Cycle 2:                             |◄── Cycle Time = 15 ──►|
                                     ✈️ enters                ✈️ exits
                                     Station_A → Station_B → Station_C

Cycle 3:                                                     |◄── CT = 15 ──►|
                                                             ✈️ enters        ...
```

**The bottleneck station determines the cycle time** - all stations must finish within this time window before the next product arrives.

### Visual Example: Aircraft Assembly

```
                     ASSEMBLY LINE (3 Stations, Cycle Time = 10)

  t=0         t=10        t=20        t=30        t=40
   │           │           │           │           │
   ✈️1         ✈️2         ✈️3         ✈️4         ✈️5
   │           │           │           │           │
   ▼           ▼           ▼           ▼           ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Station_A: [Prepare: 5] [Cut: 4]  ────────────── Total: 9     │
│             ▓▓▓▓▓████                                           │
│                                                                 │
│  Station_B: [Assemble: 3] [Join: 3] [Test: 2] ─── Total: 8     │
│             ▓▓▓███▓▓                                            │
│                                                                 │
│  Station_C: [Package: 6] ──────────────────────── Total: 6     │
│             ▓▓▓▓▓▓                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
              0         5         10        15        20
              └─────────┴─────────┴─────────┴─────────┘
                     Time within cycle

Legend: ▓ = Task execution
        Cycle Time = max(9, 8, 6) = 10 (rounded up)
        Throughput = 1 aircraft / 10 time units
```

### The Optimization Problem

```
GOAL: Minimize Cycle Time (maximize throughput)

DECISION:
  1. Assign tasks to stations
  2. Schedule tasks within each station

CONSTRAINTS:
  ✓ Precedence: "Prepare" before "Assemble", etc.
  ✓ Resources: Worker/Tool capacity per station
  ✓ No overlap: Tasks on same station can't overlap

EXAMPLE - Bad Balancing:
  Station_A: 15 time units  ←── BOTTLENECK! 💥
  Station_B: 5 time units
  Station_C: 3 time units
  → Cycle Time = 15 (Stations B & C are idle!)

EXAMPLE - Good Balancing:
  Station_A: 10 time units
  Station_B: 9 time units   ←── Well balanced! ✓
  Station_C: 10 time units
  → Cycle Time = 10 (All stations utilized!)
```

### Precedence Constraints

Tasks must respect **two types** of precedence:

```
1. STATION PRECEDENCE (Between stations):

   Station_A        Station_B        Station_C
   ┌──────┐        ┌──────┐        ┌──────┐
   │Prepare├───────►│Assemble├──────►│Test  │
   └──────┘        └──────┘        └──────┘

   Rule: If task A in Station 1, task B in Station 2,
         and A → B in precedence graph,
         then Station 1 must be before Station 2

2. TEMPORAL PRECEDENCE (Within same station):

   Station_A (time axis →)
   ┌─────────────────────────────┐
   │ [Prepare]──→[Cut]           │
   │  0─────5    5───9           │
   └─────────────────────────────┘

   Rule: If tasks A and B on same station,
         and A → B in precedence graph,
         then end_time(A) ≤ start_time(B)
```

### Resource Constraints

Each station has **pre-allocated resources**, tasks consume resources:

```
RESOURCES PER STATION:
┌────────────┬─────────┬──────┐
│ Station    │ Worker  │ Tool │
├────────────┼─────────┼──────┤
│ Station_A  │    3    │   2  │
│ Station_B  │    2    │   3  │
└────────────┴─────────┴──────┘

TASK CONSUMPTION:
  "Prepare": 1 Worker, 0 Tool
  "Cut":     1 Worker, 1 Tool

CONSTRAINT:
  At any time t, sum of resources used by active tasks
  on a station ≤ station's resource capacity

Example timeline on Station_A:
  Time: 0────5────9
  Prepare: [1W, 0T]
  Cut:          [1W, 1T]

  ✓ At t=5: Prepare ends, Cut starts (no overlap, OK)
  ✓ If parallel: Would need 2W, 1T → Exceeds Worker capacity! ✗
```

## Problem Definition

### Given
- A fixed number of **workstations** (stations)
- A set of **tasks** with processing times
- **Precedence constraints** between tasks
- Multiple **resource types** (e.g., workers, tools, space)
- **Resource allocation** to each workstation (pre-decided)
- **Resource consumption** by each task

### Decision Variables
- **Task assignment**: Which station executes which task?
- **Task schedule**: When does each task start within the cycle?

### Objective
**Minimize the cycle time** (makespan) - the maximum completion time across all stations

### Constraints
1. **Precedence**: Predecessor tasks must complete before successors, or allocated to a previous station
2. **Resource capacity**: Resource consumption at each station cannot exceed allocation
3. **No overlap**: Tasks on the same station cannot overlap in time

## Files

### Core Problem Classes
- **`problem.py`**: Problem and solution classes following discrete-optimization API
  - `RCALBPProblem`: Inherits from `SchedulingProblem[Task]` and `AllocationProblem[Task, Station]`
  - `RCALBPSolution`: Implements both `SchedulingSolution` and `AllocationSolution` interfaces

### Utilities
- **`utils.py`**: Helper functions
  - `create_simple_instance()`: Generate random instances
  - `create_precedence_example()`: Small example with meaningful names
  - `create_from_rcpsp()`: Convert RCPSP to RC-ALBP (✅ NEW!)
  - `load_rcpsp_as_albp()`: Load realistic instances from PSPLib (✅ NEW!)
  - `visualize_solution()`: Gantt chart visualization
  - `print_solution_info()`: Detailed solution analysis

### Tutorial and Exercises
- **`tutorial.py`**: Interactive walkthrough (run this first!)
- **`exercises.py`**: CP-SAT solver implementation (✅ skeleton ready)
- **`benchmark.py`**: Performance analysis on multiple instances (✅ NEW!)

## How to Run

```bash
# From the repo root (aibt_108/)

# 1. Run the tutorial (start here!)
uv run python -m scheduling.tp2_assembly_line_balancing.tutorial

# 2. View exercises instructions
uv run python -m scheduling.tp2_assembly_line_balancing.exercises

# 3. Test realistic instance creation from RCPSP
uv run python -c "
from scheduling.tp2_assembly_line_balancing.utils import load_rcpsp_as_albp
problem = load_rcpsp_as_albp('j301_1', nb_stations=3)
print(f'Loaded: {problem.nb_tasks} tasks, {problem.nb_stations} stations')
"

# 4. Run benchmark suite (after implementing solver!)
uv run python -m scheduling.tp2_assembly_line_balancing.benchmark
```

## Example Problem

The tutorial uses a small example with **meaningful names**:

### Tasks
- **Prepare** (5 time units)
- **Assemble** (3 time units)
- **Cut** (4 time units)
- **Join** (3 time units)
- **Test** (2 time units)
- **Package** (6 time units)

### Precedence Structure
```
Prepare → Assemble → Test
   ↓         ↓        ↓
  Cut   →  Join  → Package
```

### Stations
- **Station_A**
- **Station_B**

### Resources
- **Worker**: 3 units at Station_A, 2 units at Station_B
- **Tool**: 2 units at Station_A, 3 units at Station_B

### Task Resource Consumption
- **Prepare**: 1 Worker
- **Assemble**: 1 Tool
- **Cut**: 1 Worker, 1 Tool
- **Join**: 1 Tool
- **Test**: 1 Worker, 1 Tool
- **Package**: 2 Workers, 1 Tool

## Key Design Choices

### 1. Hashable Identifiers
Tasks, Stations, and Resources can be **strings or integers** for better readability:
```python
# Meaningful names (recommended for clarity)
tasks = ["Prepare", "Assemble", "Cut"]
stations = ["Station_A", "Station_B"]
resources = ["Worker", "Tool"]

# Or simple identifiers
tasks = ["T1", "T2", "T3"]
stations = ["WS1", "WS2"]
resources = ["R1", "R2"]
```

### 2. Discrete-Optimization Framework
Follows the library's design patterns:
- `SchedulingProblem[Task]`: Provides scheduling methods
- `AllocationProblem[Task, Station]`: Provides allocation methods
- `get_start_time()`, `get_end_time()`, `is_allocated()`: Standard interface

### 3. Evaluation Metrics
```python
eval_dict = problem.evaluate(solution)
# Returns:
# {
#     "cycle_time": float,           # Objective to minimize
#     "penalty_precedence": float,   # Precedence violations
#     "penalty_resource": float,     # Resource over-consumption
#     "penalty_unscheduled": float,  # Tasks without valid schedule
# }
```

## Exercise: CP-SAT Solver

The `exercises.py` file provides a skeleton for implementing a CP-SAT solver. You need to complete **7 TODOs**:

### TODO 1.1: Task Assignment Variables
Create integer variables to assign each task to a station.

### TODO 1.2: Start Time and Interval Variables
Create temporal variables for scheduling tasks within stations.

### TODO 1.3: Station Precedence Constraints
Ensure tasks flow forward through the assembly line:
```
If task A → task B in precedence graph:
  station[A] ≤ station[B]
```

### TODO 1.4: Temporal Precedence (Same Station)
If two tasks are on the same station AND have a precedence relation:
```
end[A] ≤ start[B]
```
**Hint**: Use `OnlyEnforceIf` to make this conditional!

### TODO 1.5: Resource Constraints (⭐ Key Challenge)
Add cumulative constraints **per station**.

**The Challenge**: How to filter tasks by station in CP model?

**Solution**: Use **optional intervals**!
```python
# Create interval per (task, station) pair
# Interval is "present" only if task assigned to that station
for task in tasks:
    for station in stations:
        is_assigned = (assignment[task] == station)
        optional_interval = NewOptionalIntervalVar(
            start[task], duration[task], end[task],
            is_present=is_assigned,
            name=f"interval_{task}_{station}"
        )
```

Then use `AddCumulative` per station with only the intervals "present" at that station.

### TODO 1.6: Objective Function
Minimize the cycle time (maximum end time across all tasks).

### TODO 1.7: Extract Solution
Convert CP-SAT variable values into a `RCALBPSolution` object.

## Learning Objectives

By completing this TP, you will:

1. **Understand** resource-constrained scheduling problems
2. **Model** scheduling problems with the discrete-optimization framework
3. **Implement** CP-SAT solver with optional intervals (advanced technique!)
4. **Use** conditional constraints with `OnlyEnforceIf`
5. **Handle** two types of precedence constraints
6. **Analyze** trade-offs between solution quality and computation time

## Connections to Course Content

### From Lesson 1 (RCPSP)
- Serial Generation Scheme (SGS) heuristic
- Priority rules for task ordering
- Critical path analysis

### From Lesson 2 (CP-SAT + Job Shop)
- Interval variables for scheduling
- `AddCumulative` constraint for resources
- `AddNoOverlap` for tasks on same station
- Precedence constraints

### From TP1 (RCPSP Practical)
- Using `discrete-optimization` library
- Benchmarking methodology
- Solution validation

## Differences from RCPSP

| Aspect | RCPSP | RC-ALBP (this TP) |
|--------|-------|-------------------|
| **Stations** | Not fixed | Fixed number |
| **Objective** | Minimize makespan | Minimize cycle time |
| **Resources** | Renewable, global | Allocated per station |
| **Focus** | Project scheduling | Line balancing |

## Realistic Instances from RCPSP

The `utils.py` module now includes functions to create **realistic** RC-ALBP instances from RCPSP problems:

### How it Works

```python
from scheduling.tp2_assembly_line_balancing.utils import load_rcpsp_as_albp

# Load RCPSP instance j301_1 (30 tasks, 4 resources)
# Convert to RC-ALBP with 3 stations
problem = load_rcpsp_as_albp('j301_1', nb_stations=3)

# Result:
# - Tasks: Same as RCPSP (with precedences, durations)
# - Resources: RCPSP global capacity split across stations
# - Consumption: Same as RCPSP
```

### Conversion Process

1. **Tasks**: Use RCPSP task durations
2. **Precedences**: Use RCPSP precedence graph
3. **Resources**: Split RCPSP global capacity across stations
   - Base allocation: divide equally
   - Add variation (+/- 20%)
   - Ensure total ≤ original capacity
4. **Consumption**: Use RCPSP resource consumption per task

### Available Instances

From PSPLib:
- `j301_X`: 30 tasks, 4 resources
- `j601_X`: 60 tasks, 4 resources
- `j1201_X`: 120 tasks, 4 resources

### Benchmarking

The `benchmark.py` script:
1. Loads multiple RCPSP instances
2. Converts to RC-ALBP with different station counts
3. Solves with CP-SAT
4. Stores results in DataFrame (CSV)
5. Analyzes performance statistics

**Output**: `tp2_benchmark_results.csv` with columns:
- `instance`, `nb_stations`, `nb_tasks`, `nb_resources`
- `cycle_time`, `solve_time`, `gap_percent`
- `is_valid`, `is_optimal`, `status`

## Next Steps

1. **Run the tutorial**: `uv run python -m scheduling.tp2_assembly_line_balancing.tutorial`
2. **Study the problem class**: Understand the data structures
3. **Implement the solver**: Complete the 7 TODOs in `exercises.py`
4. **Test on realistic instances**: Use `load_rcpsp_as_albp()`
5. **Run benchmarks**: Analyze performance with `benchmark.py`
6. **Analyze results**: Load CSV in pandas/Jupyter for visualization

## References

- **SALBP**: Simple Assembly Line Balancing Problem
- **RCALBP/L**: Resource-Constrained Assembly Line Balancing with Learning
- **discrete-optimization**: https://github.com/airbus/discrete-optimization

---

**Status**: ✅ Core framework complete, exercises pending