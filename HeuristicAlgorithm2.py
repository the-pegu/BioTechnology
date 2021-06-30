import xml.etree.ElementTree as ET
import random
import time

POPULATION = 20
SELECTION = int(POPULATION * 0.2)
MUTATION_PROB = 0.3


# Klasa przechowująca populacje
class ThePopulation:
    wholePopulation = []

    def add_to_population(self, unit):
        self.wholePopulation.append(unit)


# Klasa osobnika zawierająca sekwencje w alfabecie [S,W] oraz w alfabecie [R, Y]
class Unit:
    def __init__(self, swSeq, rySeq, swNotUsed=[], ryNotUsed=[]):
        self.swSeq = swSeq
        self.rySeq = rySeq
        self.fitness = 0
        self.swNotUsed = swNotUsed
        self.ryNotUsed = ryNotUsed

    def calculate_fitness(self, length, oligonLength):
        lenOfSeqSW = 0
        for i, oligon in enumerate(self.swSeq):
            if i == 0:
                lenOfSeqSW += oligonLength
            else:
                howManyFits = count_how_many_fits(self.swSeq[i-1].seq, oligon.seq)
                lenOfSeqSW += oligonLength - howManyFits

        lenOfSeqRY = 0
        for i, oligon in enumerate(self.rySeq):
            if i == 0:
                lenOfSeqRY += oligonLength
            else:
                howManyFits = count_how_many_fits(self.rySeq[i - 1].seq, oligon.seq)
                lenOfSeqRY += oligonLength - howManyFits

        self.fitness = (lenOfSeqSW + lenOfSeqRY) / 2  # TODO - length


class Oligon:
    def __init__(self, seq):
        self.seq = seq

    # def __str__(self):
    #     return self.seq


# Zamiana ostatnich liter w spektrum SW
def change_last_nuc_in_sw(swSpectrum):
    swChanged = []
    for oligon in swSpectrum:
        s = oligon[:-1]
        if oligon[-1] in ['C', 'G']:
            s += 'S'
        else:
            s += 'W'
        swChanged.append(Oligon(s))
    return swChanged


# Zamiana ostatnich liter w spektrum RY
def change_last_nuc_in_ry(rySpectrum):
    ryChanged = []
    for oligon in rySpectrum:
        s = oligon[:-1]
        if oligon[-1] in ['A', 'G']:
            s += 'R'
        else:
            s += 'Y'
        ryChanged.append(Oligon(s))
    return ryChanged


# Zmiana startowej sekwencji na odpowiadającą w danym alfabecie
def translate_start(startOligon):
    swStart = startOligon.replace('A', 'W').replace('C', 'S').replace('G', 'S').replace('T', 'W')
    ryStart = startOligon.replace('A', 'R').replace('C', 'Y').replace('G', 'R').replace('T', 'Y')
    return Oligon(swStart), Oligon(ryStart)


# Generowanie początkowej populacji
def generate_population(swStart, ryStart, swSpectrum, rySpectrum, numberOfOligons, sizeOfPopulation):
    pop = ThePopulation()
    swInx = 0
    ryInx = 0
    for k in range(len(swSpectrum)):
        if swSpectrum[k].seq == swStart.seq:
            swInx = k
            break
    for k in range(len(rySpectrum)):
        if rySpectrum[k].seq == ryStart.seq:
            ryInx = k
            break

    for i in range(sizeOfPopulation):
        swNotUsed = swSpectrum.copy()
        swNUlength = len(swNotUsed) - 1
        ryNotUsed = rySpectrum.copy()
        ryNUlength = len(ryNotUsed) - 1

        swSeq = [swStart]
        swNotUsed.remove(swNotUsed[swInx])
        rySeq = [ryStart]
        ryNotUsed.remove(ryNotUsed[ryInx])

        for j in range(numberOfOligons-1):
            x1 = random.randrange(0, swNUlength)
            swSeq.append(swNotUsed[x1])
            swNotUsed.remove(swNotUsed[x1])
            swNUlength -= 1

            x2 = random.randrange(0, ryNUlength)
            rySeq.append(ryNotUsed[x2])
            ryNotUsed.remove(ryNotUsed[x2])
            ryNUlength -= 1

        newUnit = Unit(swSeq, rySeq, swNotUsed, ryNotUsed)
        pop.add_to_population(newUnit)

    return pop


