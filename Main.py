from BKMap import BKMap

def main(filename):
    #import treasure_map
    Map = BKMap(filename)

if __name__ == '__main__':
    filename = input('Enter a filename: ')
    main(filename)