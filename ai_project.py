import sys
import random
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QLabel, QTableWidget,
                              QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont, QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries

# Constants
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
TIME_SLOTS = ['8:00-9:30', '9:45-11:15', '11:30-13:00', '14:00-15:30', '15:45-17:15']
CLASSROOMS = ['C101', 'C102', 'C103', 'C104', 'C105']
SECTIONS = ['S1', 'S2', 'S3', 'S4', 'S5']
COURSES = ['AI', 'JAVA','SE','DIP','SNA']

def generate_schedule():
    """Generates a  schedule using greedy approach ensuring all sections use all classrooms."""
    schedule = {}
    classroom_assignments = {section: CLASSROOMS.copy() for section in SECTIONS}
    classroom_usage = defaultdict(int)
    section_slot_counts = defaultdict(int)
    classroom_slot_tracker = defaultdict(set)
    
    # Create all possible day-slot combinations and shuffle
    day_slot_combinations = [(day, slot) for day in DAYS for slot in TIME_SLOTS]
    random.shuffle(day_slot_combinations)
    
    for day, slot in day_slot_combinations:
        available_sections = [
            s for s in SECTIONS 
            if section_slot_counts[s] < len(TIME_SLOTS) and classroom_assignments[s]
        ]
        
        if not available_sections:
            break  # All sections have full schedules
        
        # Prioritize sections that need to use more classrooms
        section = min(available_sections, 
                      key=lambda s: (len(classroom_assignments[s]), 
                                     section_slot_counts[s]))
        
        # Use a classroom this section hasn't used yet
        classroom = random.choice(classroom_assignments[section])
        classroom_assignments[section].remove(classroom)
        
        # Ensure classroom not already booked at this time
        while (day, slot) in classroom_slot_tracker[classroom]:
            if not classroom_assignments[section]:
                # Fallback: use any available classroom
                classroom = random.choice([
                    c for c in CLASSROOMS 
                    if (day, slot) not in classroom_slot_tracker[c]
                ])
                break
            classroom = random.choice(classroom_assignments[section])
            classroom_assignments[section].remove(classroom)
        
        # Balance course distribution
        course_counts = defaultdict(int)
        for entry in schedule.values():
            course_counts[entry['course']] += 1
        course = min(COURSES, key=lambda x: course_counts[x])
        if random.random() < 0.3:  # Some randomness
            course = random.choice(COURSES)
        
        # Assign to schedule
        schedule[(day, slot)] = {
            'classroom': classroom,
            'section': section,
            'course': course
        }
        
        # Update trackers
        classroom_usage[classroom] += 1
        section_slot_counts[section] += 1
        classroom_slot_tracker[classroom].add((day, slot))
    
    return schedule

def calculate_schedule_energy(schedule):
    """Calculates the energy of a schedule. Lower energy is better."""
    classroom_usage = defaultdict(int)
    section_classrooms = defaultdict(set)
    
    for entry in schedule.values():
        classroom_usage[entry['classroom']] += 1
        section_classrooms[entry['section']].add(entry['classroom'])
    
    energy = 0
    for section in SECTIONS:
        if len(section_classrooms[section]) != len(CLASSROOMS):
            energy += 1  # Penalty for sections not using all classrooms
    
    # Penalty for uneven classroom usage
    avg_classroom_usage = sum(classroom_usage.values()) / len(CLASSROOMS)
    for classroom in CLASSROOMS:
        energy += abs(classroom_usage[classroom] - avg_classroom_usage)
    
    return energy

def simulated_annealing(schedule, temperature=1000, cooling_rate=0.995, max_iterations=1000):
    """Improves the schedule using simulated annealing."""
    current_schedule = schedule
    current_energy = calculate_schedule_energy(current_schedule)
    
    best_schedule = current_schedule
    best_energy = current_energy
    
    iteration = 0
    while iteration < max_iterations and temperature > 0.1:
        # Randomly make small changes to the schedule (swap classrooms, time slots, etc.)
        new_schedule = generate_schedule()  # Generate a new random schedule
        
        # Calculate the new energy
        new_energy = calculate_schedule_energy(new_schedule)
        
        # Decide whether to accept the new schedule
        if new_energy < current_energy or random.random() < (temperature / 1000):
            current_schedule = new_schedule
            current_energy = new_energy
            
            if new_energy < best_energy:
                best_schedule = new_schedule
                best_energy = new_energy
        
        # Decrease the temperature
        temperature *= cooling_rate
        iteration += 1
    
    return best_schedule

