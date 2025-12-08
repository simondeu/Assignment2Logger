import time


def Log(pos, filename):
    print(f'{filename}: logtext.sample for {pos[0]}, {pos[1]}')
    time.sleep(1)

class Logger():
    def __init__(self, fileName):
        self.fileName = fileName

    def startLog(self):
        with open(self.fileName, 'w') as f:
            f.write('''8-12-2025 14:18:33\t"MAC Address"\t"Vendor"\t"SSID"\t"Access Point Name"\t"Connected AP"\t"Signal Strength"\t"Quality"\t"Station Count"\t"Frequency"\t"Position"\t"Info"\t"Adapter"''')
    
    def endLog(self):
        with open(self.fileName) as f:
            self.lines = f.readlines()
    
    def getLogs(self):
        return self.lines