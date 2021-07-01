import xml.etree.ElementTree as ET
import random
import time

POPULATION = 250
SELECTION = int(POPULATION * 0.05)
MUTATION_PROB = 0.25
GENERATIONS_TO_STOP = 25000


# Klasa przechowująca populacje
class ThePopulation:
    def __init__(self):
        self.wholePopulation = []

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

        self.fitness = (lenOfSeqSW + lenOfSeqRY) / 2 - length


class Oligon:
    def __init__(self, seq):
        self.seq = seq

    def __str__(self):
        return self.seq


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
    return swStart, ryStart


# Generowanie początkowej populacji
def generate_population(swStart, ryStart, swSpectrum, rySpectrum, numberOfOligons, sizeOfPopulation):
    pop = ThePopulation()
    swInx = 0
    ryInx = 0
    for k in range(len(swSpectrum)):
        if swSpectrum[k].seq == swStart:
            swInx = k
            break
    for k in range(len(rySpectrum)):
        if rySpectrum[k].seq == ryStart:
            ryInx = k
            break

    for i in range(sizeOfPopulation):
        swNotUsed = swSpectrum.copy()
        swNUlength = len(swNotUsed) - 1
        ryNotUsed = rySpectrum.copy()
        ryNUlength = len(ryNotUsed) - 1

        swSeq = [swSpectrum[swInx]]
        swNotUsed.remove(swSpectrum[swInx])
        rySeq = [rySpectrum[ryInx]]
        ryNotUsed.remove(rySpectrum[ryInx])

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


# Krzyżowanie najlepszych osobników
def crossover_of_best_units(unit_1, unit_2, numberToCreate, swSpectrum, rySpectrum):
    swSeqNew = [unit_1.swSeq[0]]
    rySeqNew = [unit_1.rySeq[0]]
    swNotUsed = swSpectrum.copy()
    ryNotUsed = rySpectrum.copy()

    swNotUsed.remove(unit_1.swSeq[0])
    ryNotUsed.remove(unit_1.rySeq[0])

    for i in range(1, numberToCreate):
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
            safety = 0
            while notAdded and safety < 10:
                sU = random.choice([unit_1, unit_2])
                sx = random.choice(sU.swNotUsed)
                safety += 1
                if sx in swNotUsed:
                    swSeqNew.append(sx)
                    swNotUsed.remove(sx)
                    notAdded = False
            if notAdded:
                sx = random.choice(swNotUsed)
                swSeqNew.append(sx)
                swNotUsed.remove(sx)

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
            safety = 0
            while notAdded and safety < 10:
                rU = random.choice([unit_1, unit_2])
                rx = random.choice(rU.ryNotUsed)
                safety += 1
                if rx in ryNotUsed:
                    rySeqNew.append(rx)
                    ryNotUsed.remove(rx)
                    notAdded = False
            if notAdded:
                rx = random.choice(ryNotUsed)
                rySeqNew.append(rx)
                ryNotUsed.remove(rx)

    return Unit(swSeqNew, rySeqNew, swNotUsed, ryNotUsed)