class SchedulerGUI(QMainWindow):
    def __init__(self):  # Corrected from init to __init__
        super().__init__()
        self.setWindowTitle("Classroom Scheduling System")
        self.setGeometry(100, 100, 1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Control Panel
        control_panel = QHBoxLayout()
        self.generate_btn = QPushButton("Generate New Schedule")
        self.generate_btn.clicked.connect(self.generate_schedule)
        control_panel.addWidget(self.generate_btn)
        
        self.status_label = QLabel("Ready to generate schedule")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        control_panel.addWidget(self.status_label)
        
        self.main_layout.addLayout(control_panel)
        
        # Schedule Table
        self.table = QTableWidget()
        self.table.setRowCount(len(DAYS))
        self.table.setColumnCount(len(TIME_SLOTS))
        self.table.setHorizontalHeaderLabels(TIME_SLOTS)
        self.table.setVerticalHeaderLabels(DAYS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)
        
        # Charts
        chart_layout = QHBoxLayout()
        
        self.classroom_chart = QChart()
        self.classroom_view = QChartView(self.classroom_chart)
        self.classroom_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(self.classroom_view)
        
        self.section_chart = QChart()
        self.section_view = QChartView(self.section_chart)
        self.section_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(self.section_view)
        
        self.main_layout.addLayout(chart_layout)
        
        self.current_schedule = None
        self.set_style()

    def set_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QTableWidget {
                background-color: white;
                gridline-color: #ddd;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #3a7ca5;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: #3a7ca5;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2c6085; }
            QChartView { 
                background-color: white; 
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLabel {
                color: #333;
            }
        """)

    def generate_schedule(self):
        try:
            self.status_label.setText("Generating optimized schedule...")
            QApplication.processEvents()  # Update UI immediately
            
            # Generate initial schedule
            initial_schedule = generate_schedule()
            
            # Apply simulated annealing to improve the schedule
            improved_schedule = simulated_annealing(initial_schedule)
            
            # Set the improved schedule as the current schedule
            self.current_schedule = improved_schedule
            
            self.populate_table()
            self.update_charts()
            
            self.status_label.setText("✅ Optimized schedule generated!")
        
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")

    def populate_table(self):
        if not self.current_schedule:
            return
        
        # Color coding for sections
        color_map = {
            'S1': QColor(102, 178, 255),  # Light blue
            'S2': QColor(255, 178, 102),  # Light orange
            'S3': QColor(178, 255, 102),  # Light green
            'S4': QColor(255, 102, 178),  # Light pink
            'S5': QColor(178, 102, 255)   # Light purple
        }
        
        self.table.clearContents()
        for row, day in enumerate(DAYS):
            for col, slot in enumerate(TIME_SLOTS):
                entry = self.current_schedule.get((day, slot), {})
                if entry.get('classroom'):
                    item_text = (f"{entry['section']}\n"
                                 f"{entry['classroom']}\n"
                                 f"{entry['course']}")
                    item = QTableWidgetItem(item_text)
                    item.setBackground(QBrush(color_map[entry['section']]))
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setFont(QFont("Arial", 10, QFont.Bold))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)

    def update_charts(self):
        if not self.current_schedule:
            return
        
        # Classroom Usage Chart
        classroom_usage = defaultdict(int)
        for entry in self.current_schedule.values():
            classroom_usage[entry['classroom']] += 1
        
        classroom_set = QBarSet("Classroom Usage")
        classrooms = sorted(classroom_usage.keys())
        classroom_set.append([classroom_usage[c] for c in classrooms])
        
        classroom_series = QBarSeries()
        classroom_series.append(classroom_set)
        
        self.classroom_chart.removeAllSeries()
        self.classroom_chart.addSeries(classroom_series)
        self.classroom_chart.createDefaultAxes()
        self.classroom_chart.axisX().setCategories(classrooms)
        self.classroom_chart.setTitle("Classroom Utilization")
        self.classroom_chart.legend().setVisible(False)
        self.classroom_chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Section Allocation Chart
        section_alloc = defaultdict(int)
        for entry in self.current_schedule.values():
            section_alloc[entry['section']] += 1
        
        section_set = QBarSet("Section Allocation")
        sections = sorted(section_alloc.keys())
        section_set.append([section_alloc[s] for s in sections])
        
        section_series = QBarSeries()
        section_series.append(section_set)
        
        self.section_chart.removeAllSeries()
        self.section_chart.addSeries(section_series)
        self.section_chart.createDefaultAxes()
        self.section_chart.axisX().setCategories(sections)
        self.section_chart.setTitle("Section Allocation")
        self.section_chart.legend().setVisible(False)
        self.section_chart.setAnimationOptions(QChart.SeriesAnimations)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SchedulerGUI()
    window.show()
    sys.exit(app.exec_())