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
        self.logs = {}
        self.filename = filename
        self.title = 'Map of Bouwkunde'
        self.h = 1080
        self.w = 1920
        self.currentPos = (0, 0)
        self.resizable(0,0)
        self.bind("q", self.exit)
        self.bind("l", self.logging)
        self.bind("p", self.printLogs)
        self.isLogging = False
        self.output_info()

        self.openImage()
        self.setCanvas()
        self.setDisplay()

        self.protocol('WM_DELETE_WINDOW', self.quitProgram)

        self.isRunning = True
        self.draw()


    def setDisplay(self):
        self.bind("<Motion>", self.displayCoords)
        self.bind("<ButtonRelease>", self.onMouseClick)
        self.coordstext = self.canvas.create_text(
            self.w, self.h, fill="black", anchor="se", text=""
        )
        self.loggingText = self.canvas.create_text(
            self.w//2, 0, fill="black", anchor="n", text=""
        )
    
    def output_info(self):
        print(
            f"=====Use=====\n\
Press on the map to add location. \n\
Press 'L' to start or stop logging\n\
Press 'Q' to quit the program \n \
Press 'P' to print logs\n \
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
            s = f'{wx}, {wy}'
            self.canvas.itemconfig(self.coordstext, text=s)

    def onMouseClick(self, event):
        self.drawPoint(event.x, event.y)
        if self.isLogging:
            self.logger.endLog()
            self.log[self.currentPos] = self.logger.getLogs()
            self.logger.startLog()
        self.currentPos = (event.x, event.y)

    def drawPoint(self, x, y):
        radius = 3
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill='red')

    def logging(self, event):
        if self.isLogging:
            self.isLogging = False
            self.logger.endLog()
            if self.log[self.currentPos] is None:
                self.log[self.currentPos] = self.logger.getLogs()
            txt = 'Not logging :('
        else:
            self.isLogging = True
            self.logger.startLog()
            txt = 'Logging! :D'
        self.canvas.itemconfig(self.loggingText, text = txt)

    def draw(self):
        while self.isRunning:
            self.canvas.update()

    def printLogs(self):
        print(self.log)
        
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