# Wyliczanie stopnia nałozenia się 2 oligonukleotydów
def count_how_many_fits(oligon_1, oligon_2):
    counter = len(oligon_1)-1
    for i in range(0, len(oligon_1)):
        if oligon_1[1+i:] != oligon_2[:-1-i]:
            counter -= 1
        else:
            break
    return counter


# Wywołanie funkcji oceny dla każdego osobnika
def calculate_fitness_for_population(pop, length, oligonLength):
    for unit in pop.wholePopulation:
        unit.calculate_fitness(length, oligonLength)


# Wybór najlepiej ocenionych osobników
def select_best_units(pop, howMany):
    selected_units = sorted(pop.wholePopulation, key=lambda x: x.fitness)
    return selected_units[:howMany]


# Znajdź indeks w tablicy, jeśli taki element się znajduję
def check_if_in_array(seq, array):
    for i in range(len(array)):
        if array[i].seq == seq:
            return i
    return None


# Krzyżowanie najlepszych osobników
def crossover_of_best_units(unit_1, unit_2, oligonLength, length, swSpectrum, rySpectrum):
    swSeqNew = [unit_1.swSeq[0]]
    rySeqNew = [unit_1.rySeq[0]]
    swNotUsed = swSpectrum.copy()
    ryNotUsed = rySpectrum.copy()

    swInx = check_if_in_array(unit_1.swSeq[0], swNotUsed)
    ryInx = check_if_in_array(unit_1.rySeq[0], ryNotUsed)
    if swInx is not None:
        swNotUsed.remove(swNotUsed[swInx])
    if ryInx is not None:
        ryNotUsed.remove(ryNotUsed[ryInx])

    for i in range(1, length - oligonLength - 1):
        if unit_1.swSeq[i] in swNotUsed and unit_2.swSeq[i] in swNotUsed:
            swU1Fit = count_how_many_fits(swSeqNew[i - 1].seq, unit_1.swSeq[i].seq)
            swU2Fit = count_how_many_fits(swSeqNew[i - 1].seq, unit_2.swSeq[i].seq)
            if swU1Fit >= swU2Fit:
                swSeqNew.append(unit_1.swSeq[i])
                swNotUsed.remove(unit_1.swSeq[i])
            else:
                swSeqNew.append(unit_2.swSeq[i])
                swNotUsed.remove(unit_2.swSeq[i])
        elif unit_1.swSeq[i] not in swNotUsed and unit_2.swSeq[i] in swNotUsed:
            swSeqNew.append(unit_2.swSeq[i])
            swNotUsed.remove(unit_2.swSeq[i])
        elif unit_1.swSeq[i] in swNotUsed and unit_2.swSeq[i] not in swNotUsed:
            swSeqNew.append(unit_1.swSeq[i])
            swNotUsed.remove(unit_1.swSeq[i])
        else:
            notAdded = True
            while notAdded:
                sx = random.choice(unit_1.swNotUsed)
                sInx = check_if_in_array(sx.seq, swNotUsed)
                if sInx is not None:
                    swSeqNew.append(sx)
                    swNotUsed.remove(sx)
                    notAdded = False

        if unit_1.rySeq[i] in ryNotUsed and unit_2.rySeq[i] in ryNotUsed:
            ryU1Fit = count_how_many_fits(rySeqNew[i - 1].seq, unit_1.rySeq[i].seq)
            ryU2Fit = count_how_many_fits(rySeqNew[i - 1].seq, unit_2.rySeq[i].seq)
            if ryU1Fit >= ryU2Fit:
                rySeqNew.append(unit_1.rySeq[i])
                ryNotUsed.remove(unit_1.rySeq[i])
            else:
                rySeqNew.append(unit_2.rySeq[i])
                ryNotUsed.remove(unit_2.rySeq[i])
        elif unit_1.rySeq[i] not in ryNotUsed and unit_2.rySeq[i] in ryNotUsed:
            rySeqNew.append(unit_2.rySeq[i])
            ryNotUsed.remove(unit_2.rySeq[i])
        elif unit_1.rySeq[i] in ryNotUsed and unit_2.rySeq[i] not in ryNotUsed:
            rySeqNew.append(unit_1.rySeq[i])
            ryNotUsed.remove(unit_1.rySeq[i])
        else:
            notAdded = True
            while notAdded:
                rx = random.choice(unit_1.ryNotUsed)
                rInx = check_if_in_array(rx.seq, ryNotUsed)
                if rInx is not None:
                    rySeqNew.append(rx)
                    ryNotUsed.remove(rx)
                    notAdded = False

    return Unit(swSeqNew, rySeqNew, swNotUsed, ryNotUsed)


