# Scheduling Problems - Practical Course

Welcome to the Scheduling Problems course! This hands-on course teaches you how to model and solve real-world scheduling problems using both heuristic and mathematical methods (primarily Constraint Programming with OR-Tools CP-SAT).

## 📚 Course Structure

This course is organized into **4 modules** that build upon each other:

```
Lesson 1: RCPSP Introduction      →  TP1: RCPSP Practice
         (Heuristics)                    (CP-SAT Modeling)
              ↓                               ↓
Lesson 2: CP-SAT + Job Shop       →  TP2: Assembly Line Balancing
         (Constraint Programming)         (Advanced CP-SAT)
```

### 🎯 Learning Path

1. **Lesson 1** - Understand scheduling problems through heuristics
2. **Lesson 2** - Master Constraint Programming with CP-SAT
3. **TP1** - Apply CP-SAT to RCPSP (graded practical work)
4. **TP2** - Tackle advanced scheduling with Assembly Line Balancing (graded practical work)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Basic understanding of optimization concepts
- Familiarity with Python programming

### Installation

**Option 1: Using `uv` (recommended)**
```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install dependencies
cd scheduling/
uv sync

# Run any script
uv run python -m scheduling.lesson1_rcpsp.tutorial
```

**Option 2: Using pip**
```bash
pip install discrete-optimization matplotlib numpy pandas
```

---

## 📖 Module Details

### Lesson 1: Introduction to RCPSP
**📁 Location:** `lesson1_rcpsp/`

**What you'll learn:**
- Resource-Constrained Project Scheduling Problem (RCPSP) fundamentals
- Serial Schedule Generation Scheme (SGS) algorithm
- Greedy heuristics for scheduling
- Local search and improvement techniques

**Files:**
- `tutorial.py` - Interactive walkthrough of RCPSP concepts
- `exercises.py` - Practice implementing SGS algorithm
- `solutions.py` - Reference implementations
- `utils.py` - Helper functions for RCPSP

**How to run:**
```bash
# Start with the tutorial
uv run python -m scheduling.lesson1_rcpsp.tutorial

# Then try the exercises
uv run python -m scheduling.lesson1_rcpsp.exercises

# Check solutions when stuck
uv run python -m scheduling.lesson1_rcpsp.solutions
```

**Key takeaways:**
- How to represent scheduling problems
- How heuristics build feasible schedules
- Trade-offs between solution quality and computation time

---

### Lesson 2: Constraint Programming with CP-SAT
**📁 Location:** `lesson2_cpsat/`

**What you'll learn:**
- Constraint Programming fundamentals
- OR-Tools CP-SAT solver
- Modeling techniques for scheduling (interval variables, NoOverlap, Cumulative)
- Job Shop Scheduling Problem

**Files:**
- `cpsat_tutorial.ipynb` - Interactive Jupyter notebook (optional)
- `jobshop_problem.py` - Problem and solution data structures
- `jobshop_utils.py` - Utilities (visualization, instance loading)
- `exercises.py` - Implement a Job Shop CP-SAT solver
- `solutions.py` - Complete reference implementation

**How to run:**
```bash
# Run the solution demo (includes benchmark instances)
uv run python -m scheduling.lesson2_cpsat.solutions

# Optional: Jupyter notebook
jupyter notebook scheduling/lesson2_cpsat/cpsat_tutorial.ipynb
```

**Benchmark instances:**
Test your implementation on classic benchmarks in `data/jobshop/instances/`:
- Fisher & Thompson: `ft06`, `ft10`, `ft20`
- Lawrence: `la01` to `la40`
- Adams, Balas & Zawack: `abz5` to `abz9`
- And many more...

**Example:**
```python
from scheduling.lesson2_cpsat.jobshop_utils import load_instance
from scheduling.lesson2_cpsat.solutions import SolverJobShop

problem = load_instance("ft06")  # Load benchmark
solver = SolverJobShop(problem)
solution = solver.solve(max_time_in_seconds=30)
```

**Key takeaways:**
- How to model scheduling with CP-SAT
- Using interval variables and global constraints
- Solving real benchmark instances optimally

---

### TP1: RCPSP with CP-SAT (Graded Practical Work)
**📁 Location:** `tp1_rcpsp/`

**Objective:**
Apply what you learned in Lessons 1 & 2 to model and solve RCPSP using CP-SAT instead of heuristics.

