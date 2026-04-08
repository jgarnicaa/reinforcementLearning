# AIBT-108: Sequential Decision Making

This repository contains course materials for AIBT-108, covering various approaches to sequential decision making.

## 📚 Course Topics

- **Reinforcement Learning**
- **Planning**
- **Scheduling** ← *Full practical course available*
- **Sequential Games**

---

## 🎯 Scheduling Course

**Location:** `scheduling/`

A hands-on course teaching you to model and solve scheduling problems using heuristics and Constraint Programming (OR-Tools CP-SAT).

### Course Materials

- **Slides & Cheatsheet** - Theoretical foundations (check `scheduling/` directory)
- **2 Interactive Lessons** - Learn by doing
  - Lesson 1: RCPSP with heuristics (Serial Schedule Generation)
  - Lesson 2: CP-SAT fundamentals + Job Shop Problem
- **2 Graded Practicals** - Apply your knowledge
  - TP1: RCPSP with CP-SAT + benchmarking study
  - TP2: Assembly Line Balancing (advanced techniques)

### Quick Start

```bash
# Install dependencies
uv sync

# Start with Lesson 1
uv run python -m scheduling.lesson1_rcpsp.tutorial

# Complete course guide
cat scheduling/README.md
```

**See [`scheduling/README.md`](scheduling/README.md) for the full course guide.**

---

## 🚀 Getting Started

**Prerequisites:**
- Python 3.11+
- `uv` package manager ([install here](https://github.com/astral-sh/uv))

**Installation:**
```bash
cd aibt_108
uv sync
```

**Running course content:**
```bash
uv run python -m scheduling.<module>.<script>
```

---

## 📖 Other Topics

Materials for Reinforcement Learning, Planning, and Sequential Games will be added progressively.
