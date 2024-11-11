import streamlit as st
import prettytable as prettytable 
import random as rd
from datetime import datetime, timedelta

POPULATION_SIZE = 50
NUMB_OF_ELITE_SCHEDULES = 1
TOURNAMENT_SELECTION_SIZE = 1
MUTATION_RATE = 0.1
GENERATIONS = 2000
UNIVERSITY_START_TIME = datetime.strptime("08:30", "%H:%M")
UNIVERSITY_END_TIME = datetime.strptime("16:45", "%H:%M")
LUNCH_BREAK_START = datetime.strptime("12:45", "%H:%M")
LUNCH_BREAK_END = datetime.strptime("13:30", "%H:%M")
TIME_SLOT_DURATION = timedelta(hours=1)
LAB_TIME_SLOT_DURATION = timedelta(hours=2)
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
BREAKONE_START_TIME = datetime.strptime("10:30", "%H:%M")
BREAKONE_END_TIME = datetime.strptime("10:45", "%H:%M")       
BREAKTWO_START_TIME = datetime.strptime("15:30", "%H:%M")
BREAKTWO_END_TIME = datetime.strptime("15:45", "%H:%M")

class Room:
    def __init__(self, number):
        self._number = number

    def get_number(self):
        return self._number


class Professor:
    def __init__(self, id, name):
        self._id = id
        self._name = name

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name


class Course:
    def __init__(self, number, name, professors, lectures_per_week, labs_per_week=0):
        self._number = number
        self._name = name
        self._professors = professors
        self._lectures_per_week = lectures_per_week
        self._labs_per_week = labs_per_week

    def get_number(self):
        return self._number

    def get_name(self):
        return self._name

    def get_professors(self):
        return self._professors

    def get_lectures_per_week(self):
        return self._lectures_per_week

    def get_labs_per_week(self):
        return self._labs_per_week


class Department:
    def __init__(self, name, courses):
        self._name = name
        self._courses = courses

    def get_name(self):
        return self._name

    def get_courses(self):
        return self._courses

class ClassTime:
    def __init__(self, id, day, time, duration):
        self._id = id
        self._day = day
        self._time = time
        self._duration = duration

    def get_id(self):
        return self._id

    def get_day(self):
        return self._day

    def get_time(self):
        return self._time

    def get_duration(self):
        return self._duration

class Panel:
    def __init__(self, name, num_batches):
        self._name = name
        self._num_batches = num_batches

    def get_name(self):
        return self._name

    def get_num_batches(self):
        return self._num_batches


class Data:
    def __init__(self):
        self._rooms = []
        self._lab_rooms = []
        self._class_times = []
        self._professors = []
        self._courses = []
        self._depts = []
        self._panels = []

    def add_room(self, room):
        self._rooms.append(room)

    def add_lab_room(self, room):
        self._lab_rooms.append(room)

    def add_class_time(self, class_time):
        self._class_times.append(class_time)

    def add_professor(self, professor):
        self._professors.append(professor)

    def add_course(self, course):
        self._courses.append(course)

    def add_dept(self, dept):
        self._depts.append(dept)

    def add_panel(self, panel):
        self._panels.append(panel)

    def get_rooms(self):
        return self._rooms

    def get_lab_rooms(self):
        return self._lab_rooms

    def get_class_times(self):
        return self._class_times

    def get_professors(self):
        return self._professors

    def get_courses(self):
        return self._courses

    def get_depts(self):
        return self._depts

    def get_panels(self):
        return self._panels
    def generate_class_times(self):
        class_time_id = 1
        for day in DAYS_OF_WEEK:
            current_time = UNIVERSITY_START_TIME
            while current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                if not (LUNCH_BREAK_START <= current_time < LUNCH_BREAK_END):
                  
                    class_time = ClassTime(f'MT{class_time_id}', day, current_time.strftime("%H:%M"), TIME_SLOT_DURATION)
                    self.add_class_time(class_time)
                    class_time_id += 1
     
                    if current_time + LAB_TIME_SLOT_DURATION <= UNIVERSITY_END_TIME:
                        lab_time = ClassTime(f'MT{class_time_id}', day, current_time.strftime("%H:%M"), LAB_TIME_SLOT_DURATION)
                        self.add_class_time(lab_time)
                        class_time_id += 1
                current_time += TIME_SLOT_DURATION

