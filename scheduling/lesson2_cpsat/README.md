# Lesson 2: Constraint Programming with CPSat and Jobshop Problem

## Learning Objectives

By the end of this lesson, you will be able to:

* **Create** Constraint Programming (CP) models using OR-Tools CPSat
* **Define** integer, boolean, and interval variables
* **Implement** fundamental constraints, including logical conditions (`OnlyEnforceIf`)
* **Understand and use** scheduling-specific global constraints like `NoOverlap` and `AddCumulative`
* **Model and solve** the classic Job Shop Scheduling Problem from scratch
* **Retrieve and visualize** the resulting schedules

## Job Shop Scheduling Problem

The Job Shop Scheduling Problem is defined as follows:

**Given:**
- A set of jobs, each consisting of a sequence of tasks
- Each task must be processed on a specific machine
- Each task has a processing time
- Tasks of a job must be executed in order (precedence constraints)

**Constraints:**
- No task for a job can start until the previous task is completed
- A machine can only work on one task at a time (no overlap)
- A task, once started, must run to completion

**Objective:**
- Minimize the makespan (total time to complete all jobs)

## Files in this Lesson

### Interactive Notebook: Learn (Start Here!)
1. **`cpsat_tutorial.ipynb`** - 
   - Creating models and variables
   - Boolean constraints and logic
   - Enforcement constraints (OnlyEnforceIf)
   - Interval variables for scheduling
   - Global constraints (NoOverlap, Cumulative)
   - Optional intervals
   - Hands-on exercises

### Python Modules
2. **`jobshop_problem.py`** - Problem and solution classes
   - `Subjob`: Single operation (machine + duration)
   - `JobShopProblem`: Complete problem definition
   - `SolutionJobshop`: Solution encoding

3. **`jobshop_utils.py`** - Utilities for jobshop
   - `create_simple_example()`: Create a small 3x3 problem
   - `load_instance(name)`: Load benchmark instances from files
   - `plot_solution()`: Generate Gantt chart visualization
   - `compute_lower_bound()`: Calculate simple lower bounds
   - `print_problem_stats()`: Display problem statistics

4. **`exercises.py`** - Implement your CP solver
   - Exercise: Build `SolverJobShop` class
   - Implement decision variables
   - Add precedence constraints
   - Add resource constraints
   - Define objective function

5. **`solutions.py`** - Complete reference implementation

## How to Run

### Step 1: Interactive CPSat Tutorial
```bash
# Open the notebook in Jupyter
jupyter notebook scheduling/lesson2_cpsat/cpsat_tutorial.ipynb
```

### Step 2: Jobshop Exercises
```bash
# After completing the notebook, work on the jobshop exercises
uv run scheduling/lesson2_cpsat/exercises.py

# Check solutions
uv run scheduling/lesson2_cpsat/solutions.py
```

## Topics Covered

### Part 1: CPSat Fundamentals (Notebook)
1. Creating CP models
2. Integer and boolean variables
3. Basic constraints (Add, implications)
4. Boolean operators (And, Or, Xor, AtLeastOne, AtMostOne)
5. Enforcement constraints (OnlyEnforceIf)
6. Interval variables
7. Global scheduling constraints

### Part 2: Jobshop Problem (Python Modules)
1. Problem definition and data structures
2. Solution encoding
3. Manual solution construction
4. CP model implementation
5. Testing on benchmark instances

## Learning Path

1. **Start with the notebook** - Learn CPSat interactively
2. **Complete notebook exercises** - Practice the concepts
3. **Move to exercises.py** - Implement the Jobshop solver
4. **Test on benchmarks** - Validate your implementation
5. **Compare with solutions.py** - Check your approach

## Benchmark Instances

The `data/jobshop/instances/` folder contains classic benchmark problems:
- `ft06`, `ft10`, `ft20` - Fisher & Thompson instances
- `la01` to `la40` - Lawrence instances
- `abz5` to `abz9` - Adams, Balas & Zawack instances
- `orb01` to `orb10` - Applegate & Cook instances
- `swv01` to `swv20` - Storer, Wu & Vaccari instances
- `yn1` to `yn4` - Yamada & Nakano instances
- `ta01` to `ta80` - Taillard instances

**Loading instances:**
```python
from scheduling.lesson2_cpsat.jobshop_utils import load_instance

# Load a benchmark instance
problem = load_instance("ft06")  # Fisher & Thompson 6x6
problem = load_instance("la01")  # Lawrence 10x5
problem = load_instance("abz5")  # Adams, Balas & Zawack 10x10
```

## Next Steps

After completing this lesson:
- **TP1**: Apply RCPSP modeling with CPSat
- **TP2**: Explore Assembly Line Balancing