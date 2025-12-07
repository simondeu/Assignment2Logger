from BKMap import BKMap

def main(filename):
    Map = BKMap(filename)

if __name__ == '__main__':
    filename = input('Enter a filename: ')
    main(filename)