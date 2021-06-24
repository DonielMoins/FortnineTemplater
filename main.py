from datetime import date
import logging
import multiprocessing
from sys import maxsize
import tkinter as tk
import tkinter.scrolledtext as tkscrolled
# Python libraries/modules ^
from utils.general import getOverrides
from utils.requests import MakeRequests
import utils.config as cfg


today = date.today()
dayDate = today.strftime("%d-%m-%Y")
_ov = getOverrides()


def startGUI(**kwargs):
    
    master = FrameController(kwargs=kwargs)
    master.geometry("")
    master.minsize(height=100, width=300)
    
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
        if kwargs["openEditor"]:
            self.show_frame(EditorFrame)
        else:
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

        

        # button = tk.Button(self, text="Editor Screen", command=lambda: controller.show_frame(EditorFrame))
        # button.pack()
        config = cfg.get_config()
        profiles = cfg.get_profiles(config)
        if len(profiles) > 0:
            ProfilesLabel = tk.Label(self, text="Run profiles:")
            ProfilesLabel.pack(pady=10, padx=10)
            for profile in profiles:
                button = tk.Button(self, text=profile.ProfileName,
                                   command=lambda: DataEntry(requests=profile.Requests))
                button.pack(padx=10, pady=10)
        else:
            ProfilesLabel = tk.Label(self, text="Error: No profiles in config file.")
            ProfilesLabel.pack(pady=10, padx=10)
            
            
#  Hard to refactor cause GUI programming is annoying
class DataEntry(tk.Toplevel):
    def __init__(self, master=None, requests=[]):

        super().__init__(master=master)
        self.title("Input Request variables")
        self.requests = list(requests[0].values())
        self.CurrentInput = None
        self.InputFields = []
        
        dnd = DragManager()
        
        for i in self.requests:
            input = tkscrolled.ScrolledText(self)
            self.InputFields.append(input)
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

class DragManager():
    def add_dragable(self, widget):
        widget.bind("<ButtonPress-1>", self.on_start)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_drop)
        widget.configure(cursor="hand1")

    def on_start(self, event):
        # you could use this method to create a floating window
        # that represents what is being dragged.
        pass

    def on_drag(self, event):
        # you could use this method to move a floating window that
        # represents what you're dragging
        pass

    def on_drop(self, event):
        # find the widget under the cursor
        x,y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x,y)
        try:
            # image=event.widget.cget("image")
            target.configure(text=event.widget.cget("text"))
            
        except:
            pass
    
    # def replaceText(self, text):
    #     self.delete(1.0,"end")

Screens = (EditorFrame, SelectorFrame)

# Holds all sub-processes
Processes = {}

# If DEBUG file found in overrides folder, enable debug logging
if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s", filename=f"templater-{dayDate}.log", level=logging.INFO)   

def main(**kwargs):
    logging.debug(f"Starting with following parameters: \n{kwargs}")
    
    openEditor = False
    if kwargs:
        __dict__.update(kwargs)
    
    # Queues, Lists, etc. for communication between Processes
    ActiveTasks = multiprocessing.Array() 
        
    
    
    GUIProc = multiprocessing.Process(target=startGUI, args=())
    RequestExecPool= multiprocessing.Pool(maxsize=8)
    
    # Start our dearest GUI
    GUIProc.start()
    Processes["GUI"] = GUIProc
    
    # Make sure that if all opened sub-processes are dead if GUI is dead; if so, main ends gracefully.
    # Checks from Processes Dict.
    while(Processes):
        if not Processes["GUI"].is_alive():
            for name, thread in Processes.items():
                if name != "GUI":
                    thread.join()
            break
    logging.debug('All sub-processes dead, function main ending gracefully.')
    
            

if __name__ == '__main__':
    logging.info('Starting up Templater')
    main()