# Mutacja osobnika
def mutation_of_unit(unitToMutate, oligonLength):
    worstSWInx = 1
    worstRYInx = 1
    worstSWFit = oligonLength*2
    worstRYFit = oligonLength*2
    x = random.randint(0, 100)
    if x < 25:
        for i in range(1, len(unitToMutate.swSeq)):
            swFit = count_how_many_fits(unitToMutate.swSeq[i-1].seq, unitToMutate.swSeq[i].seq)
            ryFit = count_how_many_fits(unitToMutate.rySeq[i-1].seq, unitToMutate.rySeq[i].seq)
            if swFit < worstSWFit:
                worstSWInx = i
                worstSWFit = swFit
            if ryFit < worstRYFit:
                worstRYInx = i
                worstRYFit = ryFit
    elif x < 75:
        worstSWInx = random.randrange(1, oligonLength)
        worstRYInx = random.randrange(1, oligonLength)

    if x < 75:
        unitToMutate.swNotUsed.append(unitToMutate.swSeq[worstSWInx])
        s = random.choice(unitToMutate.swNotUsed)
        unitToMutate.swNotUsed.remove(s)
        unitToMutate.swSeq[worstSWInx] = s

        unitToMutate.ryNotUsed.append(unitToMutate.rySeq[worstRYInx])
        r = random.choice(unitToMutate.ryNotUsed)
        unitToMutate.ryNotUsed.remove(r)
        unitToMutate.rySeq[worstRYInx] = r
    else:
        swInx1 = random.randrange(1, oligonLength)
        swInx2 = random.randrange(1, oligonLength)

        temp = unitToMutate.swSeq[swInx1]
        unitToMutate.swSeq[swInx1] = unitToMutate.swSeq[swInx2]
        unitToMutate.swSeq[swInx2] = temp

        ryInx1 = random.randrange(1, oligonLength)
        ryInx2 = random.randrange(1, oligonLength)

        temp = unitToMutate.rySeq[ryInx1]
        unitToMutate.rySeq[ryInx1] = unitToMutate.rySeq[ryInx2]
        unitToMutate.rySeq[ryInx2] = temp


# Generowanie nowej populacji z najlepiej ocenionych osobników z wykorzystaniem krzyżowania i mutacji
def generate_new_population_from_the_best(bestUnits, numberToCreate, oligonLength, swSpectrum, rySpectrum, sizeOfPopulation):
    pop = ThePopulation()
    for i in range(sizeOfPopulation):
        a = random.choice(bestUnits)
        b = random.choice(bestUnits)
        while b == a:
            b = random.choice(bestUnits)
        newUnit = crossover_of_best_units(a, b, numberToCreate, swSpectrum, rySpectrum)

        if random.randrange(101) / 100 < MUTATION_PROB:
            mutation_of_unit(newUnit, oligonLength)
        pop.add_to_population(newUnit)
    return pop


# Zwróci Nukleotyd z alfabetu {A, C, G, T} w oparciu o złożenie dwóch liter z alfabetu {S, W} oraz {R, Y}
def return_nucleotide(sw, ry):
    if sw == 'W' and ry == 'R':
        return 'A'
    elif sw == 'S' and ry == 'Y':
        return 'C'
    elif sw == 'S' and ry == 'R':
        return 'G'
    else:
        return 'T'


# Buduje znalezione rozwiązanie korzystając z alfabetu {A, C, G, T}
def construct_result(swSeq, rySeq):
    print(f"swLength: {len(swSeq)}  |  ryLength: {len(rySeq)}")
    result = ""
    for i in range(len(swSeq)):
        result += return_nucleotide(swSeq[i], rySeq[i])
    return result


# Sprawdza znalezione rozwiązanie
def check_if_found_solution(unit, length, oligonLength):
    sw = ""
    ry = ""
    for i, swOligon in enumerate(unit.swSeq):
        if i == 0:
            sw += swOligon.seq[:]
        else:
            howManyFits = count_how_many_fits(unit.swSeq[i - 1].seq, swOligon.seq)
            sw += swOligon.seq[-(oligonLength-howManyFits):]

    for i, ryOligon in enumerate(unit.rySeq):
        if i == 0:
            ry += ryOligon.seq[:]
        else:
            howManyFits = count_how_many_fits(unit.rySeq[i-1].seq, ryOligon.seq)
            ry += ryOligon.seq[-(oligonLength-howManyFits):]

    return construct_result(sw, ry)


