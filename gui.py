import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
# from tkFileDialog import askopenfilename
from tkinter.messagebox import showerror
from PIL import Image, ImageTk
import matplotlib
from cancer import Cancer

import numpy as np
import cv2

matplotlib.use("TkAgg")

FONT = ('Verdana',12)
TITLE = ('Verdana',22)
ABSTRACT_FONT = ('Verdana',18)

bilol = []
title = "Project name" # Add project title here
content = "Content here" # Add content here
abstract = """
Abstract here
"""
# Abstract here

class MAINGUI(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self, *args,**kwargs)
        try:
            tk.Tk.iconbitmap(self,default="favicon.ico")
        except:
            pass
        tk.Tk.wm_title(self,"Cancer Detector")
        tk.Tk.wm_minsize(self,500,550)
        tk.Tk.wm_maxsize(self,501,550)
        container = tk.Frame(self,bg="#125421", highlightbackground="red", highlightcolor="green", highlightthickness=5)
        container.pack(side="top",fill="both",expand = True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        container.configure(background='black')

        self.menubar = Menu(self)
        menu_one = Menu(self.menubar, tearoff=0)
        menu_two = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu_one)
        self.menubar.add_cascade(label="Help", menu=menu_two)
        menu_one.add_command(label="Home",command=lambda:self.show_frame(HomeFrame))
        menu_one.add_command(label="Exit",command=quit)
        menu_two.add_command(label="About Project",command=lambda:self.show_frame(AboutProject))
        menu_two.add_command(label="About Developers",command=lambda:self.show_frame(AboutDevelopers))

        try:
            tk.Tk.config(self,menu=self.menubar)
        except AttributeError as p:
            print(str(p))

        self.frames = {}
        for F in (AboutDevelopers, AboutProject, HomeFrame):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column = 0,sticky = "Nsew")
        self.show_frame(HomeFrame)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()    

data = [('one', 'one@gmail.com'),('two', 'two@email'),('three', 'three@gmail.com'),('four', 'four@gmail.com')]

class AboutDevelopers(tk.Frame):
    def __init__(self,parent,control):
        tk.Frame.__init__(self,parent)
        row = 1
        Label(self, text="About Developers", font=TITLE,fg="blue").grid(row=0,column=0,columnspan=2,pady=10, padx=10)
        for da in data:
            Label(self, text=da[0],font=("Helvetica", 32),fg="blue").grid(row=row,column=0)
            Label(self, text=da[1],font=("Helvetica", 32),fg="blue").grid(row=row,column=0)
            row += 1

class AboutProject(tk.Frame):
    def __init__(self, parent, control):
        tk.Frame.__init__(self, parent)
        Label(self, text=title, font=TITLE,fg="blue").pack(pady=10, padx=10)
        label = Label(self, text=abstract, font=ABSTRACT_FONT,fg="blue").pack(pady=10, padx=10)


class HomeFrame(tk.Frame):

    def __init__(self, parent, control):
        tk.Frame.__init__(self, parent)
        self.filename = None
        self.con = control
        Label(self, text="Enter Age ", font=FONT,fg="#000").grid(row=3,column=1,pady=10,padx=10)
        Label(self, text="Enter Gender (M/F)", font=FONT,fg="#000").grid(row=3,column=2,pady=10,padx=10)
        
        self.age = Entry(self,font=FONT)
        self.age.grid(row=4,column=1,pady=10,padx=10)

        self.gender = Entry(self,font=FONT)
        self.gender.grid(row=4,column=2,pady=10,padx=10)

        Button(self, text="Browse", command=self.load_file, width=50, fg="#000").grid(row=5,columnspan=3,pady=10,padx=10)
        Button(self, text="Run", command=self.predict,width=50, fg="#000").grid(row=6,pady=10,padx=10,columnspan=3)
        #self.capacity.grid_forget()

    def load_file(self):
        fname = askopenfilename(filetypes=(("Images", "*.png*"),("All files", "*.*")))
        if fname:
            try:
                self.filename = fname
                print(str(fname))
            except Exception as e:
                showerror("Open Source File", "Failed to read file\n'%s'" % fname)
                showerror(e)
            return
 
    def predict(self):
        age = self.age.get()
        gender = self.gender.get()
        image = self.filename
        if not (image and age and gender):
            showerror("Error")
            Message("No Image is selected")
            return
        c = Cancer()
        im = Image.open(image) # <--- chokes!
        # im.resize(250,150)
        im=im.resize((250,150))
        if im.mode == "1":
            self.image = ImageTk.BitmapImage(im, foreground="white")
            Label(self, image=self.image, bg="black", bd=0).grid(row=8,column=1,pady=10,padx=10,columnspan=2)
        else:
            self.image = ImageTk.PhotoImage(im)
            Label(self, image=self.image, bd=0).grid(row=8,column=1,pady=10,padx=10,columnspan=2)

        img = cv2.imread(image)
        resized = cv2.resize(img, (250,150), interpolation = cv2.INTER_AREA)
        filters = self.build_filters()
        res1 = self.process(resized, filters)
        #imgtk = ImageTk.PhotoImage(image=Image.fromarray(res1))
        imgtk = ImageTk.PhotoImage(Image.fromarray(res1)) 
        #cv2.imshow('result', res1)
        Label(self, image=imgtk, bd=0).grid(row=9,column=1,pady=10,padx=10,columnspan=2)        
        output = c.predict(image, gender, age)
        if output.get('error'):
            Label(self, text="Error => {}".format(output.get('error', 'No')), font=FONT,fg="#000").grid(row=7,column=1,pady=10,padx=10)
            return
        Label(self, text="Result {}".format(output.get('cancer', 'No')), font=FONT,fg="#000").grid(row=7,column=1,pady=10,padx=10)
        Label(self, text="Cancer Label is {}".format(output.get('cancer_type', 'Type')), font=FONT,fg="#000").grid(row=7,column=2,pady=10,padx=10)
        Label(self, text="DO anything here", font=FONT,fg="#000").grid(row=10,column=1,pady=10,padx=10)
        Label(self, text="Do anything here 2", font=FONT,fg="#000").grid(row=10,column=2,pady=10,padx=10)



    def build_filters(self):
        filters = []
        ksize = 31
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            kern /= 1.5*kern.sum()                          
            filters.append(kern)
        return filters

    def process(self, img, filters):
        accum = np.zeros_like(img)
        for kern in filters:
            fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)              
        return accum

app = MAINGUI()
app.resizable(False, False)
app.mainloop()
