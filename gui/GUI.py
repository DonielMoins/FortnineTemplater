from turtle import width
from typing import List
from utils.requests import MakeRequests, makeRequest
from wsgiref.validate import InputWrapper
from classes import requestObj
import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import utils.config as cfg
import multiprocessing, logging

def process(*args):
    
    master = FrameController()
    master.geometry("800x200")
    # mainloop, runs infinitely
    master.mainloop()
    
class FrameController(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, className='Fortnine Request Templates', *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)
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
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Options")
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Selector Screen", command=lambda: controller.show_frame(SelectorFrame))
        button.pack()
        
class SelectorFrame(tk.Frame):
      
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        label = tk.Label(self, text="Run profiles:")
        label.pack(pady=10,padx=10)

        # button = tk.Button(self, text="Editor Screen", command=lambda: controller.show_frame(EditorFrame))
        # button.pack()
        config = cfg.get_config()
        profiles = cfg.get_profiles(config)
        for profile in profiles:
            button = tk.Button(self, text=profile.ProfileName, command= lambda: VariableEntry(requests=profile.Requests))
            button.pack()
        i = 1

class VariableEntry(tk.Toplevel):
    def __init__(self, master = None, requests = []):
              
        super().__init__(master = master)
        self.title("Input Request variables")
        self.geometry("800x420")
        # label = tk.Label(self, text ="This is a new Window")
        # label.pack()
        self.InputFields = []
        for req in requests:
            self.InputFields.append(tkscrolled.ScrolledText(self))
        for field in self.InputFields:
            field.pack()
        
        self.SendBtn = tk.Button(self, text="Make Request", command=lambda: self.MakeRequest(requests))
        self.SendBtn.pack()
        
    def MakeRequest(self, requests):
        FieldsData = []
        for InputField in self.InputFields:
            text : str = InputField.get('1.0', tk.END)
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