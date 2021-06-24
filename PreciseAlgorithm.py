import xml.etree.ElementTree as ET


class Graph:
    def __init__(self, typ):
        self.gType = typ
        self.vertices = []


class Vertex:
    def __init__(self, ind, cell):
        self.index = ind
        self.lastNuc = cell[-1]
        self.vType = self.check_type(cell)
        self.label = self.replace_last_nuc(cell)
        self.successors = []

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


def if_fits(oligonA, oligonB):
    if oligonA[1:] != oligonB[:-1]:
        return False
    else:
        return True


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


def main():
    tree = ET.parse('example.xml')
    root = tree.getroot()
    key = root.attrib['key']
    length = root.attrib['length']
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

    # print(swSpectrum)
    # print(rySpectrum)
    print("\n")
    swGraph = make_graph(swSpectrum, 'SW')

    for i in swGraph.vertices:
        print(i)


if __name__ == '__main__':
    main()
