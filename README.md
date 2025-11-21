🏫 Classroom Scheduling System using Simulated Annealing

A PyQt5 Desktop Application

📘 Introduction

This project implements an interactive classroom scheduling system built using Python (PyQt5 + PyQtChart).
The system generates a weekly timetable for sections, classrooms, and courses while ensuring that no conflicts occur.

To improve the quality of the generated timetable, the project incorporates the Simulated Annealing (SA) optimization technique — a probabilistic method widely used for solving NP-hard scheduling and routing problems.

The result is a balanced, visually intuitive, and color-coded schedule with usage analytics.

🚀 Key Features
✅ 1. Conflict-Free Timetable Generation

The initial schedule is generated using a greedy approach that guarantees:

No classroom is double-booked at the same time

No section is assigned more than one class in the same slot

🔥 2. Optimization via Simulated Annealing

The generated schedule is refined using SA. The optimizer focuses on reducing:

Classroom usage imbalance

Sections not covering all classrooms

Overall schedule inconsistencies

SA allows occasional acceptance of worse schedules early on to escape local minima, gradually converging on an improved solution.

🎨 3. Fully Interactive GUI

Built using PyQt5, the interface provides:

A timetable grid (days × time slots)

Color-coded cells for each section

A button to regenerate an optimized schedule

Automatic refresh of tables and charts

📊 4. Visual Analytics (PyQtChart)

Two bar charts are generated dynamically:

Classroom Usage Chart — how many sessions each classroom is used for

Section Allocation Chart — number of sessions assigned per section

Both update instantly with every schedule generation.

📂 Project Structure

This application is a single-file system containing:

| Section / Function              | Purpose                                                   |
| ------------------------------- | --------------------------------------------------------- |
| **Constants**                   | Defines DAYS, TIME_SLOTS, CLASSROOMS, SECTIONS, COURSES   |
| **generate_schedule()**         | Produces a valid initial schedule using greedy heuristics |
| **calculate_schedule_energy()** | Computes penalty score used by SA                         |
| **simulated_annealing()**       | Performs the core optimization loop                       |
| **SchedulerGUI**                | PyQt5 interface, tables, charts, and event handling       |


The optimizer tries to minimize an energy function, where lower energy represents a more balanced and fair schedule.

Components of Energy:
✔ Classroom Coverage

Each section should ideally use all classrooms across the week.
Deviation → penalty applied.

✔ Classroom Load Balancing

All classrooms should be used roughly the same number of times.
Imbalance → penalty increases.

⚙️ Installation & Setup
1. Install Required Libraries

Make sure Python 3.x is installed, then run:

pip install PyQt5 PyQtChart

2. Run the Application

Save the file as:

classroom_scheduler.py


Run using:

python classroom_scheduler.py


Click “Generate New Schedule” to create and optimize timetables.

📈 Example Evaluation (Fill after running)
Metric	Initial (Greedy)	After SA	Improvement
Energy Score	—	—	—
Iterations	—	1000	—
Cooling Rate	—	0.995	—
