import xml.etree.ElementTree as ET
import random
import time

POPULATION = 2
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

    def __str__(self):
        return f"{self.swSeq}\n{self.rySeq}\n"


# Zmiana startowej sekwencji na odpowiadającą w danym alfabecie
def translate_start(startOligon):
    swStart = startOligon.replace('A', 'W').replace('C', 'S').replace('G', 'S').replace('T', 'W')
    ryStart = startOligon.replace('A', 'R').replace('C', 'Y').replace('G', 'R').replace('T', 'Y')
    return swStart, ryStart


# Generowanie początkowej populacji
def generate_population(swStart, ryStart, length):
    pop = ThePopulation()

    for i in range(POPULATION):
        swSeq = swStart
        for _ in range(length - len(swStart)):
            swSeq += random.choice(['S', 'W'])

        rySeq = ryStart
        for _ in range(length - len(ryStart)):
            rySeq += random.choice(['R', 'Y'])

        newUnit = Unit(swSeq, rySeq)
        print(newUnit)
        pop.add_to_population(newUnit)

    return pop


def start_genetic_algorithm(startOligon, length, swSpectrum, rySpectrum):
    swStart, ryStart = translate_start(startOligon)
    population = generate_population(swStart, ryStart, length)


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
