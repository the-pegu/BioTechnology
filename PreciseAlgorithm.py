import xml.etree.ElementTree as ET


def main():
    tree = ET.parse('bio.xml')
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

if __name__ == '__main__':
    main()