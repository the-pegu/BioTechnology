import xml.etree.ElementTree as ET


class Vertex:

    label = ""
    lastNuc = ""
    type = ""
    successors = []

    def __init__(self, cell):
        self.lastNuc = cell[-1]
        self.check_type(cell)
        self.label = self.replace_last_nuc(cell)

    def check_type(self, cell):
        if cell[0] in ['S', 'W']:
            self.type = 'SW'
        else:
            self.type = 'RY'

    def replace_last_nuc(self, cell):
        if self.type == 'SW':
            if self.lastNuc in ['C', 'G']:
                return cell[:-1] + 'S'
            else:
                return cell[:-1] + 'W'
        else:
            if self.lastNuc in ['A', 'G']:
                return cell[:-1] + 'R'
            else:
                return cell[:-1] + 'Y'

    def add_to_successors(self, vert):
        self.successors.append(vert)

    def __str__(self):
        return f"Type: {self.type}\nLabel: {self.label}\nLast Nuc: {self.lastNuc}"


def make_graph(spectrum):
    a = Vertex(spectrum[0])
    print(a)


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

    print(swSpectrum)
    print(rySpectrum)

    make_graph(swSpectrum)


if __name__ == '__main__':
    main()
