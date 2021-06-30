import xml.etree.ElementTree as ET
import random
import time

POPULATION = 10
SELECTION = int(POPULATION * 0.2)
MUTATION_PROB = 0.05


# Generacja populacji - start + losowa litera z alfabetu binarnego
# Ocena: ilość, która znajduję się również w spektrum


# Klasa przechowująca populacje
class ThePopulation:
    wholePopulation = []

    def add_to_population(self, unit):
        self.wholePopulation.append(unit)


# Klasa osobnika zawierająca sekwencje w alfabecie [S,W] oraz w alfabecie [R, Y]
class Unit:
    def __init__(self, swSeq, rySeq):
        self.swSeq = swSeq
        self.rySeq = rySeq
        self.fitness = 0
        self.superFitness = 0
        self.swUsed = []
        self.ryUsed = []

    def calculate_fitness(self, length, oneOligonLength, swSpectrum, rySpectrum):
        for inxFrom in range(length - oneOligonLength):
            swTry = self.swSeq[inxFrom:oneOligonLength]
            ryTry = self.rySeq[inxFrom:oneOligonLength]
            if swTry not in self.swUsed and swTry in swSpectrum:
                self.fitness += 1
                self.swUsed.append(swTry)
                if ryTry not in self.ryUsed and ryTry in rySpectrum:
                    self.superFitness += 1
            if ryTry not in self.ryUsed and ryTry in rySpectrum:
                self.fitness += 1
                self.ryUsed.append(ryTry)

    def __str__(self):
        return f"{self.swSeq}\n{self.rySeq}\nFitness: {self.fitness}"


# Zmiana startowej sekwencji na odpowiadającą w danym alfabecie
def translate_start(startOligon):
    swStart = startOligon.replace('A', 'W').replace('C', 'S').replace('G', 'S').replace('T', 'W')
    ryStart = startOligon.replace('A', 'R').replace('C', 'Y').replace('G', 'R').replace('T', 'Y')
    return swStart, ryStart


def change_last_nuc_in_sw(swSpectrum):
    swChanged = []
    for oligon in swSpectrum:
        s = oligon[:-1]
        if oligon[-1] in ['C', 'G']:
            s += 'S'
        else:
            s += 'W'
        swChanged.append(s)
    return swChanged


def change_last_nuc_in_ry(rySpectrum):
    ryChanged = []
    for oligon in rySpectrum:
        s = oligon[:-1]
        if oligon[-1] in ['A', 'G']:
            s += 'R'
        else:
            s += 'Y'
        ryChanged.append(s)
    return ryChanged


# Generowanie początkowej populacji
def generate_population(swStart, ryStart, length, sizeOfPopulation):
    pop = ThePopulation()

    for i in range(sizeOfPopulation):
        swSeq = swStart
        for _ in range(length - len(swStart)):
            swSeq += random.choice(['S', 'W'])

        rySeq = ryStart
        for _ in range(length - len(ryStart)):
            rySeq += random.choice(['R', 'Y'])

        newUnit = Unit(swSeq, rySeq)
        pop.add_to_population(newUnit)

    return pop


# Wywołanie funkcji oceny dla każdego osobnika
def calculate_fitness(pop, length, oneOligonLength, swSpectrum, rySpectrum):
    for unit in pop.wholePopulation:
        unit.calculate_fitness(length, oneOligonLength, swSpectrum, rySpectrum)


# Wybór najlepiej ocenionych osobników
def select_best_units(pop, howMany):
    selected_units = sorted(pop.wholePopulation, key=lambda x:x.fitness, reverse=True)
    return selected_units[:howMany]


# TODO: Krzyżowanie najlepszych osobników
def crossover_of_best_units(unit_1, unit_2):
    pass


# TODO: Mutacja osobnika
def mutation_of_units(unit):
    pass


# TODO: Kolejne iteracje algorytmu genetycznego
def genetic_algorithm():
    pass


# Start algorytmu genetycznego
def start_genetic_algorithm(startOligon, length, swSpectrum, rySpectrum):
    swStart, ryStart = translate_start(startOligon)
    swChanged = change_last_nuc_in_sw(swSpectrum)
    ryChanged = change_last_nuc_in_ry(rySpectrum)
    pop = generate_population(swStart, ryStart, length, POPULATION)
    calculate_fitness(pop, length, len(swSpectrum[0]), swChanged, ryChanged)
    bestUnits = select_best_units(pop, SELECTION)
    for i in bestUnits:
        print(i)

    a = random.randint(0, len(bestUnits))
    b = random.randint(0, len(bestUnits))
    while b == a and len(bestUnits) != 1:
        b = random.randint(0, len(bestUnits))

    crossover_of_best_units(bestUnits[a], bestUnits[b])


def main():
    # Zabawa z plikiem xml
    tree = ET.parse('example.xml')
    root = tree.getroot()
    key = root.attrib['key']
    length = int(root.attrib['length'])
    startOligon = root.attrib['start']
    print(f"Key: {key}\nLength: {length}\nStart: {startOligon}")

    swSpectrum = []
    rySpectrum = []

    for probe in root.iter('probe'):
        if probe.attrib['pattern'][0] == 'Z':
            for cell in probe.iter('cell'):
                swSpectrum.append(cell.text)
        if probe.attrib['pattern'][0] == 'P':
            for cell in probe.iter('cell'):
                rySpectrum.append(cell.text)
    # --------------------------------------------------------------------------

    start_genetic_algorithm(startOligon, length, swSpectrum, rySpectrum)


if __name__ == '__main__':
    main()