# Przelosowanie kolejności oligonukleotydów, gdy zbyt długi czas nie zmienia się najlepszy wynik w populacji
def little_schuffle(pop, numberToCreate, oligonLength):
    for unit in pop.wholePopulation:
        whichOne = random.choice(['SW', 'RY'])
        typeOfSchuffle = random.choice(['SWAP', 'EXCHANGE'])
        for i in range(numberToCreate-1):
            o1 = random.randrange(1, int(oligonLength/2))
            o2 = random.randrange(int(oligonLength/2), oligonLength)
            if whichOne == 'SW' and len(unit.swNotUsed) == 0:
                typeOfSchuffle = 'SWAP'
            if whichOne == 'RY' and len(unit.ryNotUsed) == 0:
                typeOfSchuffle = 'SWAP'

            if whichOne == 'SW' and typeOfSchuffle == 'SWAP':
                temp1 = unit.swSeq[o1]
                unit.swSeq[o1] = unit.swSeq[o2]
                unit.swSeq[o2] = temp1
            elif whichOne == 'RY' and typeOfSchuffle == 'SWAP':
                temp2 = unit.rySeq[o1]
                unit.rySeq[o1] = unit.rySeq[o2]
                unit.rySeq[o2] = temp2
            elif whichOne == 'SW' and typeOfSchuffle == 'EXCHANGE':
                s = random.choice(unit.swNotUsed)
                unit.swNotUsed.append(unit.swSeq[o1])
                unit.swNotUsed.remove(s)
                unit.swSeq[o1] = s
            else:
                r = random.choice(unit.ryNotUsed)
                unit.ryNotUsed.append(unit.rySeq[o1])
                unit.ryNotUsed.remove(r)
                unit.rySeq[o1] = r
            q = unit.fitness
    return pop


# Rozpoczyna algorytm genetyczny w celu znalezienia sekwencji DNA o podanej długości
def start_genetic_algorithm(start, length, oligonLength, swSpectrum, rySpectrum):
    numberToCreate = length - oligonLength + 1
    swStart, ryStart = translate_start(start)
    pop = generate_population(swStart, ryStart, swSpectrum, rySpectrum, numberToCreate, POPULATION)
    gen = 1
    genBestFitness = length * length
    absolutelyTheBest = length * length
    turnsWithoutChange = 0
    turnsWithoutChange2 = 0
    while gen <= GENERATIONS_TO_STOP:
        changed = False
        changed2 = False
        calculate_fitness_for_population(pop, length, oligonLength)
        bestUnits = select_best_units(pop, SELECTION)
        print(f"Generation: {gen} Best Units:", end="")
        for i in bestUnits:
            print(f" {i.fitness}", end="")
            if i.fitness < genBestFitness:
                if i.fitness < absolutelyTheBest:
                    absolutelyTheBest = i.fitness
                    changed2 = True
                genBestFitness = i.fitness
                changed = True
            if i.fitness <= 0:
                solution = check_if_found_solution(i, length, oligonLength)
                print("Found Solution!")
                print(solution)
                return
        if changed:
            turnsWithoutChange = 0
        else:
            turnsWithoutChange += 1
        if changed2:
            turnsWithoutChange2 = 0
        else:
            turnsWithoutChange2 += 1
        print(f"   -----   Turns without change: {turnsWithoutChange}  2: {turnsWithoutChange2}  - The Best: {absolutelyTheBest}")
        if turnsWithoutChange >= 300:
            pop = little_schuffle(pop, numberToCreate, oligonLength)
            genBestFitness = length * length
            turnsWithoutChange = 0
        elif turnsWithoutChange2 >= 1600:
            pop = generate_population(swStart, ryStart, swSpectrum, rySpectrum, numberToCreate, POPULATION)
            genBestFitness = length * length
            turnsWithoutChange2 = 0
        else:
            pop = generate_new_population_from_the_best(bestUnits, numberToCreate, oligonLength, swSpectrum, rySpectrum, POPULATION)
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
    print("Number of Oligons for perfect solutions: ", length - len(swSpectrum[0]) + 1)

    swOligons = change_last_nuc_in_sw(swSpectrum)
    ryOligons = change_last_nuc_in_ry(rySpectrum)

    start_genetic_algorithm(startOligon, length, len(swSpectrum[0]), swOligons, ryOligons)


if __name__ == '__main__':
    main()