class Schedule:
    def __init__(self, data, panel):
        self._data = data
        self._panel = panel
        self._classes = []
        self._fitness = -1
        self._class_numb = 0
        self._is_fitness_changed = True

    def get_classes(self):
        self._is_fitness_changed = True
        return self._classes

    def initialize(self):
        self._classes = []
        available_class_times = self._data.get_class_times().copy()

        for dept in self._data.get_depts():
            for course in dept.get_courses():
                for _ in range(course.get_lectures_per_week()):
                    lecture_class_times = [mt for mt in available_class_times if mt.get_duration() == TIME_SLOT_DURATION]
                    rd.shuffle(lecture_class_times)
                    lecture_class_time = lecture_class_times[0]

                    available_rooms = self._data.get_rooms().copy()
                    rd.shuffle(available_rooms)
                    room = available_rooms.pop()

                    professor = rd.choice(course.get_professors()) if course.get_professors() else None
                    if professor:
                        # Check for conflicts before assigning
                        if self._check_conflicts(lecture_class_time, room, professor):
                            self._classes.append({
                                "panel": self._panel.get_name(),
                                "batch": "All",
                                "department": dept.get_name(),
                                "course": course.get_name(),
                                "room": room.get_number(),
                                "professor": professor.get_name(),
                                "class_time": f"{lecture_class_time.get_day()} {lecture_class_time.get_time()} ({lecture_class_time.get_duration()})"
                            })
                            available_class_times.remove(lecture_class_time)

                # Schedule Labs similarly...
                for _ in range(course.get_labs_per_week()):
                    lab_class_times = [mt for mt in available_class_times if mt.get_duration() == LAB_TIME_SLOT_DURATION]
                    rd.shuffle(lab_class_times)
                    lab_class_time = lab_class_times[0]

                    available_lab_rooms = self._data.get_lab_rooms().copy()
                    if len(available_lab_rooms) < self._panel.get_num_batches():
                        raise ValueError(f"Not enough lab rooms to schedule labs for all batches in panel {self._panel.get_name()}.")

                    rd.shuffle(available_lab_rooms)
                    for batch_num in range(1, self._panel.get_num_batches() + 1):
                        lab_room = available_lab_rooms.pop()
                        professor = rd.choice(course.get_professors()) if course.get_professors() else None
                        if professor:
                         
                            if self._check_conflicts(lab_class_time, lab_room, professor):
                                self._classes.append({
                                    "panel": self._panel.get_name(),
                                    "batch": f"Batch {batch_num}",
                                    "department": dept.get_name(),
                                    "course": f"{course.get_name()} (Lab)",
                                    "room": lab_room.get_number(),
                                    "professor": professor.get_name(),
                                    "class_time": f"{lab_class_time.get_day()} {lab_class_time.get_time()} ({lab_class_time.get_duration()})"
                                })
                            available_class_times.remove(lab_class_time)

        return self

    def _check_conflicts(self, class_time, room, professor):
       
        for cls in self._classes:
            if cls["class_time"] == f"{class_time.get_day()} {class_time.get_time()} ({class_time.get_duration()})":
                if cls["room"] == room.get_number() or cls["professor"] == professor.get_name():
                    return False
        return True

    def get_fitness(self):
        if self._is_fitness_changed:
            self._fitness = self.calculate_fitness()
            self._is_fitness_changed = False
        return self._fitness

    def calculate_fitness(self):
        conflicts = 0
        classes = self.get_classes()
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                classA = classes[i]
                classB = classes[j]
               
                if classA["class_time"] == classB["class_time"]:
                    
                    if classA["room"] == classB["room"]:
                        conflicts += 1
                 
                    if classA["professor"] == classB["professor"]:
                        conflicts += 1
                    
                    if classA["batch"] == classB["batch"] and classA["batch"] != "All":
                        conflicts += 1
        return 1 / (1 + conflicts)
class Population:
    def __init__(self, size, data):
        self._schedules = []
        for _ in range(size):
            for panel in data.get_panels():
                self._schedules.append(Schedule(data, panel).initialize())

    def get_schedules(self):
        return self._schedules

class GeneticAlgorithm:
    def evolve(self, population):
        return self._mutate_population(self._crossover_population(population))

    def _crossover_population(self, pop):
        crossover_pop = Population(0, pop.get_schedules()[0]._data)
        for i in range(NUMB_OF_ELITE_SCHEDULES):
            crossover_pop.get_schedules().append(pop.get_schedules()[i])
        i = NUMB_OF_ELITE_SCHEDULES
        while i < POPULATION_SIZE:
            schedule1 = self._select_tournament_population(pop).get_schedules()[0]
            schedule2 = self._select_tournament_population(pop).get_schedules()[0]
            crossover_pop.get_schedules().append(self._crossover_schedule(schedule1, schedule2))
            i += 1
        return crossover_pop

    def _mutate_population(self, population):
        for i in range(NUMB_OF_ELITE_SCHEDULES, POPULATION_SIZE):
            self._mutate_schedule(population.get_schedules()[i])
        return population

    def _crossover_schedule(self, schedule1, schedule2):
        crossover_schedule = Schedule(schedule1._data, schedule1._panel).initialize()
        for i in range(len(crossover_schedule.get_classes())):
            if rd.random() > 0.5:
                crossover_schedule.get_classes()[i] = schedule1.get_classes()[i]
            else:
                crossover_schedule.get_classes()[i] = schedule2.get_classes()[i]
        return crossover_schedule

    def _mutate_schedule(self, mutate_schedule):
        schedule = Schedule(mutate_schedule._data, mutate_schedule._panel).initialize()
        mutate_schedule._classes = schedule.get_classes()

    def _select_tournament_population(self, pop):
        tournament_pop = Population(0, pop.get_schedules()[0]._data)
        for _ in range(TOURNAMENT_SELECTION_SIZE):
            tournament_pop.get_schedules().append(pop.get_schedules()[rd.randrange(0, len(pop.get_schedules()))])
        tournament_pop.get_schedules().sort(key=lambda x: x.get_fitness(), reverse=True)
        return tournament_pop