# Mutacja osobnika
def mutation_of_unit(unitToMutate):
    worstSWInx = 1
    worstRYInx = 1
    worstSWFit = 19
    worstRYFit = 19
    for i in range(1, len(unitToMutate.swSeq)):
        swFit = count_how_many_fits(unitToMutate.swSeq[i-1].seq, unitToMutate.swSeq[i].seq)
        ryFit = count_how_many_fits(unitToMutate.rySeq[i-1].seq, unitToMutate.rySeq[i].seq)
        if swFit < worstSWFit:
            worstSWInx = i
            worstSWFit = swFit
        if ryFit < worstRYFit:
            worstRYInx = i
            worstRYFit = ryFit

    unitToMutate.swNotUsed.append(unitToMutate.swSeq[worstSWInx])
    s = random.choice(unitToMutate.swNotUsed)
    unitToMutate.swNotUsed.remove(s)
    unitToMutate.swSeq[worstSWInx] = s

    unitToMutate.ryNotUsed.append(unitToMutate.rySeq[worstRYInx])
    r = random.choice(unitToMutate.ryNotUsed)
    unitToMutate.ryNotUsed.remove(r)
    unitToMutate.rySeq[worstRYInx] = r


# Generowanie nowej populacji z najlepiej ocenionych osobników z wykorzystaniem krzyżowania i mutacji
def generate_new_population_from_the_best(bestUnits, length, oligonLength, swSpectrum, rySpectrum, sizeOfPopulation):
    pop = ThePopulation()
    for i in range(sizeOfPopulation):
        a = random.choice(bestUnits)
        b = random.choice(bestUnits)
        while b == a:
            b = random.choice(bestUnits)
        newUnit = crossover_of_best_units(a, b, oligonLength, length, swSpectrum, rySpectrum)

        if random.randrange(101) / 100 < MUTATION_PROB:
            mutation_of_unit(newUnit)
        pop.add_to_population(newUnit)

    return pop


def start_genetic_algorithm(start, length, oligonLength, swSpectrum, rySpectrum):
    numberToCreate = length - oligonLength
    swStart, ryStart = translate_start(start)
    pop = generate_population(swStart, ryStart, swSpectrum, rySpectrum, numberToCreate, POPULATION)
    gen = 1
    while True:
        calculate_fitness_for_population(pop, length, oligonLength)
        bestUnits = select_best_units(pop, SELECTION)
        print(f"Generation: {gen} Best Units:", end="")
        for i in bestUnits:
            print(f" {i.fitness}", end="")
        print("")
        pop = generate_new_population_from_the_best(bestUnits, length, oligonLength, swSpectrum, rySpectrum, POPULATION)
        gen += 1


def main():
    # Zabawa z plikiem xml
    tree = ET.parse('example2.xml')
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
    print("Length of one oligon: ", len(swSpectrum[0]))
    print("Length of SW Spectrum: ", len(swSpectrum))
    print("Length of RY Spectrum: ", len(rySpectrum))
    print("Number of Oligons for perfect solutions: ", length - len(swSpectrum[0]))

    swOligons = change_last_nuc_in_sw(swSpectrum)
    ryOligons = change_last_nuc_in_ry(rySpectrum)

    start_genetic_algorithm(startOligon, length, len(swSpectrum[0]), swOligons, ryOligons)


if __name__ == '__main__':
    main()
