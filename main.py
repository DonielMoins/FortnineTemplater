from datetime import date
import logging
import multiprocessing as mp
from multiprocessing.connection import Connection
import time
from sys import maxsize
import tkinter as tk
import tkinter.scrolledtext as tkscrolled
# Python libraries/modules ^
import utils.parallelProcessing as proc
from utils.general import getOverrides, parseCSV
from utils.requests import MakeRequests
import utils.config as cfg


today = date.today()
dayDate = today.strftime("%d-%m-%Y")
_ov = getOverrides()
GlobalLaunchParams = {
    "GUI": {
        "openEditor": True
    }
}


def startGUI(launchParams={}, taskQueue: mp.JoinableQueue = None,  progressReceiver: Connection = None):

    master = FrameController(launchParams, taskQueue, progressReceiver)
    master.geometry("")
    master.minsize(height=100, width=300)

    # mainloop, runs infinitely
    master.mainloop()


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
        progressReceiver: Connection = controller.progressReceiver
        progressSender: Connection = controller.progressSender
        if len(profiles) > 0:
            ProfilesLabel = tk.Label(self, text="Run profiles:")
            ProfilesLabel.pack(pady=10, padx=10)
            for profile in profiles:
                button = tk.Button(self, text=profile.ProfileName,
                                   command=lambda: DataEntry(requests=profile.Requests, taskQueue=controller.taskQueue, progressSender=progressSender))
                button.pack(padx=10, pady=10)
        else:
            ProfilesLabel = tk.Label(
                self, text="Error: No profiles in config file.")
            ProfilesLabel.pack(pady=10, padx=10)


# Possible Frames.
Screens = (EditorFrame, SelectorFrame)


class FrameController(tk.Tk):

    def __init__(self, taskQueue: mp.JoinableQueue, progressReceiver: Connection, progressSender: Connection, launchParams={}, *args, **kwargs):

        tk.Tk.__init__(
            self, className='Fortnine Request Templates', *args, **kwargs)
        container = tk.Frame(self)
        self.taskQueue = taskQueue
        self.progressReceiver = progressReceiver
        self.progressSender = progressSender
        

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in Screens:

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SelectorFrame)
        # self.after(20000, printReceived, [progressReceiver])
        # TODO this doesnt try to match against dict key 
        # GUI Parameters, edit at EOF
        # if len(launchParams) > 0:
        #     match launchParams.keys():
        #         case "openEditor":
        #             if launchParams["openEditor"]:
        #                 self.show_frame(EditorFrame)
        #             else:
        #                 self.show_frame(SelectorFrame)
        #                 self.after(5000, printReceived, args=(progressReceiver))
        #         case _:
        #             pass

    def show_frame(self, frame):
        frame = self.frames[frame]
        frame.tkraise()


# Hard to refactor cause GUI programming is annoying
class DataEntry(tk.Toplevel):
    def __init__(self, taskQueue, master=None, requests=[], progressSender=None):
        """Data entry window to drop in csv data then send request to ReqExecPool

        Args:
            taskQueue ([JoinableQueue]): Task Queue to send Requests to.
            master ([type], optional): Master window that spawned frame. Defaults to None.
            requests (list, optional): Requests list taken from Profile.Requests. Defaults to [].
        """
        super().__init__(master=master)
        self.title("Input Request variables")
        self.requests = list(requests[0].values())
        self.CurrentInput = None
        self.InputFields = []
        self.taskQueue = taskQueue
        self.progressSender = progressSender
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
            Data = parseCSV(text)
            FieldsData.append(Data)
            self.destroy()

        reqsTask = proc.TaskThread(
            fun=MakeRequests, args=(requests, FieldsData, self.progressSender))
        self.taskQueue.put(reqsTask)


def printReceived(progressReceiver: Connection):
    progressReceiver = progressReceiver[0]
    
    print("Data:")
    print(progressReceiver.recv())
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
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        try:
            # image=event.widget.cget("image")
            target.configure(text=event.widget.cget("text"))

        except:
            pass

    # def replaceText(self, text):
    #     self.delete(1.0,"end")


# Holds all sub-processes
Processes = {}
# [Key Name]: [Summary]
#       GUI: Tkinter Gui Process
#       ReqExecPool: AsyncParallel


# If DEBUG file found in overrides folder, enable debug logging
if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                        filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                        filename=f"templater-{dayDate}.log", level=logging.INFO)


if __name__ == '__main__':
    logging.info('Starting up Templater')
    # logging.debug(f"Starting with following parameters: \n{kwargs}")

    openEditor = False
    # if kwargs:
    #     __dict__.update(kwargs)

    # So, this is complicated but here we go
    # manager creates shared dict
    with mp.Manager() as manager:
        taskQueue = manager.JoinableQueue()
        progressSender, progressReceiver = mp.Pipe()
        Processes["TaskQueue"] = taskQueue

        GUIProc = mp.Process(target=startGUI, args=(taskQueue, progressReceiver, GlobalLaunchParams.get("GUI", {})))
        # Start our dearest GUI
        GUIProc.start()
        Processes["GUI"] = GUIProc
        while not GUIProc.is_alive():
            time.sleep(0.01)

        RequestExecPool = proc.AsyncParallel()
        Processes["ReqExecPool"] = RequestExecPool
        proc.runPatientThread(RequestExecPool, taskQueue, progressSender)

        # Make sure that if all opened sub-processes are dead if GUI is dead; if so, program ends gracefully.
        # Checks from Processes Dict.
        while(Processes):
            if not Processes["GUI"].is_alive():
                for name, thread in Processes.items():
                    if name != "GUI":
                        thread.join()
                # Send kill signal to PatientThread
                taskQueue.put(proc._QueueEndSignal())
                if progressSender or progressReceiver:
                    progressSender.close()
                    progressReceiver.close()
                break

    logging.debug('All sub-processes dead, program ending.')
