import random

class ClassroomSchedulerGA:
    def __init__(self, subjects, classrooms, days, population_size=100, generations=1000, mutation_rate=0.05):
        self.subjects = subjects
        self.classrooms = classrooms
        self.days = days
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    # Generate a random timetable configuration
    def create_timetable(self):
        timetable = []
        for day in self.days:
            day_schedule = {}
            for subject in self.subjects:
                classroom = random.choice(self.classrooms)
                time_slot = random.randint(8, 18)  # Assuming 8:00 AM to 6:00 PM
                if day_schedule.get(classroom, 0) < 2:  # Ensure max 2 lectures per day in a class
                    day_schedule[classroom] = day_schedule.get(classroom, 0) + 1
                    timetable.append((day, subject, classroom, time_slot))
        return timetable

    # Fitness function to evaluate timetable
    def fitness(self, timetable):
        fitness_score = 0
        class_usage = {classroom: {day: 0 for day in self.days} for classroom in self.classrooms}

        for (day, subject, classroom, time_slot) in timetable:
            # Count the usage of each classroom
            class_usage[classroom][day] += 1

            # Check constraint violations
            if class_usage[classroom][day] > 2:
                fitness_score -= 1  # Penalty for more than 2 lectures in the same class on the same day

            week_usage = sum(class_usage[classroom][d] for d in self.days)
            if week_usage > 2:
                fitness_score -= 1  # Penalty for more than 2 lectures in the same class over the week

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
                day, subject, _, time_slot = timetable[i]
                classroom = random.choice(self.classrooms)
                timetable[i] = (day, subject, classroom, time_slot)
        return timetable

    # Genetic Algorithm
    def run(self):
        # Step 1: Create initial population
        population = [self.create_timetable() for _ in range(self.population_size)]

        for generation in range(self.generations):
            # Step 2: Calculate fitness scores
            population = sorted(population, key=lambda x: self.fitness(x), reverse=True)

            # Step 3: Check for a solution that meets constraints
            if self.fitness(population[0]) >= 0:
                print(f"Solution found at generation {generation}")
                return population[0]

            # Step 4: Selection
            parents = self.selection(population)

            # Step 5: Crossover to create new population
            new_population = []
            for i in range(0, len(parents), 2):
                parent1 = parents[i]
                parent2 = parents[(i + 1) % len(parents)]
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([child1, child2])

            # Step 6: Mutation
            population = [self.mutate(individual) for individual in new_population]

        # If no solution found, return best attempt
        print("No optimal solution found, returning best attempt")
        return population[0]

# Example usage
subjects = ["DETT", "DS", "MMA", "OOC", "PBL-I", "UE-I", "SCHIE", "ESD"]
classrooms = ["KS107", "KS206", "KS203", "KS106"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

scheduler = ClassroomSchedulerGA(subjects, classrooms, days)
best_timetable = scheduler.run()
print("Best timetable configuration:", best_timetable)