**What you'll implement:**
- Part 1: Complete CP-SAT model for RCPSP
  - Decision variables (start times, intervals)
  - Precedence constraints
  - **Cumulative resource constraints** (key difference from Job Shop)
  - Objective function

- Part 2: Benchmarking and Comparison Study
  - Compare CP-SAT vs heuristic approaches (SGS, random search)
  - Analyze quality vs computation time trade-offs
  - Run experiments on multiple instances
  - Draw conclusions about when to use each method

**Files:**
- `README.md` - Detailed TP instructions
- `exercises_part1.py` - Your work goes here! (with TODOs)
- `exercises_part2.py` - Benchmarking study (complete code, focus on analysis)
- `solutions_part1.py` - Reference solution (check after attempting)
- `utils.py` - Helper functions and instance loader

**How to run:**
```bash
# Work on Part 1 (implement CP-SAT solver)
uv run python -m scheduling.tp1_rcpsp.exercises_part1

# Check your solution
uv run python -m scheduling.tp1_rcpsp.solutions_part1

# Part 2: Run benchmarking study
uv run python -m scheduling.tp1_rcpsp.exercises_part2
```

**Key difference from Lesson 2:**
- Job Shop: `AddNoOverlap` (machine capacity = 1)
- RCPSP: `AddCumulative` (resource capacity ≥ 1)

**Expected outcome:**
- Part 1: Working CP-SAT solver for RCPSP with cumulative constraints
- Part 2: Analysis of heuristic vs exact methods (quality/time trade-offs)
- Ability to solve and benchmark PSPLib instances
- Understanding of when to use CP-SAT vs heuristics

---

### TP2: Assembly Line Balancing (Graded Practical Work)
**📁 Location:** `tp2_assembly_line_balancing/`

**Objective:**
Tackle an advanced scheduling problem combining task assignment, scheduling, and resource allocation.

**What you'll implement:**
Complete CP-SAT solver for Resource-Constrained Assembly Line Balancing Problem (RC-ALBP):
- Task assignment to stations
- Scheduling within stations
- **Two types of precedence:**
  1. Station precedence: task A's station ≤ task B's station
  2. Temporal precedence: if same station, end[A] ≤ start[B]
- **Resources per station** (not global!)
- **Optional intervals technique** (advanced CP-SAT)

**Files:**
- `README.md` - Complete problem description with visual diagrams
- `problem.py` - Problem and solution classes (uses discrete-optimization API)
- `utils.py` - Instance creation and visualization
- `tutorial.py` - 5-part interactive walkthrough
- `exercises.py` - Your implementation (7 TODOs)
- `solutions.py` - Reference solution
- `benchmark.py` - Performance analysis on multiple instances

**How to run:**
```bash
# Start with the tutorial
uv run python -m scheduling.tp2_assembly_line_balancing.tutorial

# Implement your solution
uv run python -m scheduling.tp2_assembly_line_balancing.exercises

# Check reference solution
uv run python -m scheduling.tp2_assembly_line_balancing.solutions

# Run performance benchmark
uv run python -m scheduling.tp2_assembly_line_balancing.benchmark
```

**Key challenges:**
1. **Optional intervals**: How to model "if task is assigned to station X, then..."
2. **Conditional constraints**: Using `OnlyEnforceIf` for same-station precedence
3. **Per-station resources**: Different from global resource pools

**Example technique (from solutions):**
```python
# Create optional interval per (task, station) pair
for task in tasks:
    for station in stations:
        is_assigned = model.NewBoolVar(f"assigned_{task}_{station}")

        # Interval only "present" if task assigned to this station
        opt_interval = model.NewOptionalIntervalVar(
            start, duration, end,
            is_assigned,  # ← Key: controls presence
            f"interval_{task}_{station}"
        )

        # Now use opt_interval in per-station cumulative constraints
```

**Expected outcome:**
- Master advanced CP-SAT techniques (optional intervals)
- Understand assembly line scheduling
- Solve realistic instances optimally

---

## 🎓 Pedagogical Progression

### From Simple to Complex

1. **Lesson 1**: Simple heuristics → understand the problem
2. **Lesson 2**: Basic CP-SAT → learn the tool
3. **TP1**: Apply CP-SAT to RCPSP → combine knowledge
4. **TP2**: Advanced CP-SAT techniques → master the tool

### From Exploration to Implementation

- **Lessons**: Tutorials with reference solutions provided
- **TPs**: Skeleton code with TODOs for you to complete

