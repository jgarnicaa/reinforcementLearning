# Lesson 1: Introduction to RCPSP

## Learning Objectives

By the end of this lesson, you will be able to:

* **Define** a Resource Constrained Project Scheduling Problem (RCPSP) and its key components
* **Load and inspect** standard scheduling problem instances using the `discrete-optimization` library
* **Visualize** precedence constraints as a network graph
* **Understand and compute** the Critical Path to find a lower bound for project duration
* **Implement** a fundamental scheduling heuristic: the Serial Schedule Generation Scheme (SGS)
* **Evaluate** the quality of a generated schedule by its makespan

## RCPSP Definition

The Resource Constrained Project Scheduling Problem (RCPSP) consists of:

- **M activities/tasks** with precedence constraints
- If activity j is a successor of activity i, then i must complete before j can start
- **K renewable resources**, each resource k has R_k units available
- Each activity requires specific resources during execution
- Resource capacity constraints must be respected at all times
- Each activity j takes d_j time units to complete
- **Objective**: Minimize the makespan (project completion time)

### Variants

**Multi-mode RCPSP**: Each task can be executed in different modes:
- Mode 1 'Fast mode': high resource consumption, short duration
- Mode 2 'Slow mode': low resource consumption, long duration

## Files in this Lesson

1. **tutorial.py** - Interactive tutorial with examples and explanations
2. **exercises.py** - Exercises to implement yourself
3. **solutions.py** - Complete solutions to exercises

## How to Run

```bash
# Run the tutorial
uv run scheduling/lesson1_rcpsp/tutorial.py

# Try the exercises
uv run scheduling/lesson1_rcpsp/exercises.py

# View solutions
uv run scheduling/lesson1_rcpsp/solutions.py
```

## Topics Covered

1. Loading RCPSP instances from PSPLib
2. Visualizing precedence graphs
3. Computing the critical path
4. Implementing the Serial Generation Scheme (SGS)
5. Building priority-based heuristics
6. Random search for better solutions

## Next Steps

After completing this lesson, proceed to:
- **Lesson 2**: Constraint Programming with CPSat and the Jobshop problem
- **TP1**: Hands-on RCPSP practical exercises