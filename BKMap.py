from tkinter import Canvas, Tk

import numpy as np
import rasterio
from matplotlib import cm
from PIL import Image, ImageTk
from Logger import Logger
import time

class BKMap(Tk):

    def __init__(self, filename):
        Tk.__init__(self)
        self.logger = Logger(filename)
        self.log = {}
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
        print(self.log.keys())

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

def main():
    Map = BKMap()

if __name__ == '__main__':
    main()
