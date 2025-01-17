import random
from prettytable import PrettyTable

class ClassroomSchedulerGA:
    def __init__(self, subjects, classrooms, days, population_size=100, generations=1000, mutation_rate=0.05):
        self.subjects = subjects
        self.classrooms = classrooms
        self.days = days
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.min_classes_per_day = 4
        self.max_classes_per_day = 5
        self.penalty_factor = 10  # Adjust this value for penalty severity

    # Generate a random timetable configuration
    def create_timetable(self):
        timetable = []
        classroom_usage = {classroom: {day: 0 for day in self.days} for classroom in self.classrooms}

        # Control the number of classes per day to be between 4 and 5
        for day in self.days:
            num_classes_today = random.randint(self.min_classes_per_day, self.max_classes_per_day)
            subjects_for_day = random.sample(self.subjects, num_classes_today)  # Randomly select subjects for the day

            for subject in subjects_for_day:
                while True:
                    classroom = random.choice(self.classrooms)
                    # Ensure the classroom is not used more than 2 times in a day
                    if classroom_usage[classroom][day] < 2:
                        classroom_usage[classroom][day] += 1
                        timetable.append((day, subject, classroom))
                        break  # Exit loop once a valid classroom is found

        return timetable

    # Fitness function to evaluate timetable
    def fitness(self, timetable):
        fitness_score = 0
        classroom_usage = {classroom: {day: 0 for day in self.days} for classroom in self.classrooms}
        classes_per_day = {day: 0 for day in self.days}

        for (day, subject, classroom) in timetable:
            classroom_usage[classroom][day] += 1
            # Penalty if a classroom is used more than 2 times in a day
            if classroom_usage[classroom][day] > 2:
                fitness_score -= 10
            classes_per_day[day] += 1

        # Apply penalty for days with less than 4 or more than 5 classes
        for day, num_classes in classes_per_day.items():
            if num_classes < self.min_classes_per_day:
                fitness_score -= (self.min_classes_per_day - num_classes) * self.penalty_factor
            elif num_classes > self.max_classes_per_day:
                fitness_score -= (num_classes - self.max_classes_per_day) * self.penalty_factor

        return fitness_score

    # Selection function
    def selection(self, population):
        # Select parents based on fitness scores (higher fitness is better)
        population = sorted(population, key=lambda x: self.fitness(x), reverse=True)
        return population[:self.population_size // 2]  # Select top half

    # Crossover to create new timetable from two parents
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    # Mutation function
    def mutate(self, timetable):
        for i in range(len(timetable)):
            if random.random() < self.mutation_rate:
                day, subject, classroom = timetable[i]
                # Randomly change either the classroom or the day
                if random.random() < 0.5:
                    # Change classroom
                    new_classroom = random.choice(self.classrooms)
                    timetable[i] = (day, subject, new_classroom)
                else:
                    # Change day
                    new_day = random.choice(self.days)
                    timetable[i] = (new_day, subject, classroom)
        return timetable

    # Genetic Algorithm
    def run(self):
        population = [self.create_timetable() for _ in range(self.population_size)]

        for generation in range(self.generations):
            # Evaluate fitness
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)
            best_fitness = self.fitness(population[0])

            # Define the ideal fitness (assume 0 means no penalties)
            ideal_fitness = 0

            # Calculate quality percentage
            if best_fitness >= 0:  # When fitness is positive or zero
                quality_percentage = 100
            else:
                quality_percentage = (1 - abs(best_fitness) / abs(ideal_fitness + 1e-6)) * 100  # Avoid divide-by-zero

            # Logging
            print(f"Generation {generation}, Best Fitness: {best_fitness}, Quality: {quality_percentage:.2f}%")

            # Check for optimal solution
            if best_fitness >= 0:
                print(f"Optimal solution found at generation {generation}")
                return population[0]

            # Selection
            parents = self.selection(population)

            # Crossover and Mutation
            new_population = []
            for i in range(0, len(parents), 2):
                parent1 = parents[i]
                parent2 = parents[(i + 1) % len(parents)]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([self.mutate(child1), self.mutate(child2)])

            population = new_population

        print("No optimal solution found, returning best attempt")
        return population[0]

    # Display the timetable in a readable format
    def display_timetable(self, timetable):
        table = PrettyTable()
        table.field_names = ["Day", "Subject", "Classroom"]
        timetable.sort(key=lambda x: (self.days.index(x[0]), x[1]))

        for day in self.days:
            entries = [entry for entry in timetable if entry[0] == day]
            for entry in entries:
                table.add_row([entry[0], entry[1], entry[2]])

        print(table)


# Example usage
subjects = ["DETT", "DS", "MMA", "OOC", "PBL-I", "UE-I", "SCHIE", "ESD"]
classrooms = ["KS107", "KS206", "KS203", "KS106"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

scheduler = ClassroomSchedulerGA(subjects, classrooms, days)
best_timetable = scheduler.run()
scheduler.display_timetable(best_timetable)