class PrettyTableDisplay:
    def print_schedule_as_table(self, schedule):
        table = prettytable.PrettyTable(['Panel', 'Batch', 'Department', 'Course', 'Room', 'Professor', 'Class Time'])
        for cls in schedule.get_classes():
            table.add_row([
                cls["panel"],
                cls["batch"],
                cls["department"],
                cls["course"],
                cls["room"],
                cls["professor"],
                cls["class_time"]
            ])
        st.text(table)

def main():
    st.title('University Timetable Scheduling')
    st.header('Input Data')

    data = Data()


    room_count = st.number_input('Number of Rooms:', min_value=1, max_value=20, value=5, key='room_count')
    for i in range(room_count):
        room_number = st.text_input(f'Room {i + 1} Number:', key=f'room_number_{i}')
        data.add_room(Room(room_number))

   
    lab_room_count = st.number_input('Number of Lab Rooms:', min_value=1, max_value=20, value=5, key='lab_room_count')
    for i in range(lab_room_count):
        lab_room_number = st.text_input(f'Lab Room {i + 1} Number:', key=f'lab_room_number_{i}')
        data.add_lab_room(Room(lab_room_number))

    
    data.generate_class_times()

    
    professor_count = st.number_input('Number of Professors:', min_value=1, max_value=50, value=10, key='professor_count')
    for i in range(professor_count):
        professor_name = st.text_input(f'Professor {i + 1} Name:', key=f'professor_name_{i}')
        data.add_professor(Professor(f'I{i + 1}', professor_name))

    
    dept_count = st.number_input('Number of Departments:', min_value=1, max_value=5, value=2, key='dept_count')
    for i in range(dept_count):
        dept_name = st.text_input(f'Department {i + 1} Name:', key=f'dept_name_{i}')
        course_count = st.number_input(f'Number of Courses in {dept_name}:', min_value=1, max_value=20, value=3, key=f'course_count_{i}')
        courses = []
        for j in range(course_count):
            course_name = st.text_input(f'Course {j + 1} Name in {dept_name}:', key=f'course_name_{i}_{j}')
            course_lectures = st.number_input(f'Number of Lectures per Week for {course_name}:', min_value=1, max_value=10, value=3, key=f'course_lectures_{i}_{j}')
            course_labs = st.number_input(f'Number of Labs per Week for {course_name}:', min_value=0, max_value=5, value=1, key=f'course_labs_{i}_{j}')
            professor_options = [prof.get_name() for prof in data.get_professors()]
            selected_professors = st.multiselect(f'Professors for {course_name}:', professor_options, key=f'professors_{i}_{j}')
            professors = [prof for prof in data.get_professors() if prof.get_name() in selected_professors]
            courses.append(Course(f'C{j + 1}', course_name, professors, course_lectures, course_labs))
        data.add_dept(Department(dept_name, courses))


    panel_count = st.number_input('Number of Panels:', min_value=1, max_value=15, value=2, key='panel_count')
    for i in range(panel_count):
        panel_name = st.text_input(f'Panel {i + 1} Name:', key=f'panel_name_{i}')
        num_batches = st.number_input(f'Number of Batches in {panel_name}:', min_value=1, max_value=10, value=2, key=f'num_batches_{i}')
        data.add_panel(Panel(panel_name, num_batches))

    if st.button('Generate Timetable'):
        population = Population(POPULATION_SIZE, data)
        genetic_algorithm = GeneticAlgorithm()
        for generation in range(GENERATIONS):
            population = genetic_algorithm.evolve(population)
            best_schedule = max(population.get_schedules(), key=lambda s: s.get_fitness())
            if best_schedule.get_fitness() == 1.0:
                break

        st.header("Generated Timetable")
        for panel in data.get_panels():
            st.subheader(f"Panel: {panel.get_name()}")
            panel_schedules = [s for s in population.get_schedules() if s._panel == panel]
            if panel_schedules:
                best_panel_schedule = max(panel_schedules, key=lambda s: s.get_fitness())
                display = PrettyTableDisplay()
                display.print_schedule_as_table(best_panel_schedule)
            else:
                st.write(f"No schedule generated for panel {panel.get_name()}.")

if __name__ == '__main__':
    main()
