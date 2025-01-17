import random
from prettytable import PrettyTable

class ClassroomSchedulerGA:
    def __init__(self, subjects, classrooms, days, divisions, population_size=100, generations=1000, mutation_rate=0.05):
        self.subjects = subjects
        self.classrooms = classrooms
        self.days = days
        self.divisions = divisions
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.min_classes_per_day = 4
        self.max_classes_per_day = 5
        self.penalty_factor = 10
        # Maximum time slots now matches maximum classes per day
        self.max_time_slots = self.max_classes_per_day

    def create_timetable(self):
        timetable = []
        classroom_usage = {classroom: {day: [] for day in self.days} for classroom in self.classrooms}
        division_schedule = {div: {day: [] for day in self.days} for div in self.divisions}

        # Generate schedule for each division
        for division in self.divisions:
            for day in self.days:
                num_classes_today = random.randint(self.min_classes_per_day, self.max_classes_per_day)
                subjects_for_day = random.sample(self.subjects, num_classes_today)
                # Create available time slots based on number of classes
                available_time_slots = list(range(1, self.max_time_slots + 1))
                
                for subject in subjects_for_day:
                    attempts = 0
                    max_attempts = 50

                    while attempts < max_attempts and available_time_slots:
                        classroom = random.choice(self.classrooms)
                        # Only choose from remaining available time slots
                        time_slot = random.choice(available_time_slots)
                        
                        if self._is_slot_available(classroom_usage, division_schedule, 
                                                 day, classroom, time_slot, division):
                            classroom_usage[classroom][day].append((time_slot, division))
                            division_schedule[division][day].append((time_slot, subject))
                            timetable.append((day, subject, classroom, division, time_slot))
                            # Remove used time slot from available slots
                            available_time_slots.remove(time_slot)
                            break
                        
                        attempts += 1

        return timetable

    def _is_slot_available(self, classroom_usage, division_schedule, day, classroom, time_slot, division):
        # Check if classroom is already in use at this time
        classroom_slots = [slot for slot, _ in classroom_usage[classroom][day]]
        if time_slot in classroom_slots:
            return False

        # Check if division already has a class at this time
        division_slots = [slot for slot, _ in division_schedule[division][day]]
        if time_slot in division_slots:
            return False

        return True

    def mutate(self, timetable):
        for i in range(len(timetable)):
            if random.random() < self.mutation_rate:
                day, subject, classroom, division, time_slot = timetable[i]
                mutation_type = random.choice(['classroom', 'time_slot'])
                
                if mutation_type == 'classroom':
                    new_classroom = random.choice(self.classrooms)
                    timetable[i] = (day, subject, new_classroom, division, time_slot)
                else:
                    # Only mutate to valid time slots (1 to max_classes_per_day)
                    new_time_slot = random.randint(1, self.max_time_slots)
                    timetable[i] = (day, subject, classroom, division, new_time_slot)
        return timetable

    # Rest of the methods remain the same as in the previous version
    def fitness(self, timetable):
        fitness_score = 0
        classroom_usage = {classroom: {day: [] for day in self.days} for classroom in self.classrooms}
        division_schedule = {div: {day: [] for day in self.days} for div in self.divisions}

        for (day, subject, classroom, division, time_slot) in timetable:
            classroom_slots = [slot for slot, _ in classroom_usage[classroom][day]]
            if time_slot in classroom_slots:
                fitness_score -= self.penalty_factor * 2

            division_slots = [slot for slot, _ in division_schedule[division][day]]
            if time_slot in division_slots:
                fitness_score -= self.penalty_factor * 2

            classroom_usage[classroom][day].append((time_slot, division))
            division_schedule[division][day].append((time_slot, subject))

        for division in self.divisions:
            for day in self.days:
                classes_today = len(division_schedule[division][day])
                if classes_today < self.min_classes_per_day:
                    fitness_score -= (self.min_classes_per_day - classes_today) * self.penalty_factor
                elif classes_today > self.max_classes_per_day:
                    fitness_score -= (classes_today - self.max_classes_per_day) * self.penalty_factor

        return fitness_score

    def selection(self, population):
        population = sorted(population, key=lambda x: self.fitness(x), reverse=True)
        return population[:self.population_size // 2]

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def run(self):
        population = [self.create_timetable() for _ in range(self.population_size)]

        for generation in range(self.generations):
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)
            best_fitness = self.fitness(population[0])

            quality_percentage = (1 - abs(best_fitness) / (abs(best_fitness) + 1e-6)) * 100
            print(f"Generation {generation}, Best Fitness: {best_fitness}, Quality: {quality_percentage:.2f}%")

            if best_fitness >= 0:
                print(f"Optimal solution found at generation {generation}")
                return population[0]

            parents = self.selection(population)
            new_population = []
            
            for i in range(0, len(parents), 2):
                parent1 = parents[i]
                parent2 = parents[(i + 1) % len(parents)]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([self.mutate(child1), self.mutate(child2)])

            population = new_population

        return population[0]

    def display_timetable(self, timetable):
        timetable.sort(key=lambda x: (x[3], self.days.index(x[0]), x[4]))
        
        for division in self.divisions:
            print(f"\nTimetable for Division {division}")
            table = PrettyTable()
            table.field_names = ["Day", "Time Slot", "Subject", "Classroom"]
            
            division_schedule = [entry for entry in timetable if entry[3] == division]
            for day in self.days:
                day_schedule = [entry for entry in division_schedule if entry[0] == day]
                for entry in sorted(day_schedule, key=lambda x: x[4]):
                    table.add_row([entry[0], f"Period {entry[4]}", entry[1], entry[2]])
            
            print(table)

# Example usage
subjects = ["DETT", "DS", "MMA", "OOC", "PBL-I", "UE-I", "SCHIE", "ESD"]
classrooms = ["KS107", "KS206", "KS203", "KS106","KS109", "KS207", "KS204", "KS105"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
divisions = ["A", "B", "C", "D", "E", "F", "G"]

scheduler = ClassroomSchedulerGA(subjects, classrooms, days, divisions)
best_timetable = scheduler.run()
scheduler.display_timetable(best_timetable)