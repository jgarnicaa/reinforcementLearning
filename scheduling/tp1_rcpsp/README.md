# TP1: RCPSP - Practical Exercises

## Overview

This practical work (TP) combines everything you've learned in Lessons 1 and 2 to solve Resource Constrained Project Scheduling Problems using both heuristic and exact methods.

## Learning Objectives

By completing this TP, you will be able to:

* **Implement** a CP-SAT model for RCPSP from scratch
* **Use** the `AddCumulative` constraint for resource management
* **Compare** heuristic solutions (SGS) with optimal solutions (CP)
* **Handle** real-world constraints (calendars, skills, precedences)
* **Analyze** solution quality and solving performance
* **[Bonus]** Model and solve multi-mode RCPSP

## Prerequisites

**Required:**
- Lesson 1: RCPSP Introduction + SGS implementation
- Lesson 2: CPSat basics + Job Shop solver

**Recommended:**
- Understanding of cumulative resource constraints
- Familiarity with the `discrete-optimization` library

## TP Structure

### Part 1: CP-SAT Model for RCPSP ⭐
**File:** `exercises_part1.py`

Implement a complete CP-SAT solver for standard RCPSP:
- Decision variables (starts, ends, intervals)
- Precedence constraints
- Cumulative resource constraints
- Objective function (minimize makespan)
- Solution extraction

**Challenge:** Unlike Job Shop (NoOverlap), RCPSP uses `AddCumulative` for resources with capacity > 1.

### Part 2: Comparing Heuristics vs CP 📊
**File:** `exercises_part2.py`

Benchmark different solving approaches:
- SGS with various priority rules
- Random search
- CP-SAT exact solver
- Hybrid approaches (SGS + CP warmstart)

**Goal:** Understand trade-offs between solution quality and computation time.

### Part 3: Advanced RCPSP Features 🚀
**File:** `exercises_part3.py` (Bonus)

Handle real-world extensions:
- Resource calendars (availability varies over time)
- Multi-skill resources (tasks require specific skills)
- Multi-mode RCPSP (tasks have alternative execution modes)
- Time windows and deadlines

## Files in this TP

```
tp1_rcpsp/
├── README.md                    # This file
├── problem_definition.py        # RCPSP problem classes
├── exercises_part1.py           # CP model implementation
├── exercises_part2.py           # Benchmarking
├── exercises_part3.py           # Advanced features (bonus)
├── solutions_part1.py           # Reference: CP model
├── solutions_part2.py           # Reference: Benchmarking
├── solutions_part3.py           # Reference: Advanced features
├── utils.py                     # Utility functions
└── test_instances/              # Test problems
    ├── small/                   # 10-30 tasks
    ├── medium/                  # 30-60 tasks
    └── large/                   # 60-120 tasks
```

## How to Work on this TP

### Step 1: Understand the Problem
```python
# Load and explore a test instance
from problem_definition import RcpspProblemCP
from utils import load_instance, print_problem_stats

problem = load_instance("test_instances/small/j30_1.sm")
print_problem_stats(problem)
```

### Step 2: Complete Part 1 (CP Model)
```bash
# Implement the CP-SAT solver
python tp1_rcpsp/exercises_part1.py

# Test your implementation
# Compare with reference solution
python tp1_rcpsp/solutions_part1.py
```

### Step 3: Complete Part 2 (Benchmarking)
```bash
# Run experiments comparing methods
python tp1_rcpsp/exercises_part2.py
```

### Step 4: [Optional] Advanced Features
```bash
# Tackle the bonus exercises
python tp1_rcpsp/exercises_part3.py
```

## Test Instances

We provide several difficulty levels:

### Small (Quick testing)
- **j30_X.sm**: 30 tasks, 4 resources
- **Optimal**: Usually found in < 10 seconds
- **Use for:** Development and debugging

### Medium (Realistic)
- **j60_X.sm**: 60 tasks, 4 resources
- **Near-optimal**: Often found in < 60 seconds
- **Use for:** Evaluation and comparison

### Large (Challenge)
- **j120_X.sm**: 120 tasks, 4 resources
- **Hard instances**: May require > 5 minutes
- **Use for:** Testing scalability

## Deliverables

### Minimum (Required)
- ✅ Working CP-SAT solver (Part 1)
- ✅ Solution on at least 3 test instances
- ✅ Brief analysis comparing SGS vs CP

### Complete (Recommended)
- ✅ All of the above
- ✅ Benchmarking results (Part 2)
- ✅ Performance analysis (time vs quality)

### Advanced (Bonus)
- ✅ All of the above
- ✅ Advanced features implementation (Part 3)
- ✅ Multi-mode RCPSP solver

## Evaluation Criteria

1. **Correctness** (40%): Does your CP model produce valid solutions?
2. **Completeness** (30%): Are all constraints properly implemented?
3. **Analysis** (20%): Quality of your comparison and insights
4. **Code Quality** (10%): Clarity, documentation, structure

## Tips for Success

### 🎯 CP Modeling Tips
- Start with a simple instance (j30_1.sm)
- Test each constraint type separately
- Use the solution checker to validate
- Remember: `AddCumulative` ≠ `AddNoOverlap`!

### 📊 Benchmarking Tips
- Run multiple times for statistical significance
- Track both time and solution quality
- Visualize results (Gantt charts, tables)
- Consider time limits for fair comparison

### 🚀 Advanced Tips
- Multi-mode: One interval per mode + selection logic
- Calendars: Adjust resource availability arrays
- Skills: Add matching constraints between tasks and resources

## Common Pitfalls

❌ **Using NoOverlap instead of AddCumulative**
Resources in RCPSP have capacity > 1!

❌ **Forgetting to update resource availability**
When extracting solutions, check resource usage over time.

❌ **Not setting time limits**
CP solvers can run forever - always set `max_time_in_seconds`.

❌ **Comparing incomparable methods**
SGS with 1000 iterations vs CP with 10s? Be fair!

## Resources

### RCPSP Data Format
- [PSPLib](http://www.om-db.wi.tum.de/psplib/)
- [Standard benchmark instances](http://www.om-db.wi.tum.de/psplib/getdata.cgi)

### OR-Tools Documentation
- [AddCumulative constraint](https://developers.google.com/optimization/scheduling/rcpsp)
- [Scheduling examples](https://developers.google.com/optimization/scheduling)

### Previous Lessons
- Lesson 1: `../lesson1_rcpsp/`
- Lesson 2: `../lesson2_cpsat/`

## Expected Time

- **Part 1 (CP Model)**: 2-3 hours
- **Part 2 (Benchmarking)**: 1-2 hours
- **Part 3 (Advanced)**: 2-4 hours (bonus)

**Total:** 3-5 hours minimum, up to 9 hours with all bonuses.

## Getting Help

1. Review Lesson 2 (Job Shop) - similar structure!
2. Check the utilities in `utils.py`
3. Look at solution validation errors carefully
4. Compare your output with `solutions_partX.py`

---

Good luck! Remember: The goal is to learn, not just to finish. Take time to understand each constraint. 🎓