### From Abstract to Concrete

- Start with toy examples (3 jobs, 3 machines)
- Progress to benchmark instances (32+ jobs, multiple resources)
- End with realistic problems (assembly lines)

---

## 📊 Data Files

The `data/` directory contains benchmark instances:

### RCPSP Instances (`data/rcpsp/`)
- PSPLib format
- Small: j301_*.sm (30 jobs, 4 resources)
- Medium: j601_*.sm (60 jobs)
- Large: j1201_*.sm (120 jobs)

### Job Shop Instances (`data/jobshop/`)
- Standard format
- Classic benchmarks: ft06, la01, abz5, ta01, etc.
- Used in academic research worldwide

---

## 🛠️ Technical Details

### Using discrete-optimization API

All solvers inherit from `discrete-optimization`'s base classes:

```python
from discrete_optimization.generic_tools.ortools_cpsat_tools import OrtoolsCpSatSolver
from discrete_optimization.generic_tools.cp_tools import ParametersCp

class MySolver(OrtoolsCpSatSolver):
    def __init__(self, problem):
        super().__init__(problem)
        self.variables = {}

    def init_model(self, **kwargs):
        super().init_model(**kwargs)  # Creates self.cp_model
        # Your model building code

    def retrieve_solution(self, cpsolvercb):
        # Extract solution from CP-SAT callback
        return MySolution(...)

# Usage
solver = MySolver(problem)
params_cp = ParametersCp.default_cpsat()
result_storage = solver.solve(
    parameters_cp=params_cp,
    time_limit=60,
    ortools_cpsat_solver_kwargs={"log_search_progress": True}
)
solution = result_storage.get_best_solution()
```

### Visualization

Most modules include visualization tools:
```python
from scheduling.tp1_rcpsp.utils import visualize_solution
visualize_solution(problem, solution)
```

---

## 📝 Assessment

### Grading Criteria (TPs)

**TP1 & TP2** are graded on:
1. **Correctness** (60%): Does your solution satisfy all constraints?
2. **Completeness** (20%): Did you implement all required TODOs?
3. **Code Quality** (10%): Clear, well-structured code
4. **Performance** (10%): Solves benchmark instances within time limits

### Validation

Each TP includes validation:
```python
is_valid = problem.satisfy(solution)  # Check all constraints
makespan = problem.evaluate(solution)  # Compute objective
```

---

## 🔗 Additional Resources

### Going Further

- **discrete-optimization tutorials**: https://airbus.github.io/discrete-optimization/
- **OR-Tools examples**: https://github.com/google/or-tools/tree/stable/examples/python
- **CP-SAT guide**: https://developers.google.com/optimization/cp/cp_solver
- **Scheduling with CP-SAT**: https://developers.google.com/optimization/scheduling

### Getting Help

- Check the `solutions.py` in each module
- Read the README.md in each folder for detailed instructions
- Consult PDF course materials in `course_material/`
- Open an issue on GitHub
- Contact: g-poveda (via issues or personal contact)

---

## 🎯 Learning Objectives Summary

By the end of this course, you will be able to:

✅ Understand and formulate scheduling problems
✅ Implement heuristic algorithms (SGS, local search)
✅ Model scheduling problems with Constraint Programming
✅ Use OR-Tools CP-SAT effectively
✅ Apply interval variables and global constraints
✅ Solve real-world benchmark instances
✅ Master advanced CP-SAT techniques (optional intervals, conditional constraints)
✅ Debug and validate scheduling solutions
✅ Compare different solving approaches (heuristics vs CP)
✅ Work with standard problem formats (PSPLib, Job Shop benchmarks)

---

## 🚦 Quick Start Guide

**New to scheduling?** Start here:
```bash
# 1. Install dependencies
uv sync

# 2. Run Lesson 1 tutorial
uv run python -m scheduling.lesson1_rcpsp.tutorial

# 3. Run Lesson 2 solutions (see CP-SAT in action)
uv run python -m scheduling.lesson2_cpsat.solutions

# 4. Try TP1 exercises
uv run python -m scheduling.tp1_rcpsp.exercises_part1
```

**Already familiar with CP?** Jump to:
```bash
# Go straight to advanced TP2
uv run python -m scheduling.tp2_assembly_line_balancing.tutorial
```

---

Good luck with your learning! 🎓

For questions or feedback, contact g-poveda via GitHub issues.