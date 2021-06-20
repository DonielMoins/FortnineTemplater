from turtle import width
from typing import List
from utils.requests import MakeRequests, makeRequest
from wsgiref.validate import InputWrapper
from classes import requestObj
import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import utils.config as cfg
import multiprocessing
import logging


def process(*args):

    master = FrameController()
    master.geometry("800x200")
    # mainloop, runs infinitely
    master.mainloop()


class FrameController(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(
            self, className='Fortnine Request Templates', *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in Screens:

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SelectorFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class EditorFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Options")
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Selector Screen",
                           command=lambda: controller.show_frame(SelectorFrame))
        button.pack()


class SelectorFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        ProfilesLabel = tk.Label(self, text="Run profiles:")
        ProfilesLabel.pack(pady=10, padx=10)

        # button = tk.Button(self, text="Editor Screen", command=lambda: controller.show_frame(EditorFrame))
        # button.pack()
        config = cfg.get_config()
        profiles = cfg.get_profiles(config)
        for profile in profiles:
            button = tk.Button(self, text=profile.ProfileName,
                               command=lambda: DataEntry(requests=profile.Requests))
            button.pack()
        i = 1

# TODO: Make prettier
class DataEntry(tk.Toplevel):
    def __init__(self, master=None, requests=[]):

        super().__init__(master=master)
        self.title("Input Request variables")
        self.requests = list(requests[0].values())
        self.CurrentInput = None
        self.InputFields = []
        for i in self.requests:
            self.InputFields.append(tkscrolled.ScrolledText(self))
        if not self.CurrentInput:
            self.CurrentInput = 1
        ReqPreviewLabel = tk.Label(
            self, text=f"Preview: {self.requests[self.CurrentInput - 1]['uri']}")
        ReqPreviewLabel.grid(padx=10, row=0, rowspan=1)
        ReqMethodLabel = tk.Label(
            self, text=f"Method: {self.requests[self.CurrentInput - 1]['reqtype'].upper()}")
        ReqMethodLabel.grid(padx=10, row=0, rowspan=1, column=1)
        
        if len(self.InputFields) > 1:
            self.InputFields[self.CurrentInput - 1].grid(padx=10, row=1)
            self.MakeButtons()

        elif len(self.InputFields) == 1:
            self.InputFields[0].grid(padx=10, row=1, columnspan=2)
            self.MakeButtons()
        else:
            self.SendBtn = tk.Button(
                self, text="Make Request", command=lambda: self.MakeRequest(self.requests))
            self.SendBtn.grid(padx=10, pady=5, row=2, columnspan=2)
        self.geometry("")

    def MakeButtons(self):

        if self.CurrentInput != 1:
            self.PrevBtn = tk.Button(
                self, text="Previous Request", command=lambda: self.ShowPrevField())
            self.PrevBtn.grid(padx=10, row=2, pady=5)

        if self.CurrentInput != len(self.InputFields):
            self.NextBtn = tk.Button(
                self, text="Next Request", command=lambda: self.ShowNextField())
            self.NextBtn.grid(padx=10, row=2, pady=5)

        self.SendBtn = tk.Button(
            self, text="Make Request", command=lambda: self.MakeRequest(self.requests))
        self.SendBtn.grid(padx=10, row=3, pady=5, columnspan=2)

    def ShowNextField(self):
        self.CurrentInput += 1
        for widget in self.winfo_children():
            widget.grid_forget()
        ReqPreviewLabel = tk.Label(
            self, text=f"Preview: {self.requests[self.CurrentInput - 1]['uri']}")
        ReqPreviewLabel.grid(padx=10, row=0, rowspan=1)
        ReqMethodLabel = tk.Label(
            self, text=f"Method: {self.requests[self.CurrentInput - 1]['reqtype'].upper()}")
        ReqMethodLabel.grid(padx=10, row=0, rowspan=1, column=1)
        self.InputFields[self.CurrentInput - 1].grid(padx=10, row=1)
        self.MakeButtons()

    def ShowPrevField(self):
        self.CurrentInput -= 1
        for widget in self.winfo_children():
            widget.grid_forget()
        ReqPreviewLabel = tk.Label(
            self, text=f"Preview: {self.requests[self.CurrentInput - 1]['uri']}")
        ReqPreviewLabel.grid(padx=10, row=0, rowspan=1)
        ReqMethodLabel = tk.Label(
            self, text=f"Method: {self.requests[self.CurrentInput - 1]['reqtype'].upper()}")
        ReqMethodLabel.grid(padx=10, row=0, rowspan=1, column=1)
        self.InputFields[self.CurrentInput - 1].grid(padx=10, row=1)
        self.MakeButtons()

    def MakeRequest(self, requests):
        FieldsData = []
        for InputField in self.InputFields:
            text: str = InputField.get('1.0', tk.END)
            SplitText = text.split("\n")
            FieldsData.append(SplitText)
        try:
            MakeRequests(requests, FieldsData)
        except:
            # TODO: Catch error
            pass
        finally:
            self.destroy()


GUIProc = multiprocessing.Process(target=process, args=())
Screens = (EditorFrame, SelectorFrame)
