import xml.etree.ElementTree as ET


# Klasa grafu, która dla ułatwienia przechowuje tylko wszystkie wierzchołki z danego spektrum
class Graph:
    def __init__(self, typ):
        self.gType = typ
        self.vertices = []


# Klasa wierzchołka w grafie
class Vertex:
    def __init__(self, ind, cell):
        self.index = ind
        self.lastNuc = cell[-1]
        self.vType = self.check_type(cell)
        self.label = self.replace_last_nuc(cell)
        self.successors = []
        self.visited = False

    def check_type(self, cell):
        if cell[0] in ['S', 'W']:
            return 'SW'
        else:
            return 'RY'

    def replace_last_nuc(self, cell):
        if self.vType == 'SW':
            if self.lastNuc in ['C', 'G']:
                return cell[:-1] + 'S'
            else:
                return cell[:-1] + 'W'
        else:
            if self.lastNuc in ['A', 'G']:
                return cell[:-1] + 'R'
            else:
                return cell[:-1] + 'Y'

    def __str__(self):
        return f"Type: {self.vType}\nLabel: {self.label}\nLast Nuc: {self.lastNuc}\nSuccessors: {self.successors}\n"


# Sprawdzenie czy pomiędzy dwoma oligonukleotydami jest maksymalne nałożenie
def if_fits(oligonA, oligonB):
    if oligonA[1:] != oligonB[:-1]:
        return False
    else:
        return True


# Stworzenie grafu z danego spektrum oraz znalezienie następników dla każdego wierzchołka
def make_graph(spectrum, gType):
    graph = Graph(gType)
    for ind, cell in enumerate(spectrum):
        v = Vertex(ind, cell)
        graph.vertices.append(v)

    for i, vertA in enumerate(graph.vertices):
        for j, vertB in enumerate(graph.vertices):
            if i != j and if_fits(vertA.label, vertB.label):
                graph.vertices[i].successors.append(vertB)

    return graph


# Zmiana startowego oligonukleotydu z alfabetu {A,C,G,T} na dwa binarne: {S, W} i {R, Y}
def change_start_for_both_spectrum(start):
    swStart = start.replace('A', 'W').replace('C', 'S').replace('G', 'S').replace('T', 'W')
    ryStart = start.replace('A', 'R').replace('C', 'Y').replace('G', 'R').replace('T', 'Y')
    return swStart, ryStart


# Przeszukiwanie grafów w celu znalezienia oligonukleotydu startowego w obu ze spektrum
def find_first_vertices(swStart, swGraph, ryStart, ryGraph):
    swVertex = None
    ryVertex = None
    for swV in swGraph.vertices:
        if swV.label == swStart:
            swVertex = swV
    for ryV in ryGraph.vertices:
        if ryV.label == ryStart:
            ryVertex = ryV
    return swVertex, ryVertex


# Sprawdzenie czy któraś para się nadaje jako następnicy w ścieżce
def find_candidates(swVertex, ryVertex):
    candidates = []
    for swNext in swVertex.successors:
        for ryNext in ryVertex.successors:
            if swNext.lastNuc == ryNext.lastNuc:
                candidates.append([swNext, ryNext])
    return candidates


# Wybór pierwszej pary z listy kandydatów.
# TODO: Będzie potrzebna zmiana jak będzie już wywoływanie powrotów, żeby wybrać np. kolejną parę
def add_first_candidates(candidates):
    if len(candidates) > 0:
        swVertex = candidates[0][0]
        ryVertex = candidates[0][1]
        return swVertex, ryVertex
    else:
        return None, None


# Przeszukiwanie grafów równocześnie, w celu znalezienia poszukiwanej ścieżki
# TODO: Wywoływanie powrotów, sprawdzenie czy to działa i ewentualna poprawa
def find_path(swGraph, ryGraph, start, lengthToFind):
    swStart, ryStart = change_start_for_both_spectrum(start)
    swVertex, ryVertex = find_first_vertices(swStart, swGraph, ryStart, ryGraph)
    path = [[swVertex, ryVertex]]
    length = len(start)
    while length < lengthToFind:
        candidates = find_candidates(swVertex, ryVertex)
        swVertex, ryVertex = add_first_candidates(candidates)
        if swVertex is not None and ryVertex is not None:
            path.append([swVertex, ryVertex])
        else:
            break
    return path


# Na razie nie jest to potrzebne i może wcale nie być, ale niech będzie
def choose_nuc(sORw, rORy):
    if sORw == 'S' and rORy == 'R':
        return 'G'
    elif sORw == 'S' and rORy == 'Y':
        return 'C'
    elif sORw == 'W' and rORy == 'R':
        return 'A'
    elif sORw == 'W' and rORy == 'Y':
        return 'T'
    else:
        return 'whatthefuck'


# Konstrukcja ścieżki, dla uzyskania wyniku w postaci sekwencji DNA nad alfabetem {A,C,G,T}
def construct_result(path, start):
    result = start
    for i, nuc in enumerate(path):
        if i == 0:
            continue
        result += nuc[0].lastNuc
    return result


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
    # Tworzenie grafu. Tylko po to by gdzieś przechować wszystkie wierzchołki
    swGraph = make_graph(swSpectrum, 'SW')
    ryGraph = make_graph(rySpectrum, 'RY')

    # Szukanie ścieżki w obu grafach równocześnie
    path = find_path(swGraph, ryGraph, startOligon, length)
    print(path)

    # Stworzenie wyniku by można było go ładnie wyprintować
    result = construct_result(path, startOligon)
    print(result)
    print(len(result))


if __name__ == '__main__':
    main()
