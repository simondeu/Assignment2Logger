from tkinter import Canvas, Tk

import numpy as np
import rasterio
from matplotlib import cm
from PIL import Image, ImageTk
from Logger import Logger
import time
from Log_to_csv_mvp import log_to_csv

import csv
from collections import defaultdict
from statistics import mean
import math  # Needed for Euclidean distance (square root)


class BKMap(Tk):

    def __init__(self, filename):
        Tk.__init__(self)
        self.interface()
        self.logger = Logger(filename)
        self.log = {}
        self.scores = {}
        self.points = []
        self.filename = filename
        self.title = 'Map of Bouwkunde'
        self.h = 1080
        self.w = 1920
        self.currentPos = (0, 0)
        self.resizable(0,0)
        self.bind("q", self.exit)
        self.bind("l", self.logging)
        self.bind("p", self.printLogs)
        self.bind("x", self.deletePoint)
        self.bind("d", self.dictToWNT)
        self.isLogging = False
        self.output_info()

        self.setTexts()

        self.actualPointIndex = None

        self.openImage()
        self.setCanvas()
        self.setDisplay()

        self.protocol('WM_DELETE_WINDOW', self.quitProgram)

        self.isRunning = True
        self.draw()

    def interface(self):
        print("\n" + "=" * 170)
        print("                                                                     WI-FI FINGERPRINTING")
        print("                                                                         TREASURE MAP")
        print("=" * 170)

        # =======================
        # KNOBS FOR TREASURE HUNT
        # =======================

        # MINIMUM RELIABILITY: as a fraction
        MIN_RELIABILITY_PERCENT = input("Minimum reliability percentage (default 0): ")
        if MIN_RELIABILITY_PERCENT == "":
            MIN_RELIABILITY_PERCENT = 0.00
        else:
            MIN_RELIABILITY_PERCENT = float(MIN_RELIABILITY_PERCENT) / 100.0

        # Missing-signal penalty (dBm)
        MISSING_PENALTY_RSS = input("Missing penalty RSS (default: -100): ")
        if MISSING_PENALTY_RSS == "":
            MISSING_PENALTY_RSS = -100
        else:
            MISSING_PENALTY_RSS = int(MISSING_PENALTY_RSS)

        # Scoring algorithm (M or E)
        SCORING_ALGORITHM = input("Choose scoring algorithm, (default) M=Manhattan or E=Euclidean: ")
        if SCORING_ALGORITHM == "":
            SCORING_ALGORITHM = "M"
        else:
            SCORING_ALGORITHM = SCORING_ALGORITHM.strip().upper()

        # Refreshing time
        REFRESHING_TIME = input("Refreshing time in seconds (default 2): ")
        if REFRESHING_TIME == "":
            REFRESHING_TIME = 2
        else:
            REFRESHING_TIME = float(REFRESHING_TIME)

        # Difference tolerance
        TOLL = input("Tolerance (default 3): ")
        if TOLL == "":
            TOLL = 3
        else:
            TOLL = float(TOLL)

        self.min_rel_per = MIN_RELIABILITY_PERCENT
        self.mis_pen_rss = MISSING_PENALTY_RSS
        self.scor_alg = SCORING_ALGORITHM
        self.ref_time = REFRESHING_TIME
        self.toll = TOLL

        # =========
        # LOAD DATA
        # =========

        self.target_files = {
            "Location_1" : "location_1.csv",
            "Location_2" : "location_2.csv",
            "Location_3" : "location_3.csv",
            "Location_4" : "location_4.csv",
        }


        self.test_files = {
            "Test_Location_1" : "known_locations/known_1.csv",
            "Test_Location_2" : "known_locations/known_2.csv",
            "Test_Location_3" : "known_locations/known_3.csv",
            "Test_Location_4" : "known_locations/known_4.csv"
        }

    def setDisplay(self):
        self.bind("<Motion>", self.displayCoords)
        self.bind("<ButtonRelease-1>", self.onLeftMouseClick)
        self.bind("<ButtonRelease-3>", self.onRightMouseClick)
        
    def setTexts(self):
        self.logtxt = "Not logging :("
        self.coordtxt = "0, 0"
    
    def output_info(self):
        print(
            f"=====Use=====\n\
Press on the map to add location. \n\
Press 'L' to start or stop logging\n\
Press 'Q' to quit the program \n\
Press 'P' to print logs\n\
Rightclick on point to select and 'X' to remove\n\
============= "
        )

    def setCanvas(self):
        self.canvas = Canvas(self, bg = 'white', width = self.w, height=self.h)
        self.canvas.pack()

        self.canvas.create_image(0,0,image=self.img, anchor= 'nw')
    
    def openImage(self):
        img = Image.open('BKPlan.jpg')
        self.w = img.width
        self.h = img.height
        self.img = ImageTk.PhotoImage(img)

    def displayCoords(self, event):
        if (
            (event.x > 0)
            and (event.x < self.w)
            and (event.y > 0)
            and (event.y < self.h)
        ):
            wx, wy = (event.x, event.y)
            self.coordtxt = f'{wx}, {wy}'
            self.canvas.itemconfig(self.coordstext, text=self.coordtxt)

    def onLeftMouseClick(self, event):
        self.points.append([event.x, event.y, 'red'])
        if self.isLogging:
            self.logger.endLog()
            self.log[self.currentPos] = self.logger.getLogs()
            self.logger.startLog()
        self.currentPos = (event.x, event.y)

    def onRightMouseClick(self, event):
        toleranceRadius = 6
        for i, pt in enumerate(self.points):
            if abs(pt[0] - event.x) <= toleranceRadius and abs(pt[1] - event.y) <= toleranceRadius:
                if self.actualPointIndex is not None:
                    self.points[self.actualPointIndex][2] = 'red'
                self.points[i][2] = 'green'
                self.actualPointIndex = i


    def drawPoint(self, x, y, col):
        radius = 3
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=col)

    def logging(self, event):
        if self.isLogging:
            self.isLogging = False
            self.logger.endLog()
            try:
                self.log[self.currentPos]
            except:
                self.log[self.currentPos] = self.logger.getLogs()
            else:
                self.log[self.currentPos] += self.logger.getLogs()
            self.getScores(self.currentPos)
            self.logtxt = 'Not logging :('
        else:
            self.isLogging = True
            self.logger.startLog()
            self.logtxt = 'Logging! :D'
        self.canvas.itemconfig(self.loggingText, text = self.logtxt)

    def draw(self):
        while self.isRunning:
            self.canvas.delete('all')
            self.canvas.create_image(0,0,image=self.img, anchor= 'nw')
            for pt in self.points:
                self.drawPoint(pt[0], pt[1], pt[2])
            self.coordstext = self.canvas.create_text(
                self.w, self.h, fill="black", anchor="se", text= self.coordtxt
            )
            self.loggingText = self.canvas.create_text(
                self.w//2, 0, fill="black", anchor="n", text = self.logtxt
            )
            self.canvas.update()

    def printLogs(self, event):
        for key in self.log.keys():
            print(f'{key}: {self.log[key][:5]}')

    def deletePoint(self, event):
        if self.isLogging:
            return
        del self.points[self.actualPointIndex]

        try:
            keys = list(self.log)
            key = keys[self.actualPointIndex]
            self.log.pop(key)
        except:
            print('Point had no logs')

        self.actualPointIndex = None

    def getScores(self, key):
        x,y = key[0], key[1]
        fileName = f"Live_log_{x}_{y}.txt"
        with open(fileName, 'w') as f:
            for line in self.log[key]:
                f.write(f'{line}')
        csvFile = log_to_csv(fileName, 'eduroam', key)
        self.scores[key] = self.compute_score(csvFile)
        
    def exit(self, event):
        print('Bye!')
        self.isRunning = False
        self.destroy()
        time.sleep(1)
    
    def quitProgram(self):
        print('Bye!')
        self.isRunning = False
        self.destroy()
        time.sleep(1)


    

    def process_csv_fingerprint(self, filepath):

        mac_rss_values = defaultdict(list)              # values are lists (become rss_list)
        total_rows = 0

        with open(filepath, 'r', newline='') as file:
            reader = csv.reader(file)
            # Handle potential different headers or skip first row
            header = next(reader, None)

            # quick checks
            for row in reader:
                if len(row) < 4: continue # check valid row length
                ssid = row[2].strip()
                if "eduroam" not in ssid.lower():  # check if "eduroam" is listed
                    continue
                total_rows += 1
                mac = row[1].strip()                    # collect MAC
                try:
                    rss = int(row[3].strip())           # collect RSS
                    mac_rss_values[mac].append(rss)     # (key <- mac): (value <- rss_list)
                except ValueError:
                    continue

        if total_rows == 0:
            print("   [WARNING] No valid Eduroam data found in file.")
            return None, 0, 0

        # FILTERING
        final_fingerprint = {}
        dropped_macs = 0

        for mac, rss_list in mac_rss_values.items():
            # Frequency Check: How often did this MAC appear?
            observation_count = len(rss_list)
            reliability = observation_count / total_rows    # as proportion

            if reliability >= self.min_rel_per:
                # stable signal -> Add Average RSS to fingerprint
                avg_rss = round(mean(rss_list))
                final_fingerprint[mac] = avg_rss
            else:
                # It's noise
                dropped_macs += 1

        # print(f"   [DONE] Kept {len(final_fingerprint)} stable APs. Dropped {dropped_macs} noisy signals.")
        kept_count = len(final_fingerprint)
        return final_fingerprint, kept_count, total_rows

    def score(self, target_fp, live_fp):
        final_score = 0

        if self.scor_alg == "M":    # Manhattan
            for mac, target_rss in target_fp.items():
                if mac in live_fp:
                    final_score += abs(target_rss - live_fp[mac])
                else:
                    final_score += abs(target_rss - self.mis_pen_rss)

        elif self.scor_alg == 'E':
            sum_sq_diff = 0             # Euclidean
            for mac, target_rss in target_fp.items():
                if mac in live_fp:
                    diff = target_rss - live_fp[mac]
                    sum_sq_diff += (diff ** 2)
                else:
                    diff = target_rss - self.mis_pen_rss
                    sum_sq_diff += (diff ** 2)
            final_score = math.sqrt(sum_sq_diff)

        # Penalize strong alien signals
        for mac, live_rss in live_fp.items():
            if mac not in target_fp and live_rss > -60:
                final_score += 20
        return final_score
    
    def dictToWNT(self,event):
        with open('WTKPoints', 'w') as f:
            for key, lst in self.scores.items():
                f.write(f'{key[0]},{key[1]},{lst[0]},{lst[1]},{lst[2]},{lst[3]}\n')

    def compute_score(self, live_observation):
        targets = {}
        for location, location_path in self.target_files.items():
            fp, kept, total = self.process_csv_fingerprint(location_path)
            if not fp:
                print(f"Warning: no fingerprint for {location}, skipping.")
                continue
            targets[location] = {"fp": fp, "kept": kept, "total": total}

        live_fp, live_kept, live_total = self.process_csv_fingerprint(live_observation)
        if not live_fp:
            print("Warning: no live fingerprint, skipping this cycle.")

        score_lst = []
        for location, target_info in targets.items():
            target_fp = target_info["fp"]
            live_score = self.score(target_fp, live_fp)
            score_lst.append((location, live_score))
        return score_lst

def main():
    Map = BKMap()

if __name__ == '__main__':
    main()
