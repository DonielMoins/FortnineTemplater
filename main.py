from datetime import date
import logging
from objects import Profile, Request
import multiprocessing as mp
from multiprocessing.connection import Connection
import tkinter as tk
import tkinter.scrolledtext as tkscrolled


import utils.parallelProcessing as proc
from utils.general import getOverrides, parseCSV
from utils.requests import MakeRequests
import utils.config as cfg


today = date.today()
dayDate = today.strftime("%d-%m-%Y")

# Settings
_ov = getOverrides()
GlobalLaunchParams = {
    "GUI": {
        "openEditor": True
    }
}


# Initialize the GUI then start FrameController with minimum size.
# Finally run main tkinter's mainloop()
def startGUI(launchParams, taskQueue: mp.JoinableQueue,  progressReceiver: Connection, progressSender: Connection):

    master = FrameController(launchParams, taskQueue,
                             progressReceiver, progressSender)
    master.geometry("")
    master.minsize(height=100, width=300)

    # mainloop, runs infinitely
    master.mainloop()


# EditorFrame
class EditorFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Editor Mode")
        label.pack(pady=10, padx=10)

        switchbtn = tk.Button(self, text="Switch to User Mode",
                              command=lambda: controller.show_frame(SelectorFrame))
        createProfilebtn = tk.Button(self, text="Create new Profile",
                                     command=lambda: ProfileEditor(master=parent))
        deleteProfilebtn = tk.Button(self, text="Delete pre-existing Profile",
                                     command=lambda: controller.show_frame(SelectorFrame))
        editProfilesbtn = tk.Button(self, text="Edit Profile",
                                    command=lambda: controller.show_frame(SelectorFrame))
        switchbtn.pack(pady=10, padx=10)
        createProfilebtn.pack(pady=10, padx=10)
        deleteProfilebtn.pack(pady=10, padx=10)
        editProfilesbtn.pack(pady=10, padx=10)

# Making this GUI makes me wanna kill myself


class ProfileEditor(tk.Toplevel):
    def __init__(self, master=None, profile: Profile = None):
        super().__init__(master=master)
        self.title("Profile Creator")
        self.minsize(height=400, width=400)
        self.requestsList = []
        # self.grid(sticky="nsew")
        if profile is not None:
            self.profileName = profile.profileName
            self.requests = profile.requests
        else:
            self.profileName = tk.StringVar(self, "Default Name")
            self.requests = [Request()]

        for index, item in enumerate(self.requests):
            self.requestsList.append({"uri": tk.StringVar(
                self, item.uri), "reqtype": tk.StringVar(self, item.reqtype.upper())})
            self.requestsList[index]["Entry"] = tk.Entry(
                self, textvariable=self.requestsList[index]["uri"], width=80)

        self.currentRequest = 0
        self.nameLabel = tk.Label(self, text="Profile Name:")
        self.nameEntry = tk.Entry(
            self, textvariable=self.profileName, width=75)
        self.currentRequestLabel = tk.Label(
            self, text=f"Viewing Request: {self.currentRequest + 1}/{len(self.requests)}")

        # Request part
        self.requestUriLabel = tk.Label(self, text="Request Uri:")
        self.requestMethodDropdown = [tk.OptionMenu(
            self, self.requestsList[0]["reqtype"], *("GET", "HEAD", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"))]

        self.nameLabel.grid(row=0, column=0, sticky="w")
        self.nameEntry.grid(row=0, column=1, columnspan=2,
                            rowspan=2, padx=5, sticky="n")
        self.currentRequestLabel.grid(row=0, column=4, sticky="ne")

        self.requestUriLabel.grid(row=1)
        self.requestsList[0]["Entry"].grid(row=1, column=1)
        self.requestMethodDropdown[0].grid(row=1, column=4)

        self.prevRequestbtn = tk.Button(
            self, text="Previous Request", command=lambda: self.prevReq(True))
        self.newRequestbtn = tk.Button(
            self, text="New Request", command=lambda: self.CreateRequest(True))
        self.nextRequestbtn = tk.Button(
            self, text="Next Request", command=lambda: self.nextReq(True))
        self.saveProfilebtn = tk.Button(
            self, text="Save Profile", command=lambda: self.saveProfile)
        self.redrawAll()

    def saveProfile(self):
        prof = Profile(ProfileName=self.profileName, Requests=self.requests)
        cfg.add_profile(cfg.get_config(), prof)
        self.destroy()
    # Called whenever remaking window

    def clearScreen(self):
        for widget in self.winfo_children():
            widget.grid_forget()

    def upperWidgets(self, redraw=False):
        self.currentRequestLabel.config(
            text=f"Viewing Request: {self.currentRequest + 1}/{len(self.requests)}")
        self.nameLabel.grid(row=0, column=0, sticky="w")
        self.nameEntry.grid(row=0, column=1, columnspan=2,
                            rowspan=2, padx=5, sticky="n")
        self.currentRequestLabel.grid(row=0, column=4, sticky="ne")
        if redraw:
            self.redrawAll()

    def bottomWidgets(self, redraw=False):
        if len(self.requestsList) > 1:
            self.prevRequestbtn.grid(
                row=4, column=1, sticky="SEW", columnspan=1, padx=5)
            self.nextRequestbtn.grid(
                row=4, column=3, sticky="SEW", columnspan=1, padx=5)
        self.newRequestbtn.grid(
            row=4, column=2, columnspan=1, sticky="SEW", padx=5)
        self.saveProfilebtn.grid(
            row=5, column=2, columnspan=1, sticky="SEW", padx=5)
        if redraw:
            self.redrawAll()

    def showRequestWidgets(self, redraw=False):
        self.requestUriLabel.grid(row=1)
        self.requestsList[self.currentRequest]["Entry"].grid(row=1, column=1)
        self.requestMethodDropdown[self.currentRequest].grid(row=1, column=4)
        if redraw:
            self.redrawAll()

    def prevReq(self, redraw=False):
        if len(self.requestsList) > 1:
            if self.currentRequest == 0:
                self.currentRequest = len(self.requestsList) - 1
            else:
                self.currentRequest -= 1
            if redraw:
                self.redrawAll()

    def nextReq(self, redraw=False):
        if len(self.requestsList) > 1:
            if self.currentRequest == len(self.requestsList) - 1:
                self.currentRequest = 0
            else:
                self.currentRequest += 1
            if redraw:
                self.redrawAll()

    def CreateRequest(self, redraw=False):
        newReq = Request()
        self.requests.append(newReq)
        self.requestsList.append({"uri": tk.StringVar(
            self, newReq.uri), "reqtype": tk.StringVar(self, newReq.reqtype.upper())})
        self.requestsList[len(self.requestsList) - 1]["Entry"] = tk.Entry(
            self, textvariable=self.requestsList[len(self.requestsList) - 1]["uri"], width=80)
        self.requestMethodDropdown.append(tk.OptionMenu(self, self.requestsList[len(
            self.requestsList) - 1]["reqtype"], *("GET", "HEAD", "POST", "PATCH", "PUT", "DELETE", "OPTIONS")))
        if redraw:
            self.redrawAll()

    def redrawAll(self):
        self.clearScreen()
        self.upperWidgets()
        self.showRequestWidgets()
        self.bottomWidgets()


#  TODO Parse Progress Data
class SelectorFrame(tk.Frame):
    def __init__(self, parent, controller):
        """ 
            Creates a button for each Profile using Profile.profileName as Button Text.
            If request function sends progress of a Profile, button should block with possible addition of a progress bar.
        """
        tk.Frame.__init__(self, parent)

        config = cfg.get_config()
        profiles = config.profiles
        progressReceiver: Connection = controller.progressReceiver
        progressSender: Connection = controller.progressSender
        self.profileButtons = []
        if len(profiles) > 0:
            ProfilesLabel = tk.Label(self, text="Run profiles:")
            ProfilesLabel.pack(pady=10, padx=10)
            for profile in profiles:
                button = tk.Button(self, text=profile.profileName,
                                   command=lambda: DataEntry(requests=profile.requests, taskQueue=controller.taskQueue, progressSender=progressSender))
                self.profileButtons.append(button)
                button.pack(padx=10, pady=10)
        else:
            ProfilesLabel = tk.Label(
                self, text="Error: No profiles in config file.")
            ProfilesLabel.pack(pady=10, padx=10)

        if progressSender and progressReceiver:
            self.disabledButtons: list[tk.Button] = []
            self.after_idle(self.checkInactiveButtons, progressReceiver)

    # TODO Understand what button is being run, then add it to self.blockedButtons
    def checkInactiveButtons(self, progressReceiver: Connection):
        """
            If blockedButtons contains a button, grey it out, then re-add check to tkinter's idle loop.
            progressReceiver.recv() blocks, so if progressReceiver contains any data, progressReceiver.recv()
            then parse which Profile should be blocked.
            Add said button to sef.blockedButtons.

            Poll progress Pipe with timeout of 0.3 seconds
        """
        data = ""
        if progressReceiver.poll(0.3):
            data = progressReceiver.recv()
        if data != "":
            print(data)

        for button in self.profileButtons:
            if button in self.disabledButtons:
                button.setvar("state", "disabled")
            else:
                button.setvar("state", "normal")
        self.after(1500, self.checkInactiveButtons, progressReceiver)


# God I love StackOverflow
Screens = (EditorFrame, SelectorFrame)


class FrameController(tk.Tk):

    def __init__(self, launchParams: dict, taskQueue: mp.JoinableQueue, progressReceiver: Connection, progressSender: Connection, *args, **kwargs):

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

        # GUI Parameters, edit at Start of file
        if len(launchParams) > 0:
            if launchParams["openEditor"]:
                self.show_frame(EditorFrame)
            else:
                self.show_frame(SelectorFrame)
                # self.after(5000, printReceived, args=(progressReceiver)

    def show_frame(self, frame):
        frame = self.frames[frame]
        frame.tkraise()


class DataEntry(tk.Toplevel):
    def __init__(self, taskQueue, master=None, requests=[], progressSender=None):
        # TODO add drag and drop to facilitate Inputing CSV data
        """Create Data Entry window to paste in csv data then send request to ReqExecPool.
            Can handle multiple requests, each request hosting a page with an Input Field

        Args:
            taskQueue ([JoinableQueue]): Task Queue to send Requests to.
            master ([type], optional): Master window that spawned frame. Defaults to None.
            requests (list, optional): Requests list taken from Profile.requests. Defaults to [].
        """
        super().__init__(master=master)
        self.title("Input Request variables")
        self.requests = requests
        self.CurrentInput = 1
        self.InputFields = []
        self.taskQueue = taskQueue
        self.progressSender = progressSender

        for i in self.requests:
            input = tkscrolled.ScrolledText(self)
            self.InputFields.append(input)
        ReqPreviewLabel = tk.Label(
            self, text=f"Preview: {self.requests[self.CurrentInput - 1].uri}")
        ReqPreviewLabel.grid(padx=10, row=0, rowspan=1)
        ReqMethodLabel = tk.Label(
            self, text=f"Method: {self.requests[self.CurrentInput - 1].reqtype.upper()}")
        ReqMethodLabel.grid(padx=10, row=0, rowspan=1, column=1)

        if len(self.InputFields) > 1:
            self.InputFields[self.CurrentInput - 1].grid(padx=10, row=1)
            self.MakeButtons()

        elif len(self.InputFields) == 1:
            self.InputFields[0].grid(padx=10, row=1, columnspan=2)
            self.MakeButtons()
        else:
            self.SendBtn = tk.Button(
                self, text="Make Request", command=lambda: self.SendRequest(self.requests))
            self.SendBtn.grid(padx=10, pady=5, row=2, columnspan=2)
        self.geometry("")


# Add buttons to end of DataEntry screen.


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
            self, text="Make Request", command=lambda: self.SendRequest(self.requests))
        self.SendBtn.grid(padx=10, row=3, pady=5, columnspan=2)

# Clears DataEntry screen and displays entry fields for the next request.
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

# Clears DataEntry screen and displays entry fields for the Previous request.
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

# Get Input of every Request, parse data, then send a requestTask with requests, FieldsData and ProgressSender to TaskQueue.
    def SendRequest(self, requests):
        FieldsData = []
        for InputField in self.InputFields:
            text: str = InputField.get('1.0', tk.END)
            Data = parseCSV(text)
            FieldsData.append(Data)

        reqsTask = proc.TaskThread(
            fun=MakeRequests, args=(requests, FieldsData, self.progressSender))
        self.taskQueue.put(reqsTask)

        self.destroy()


# If DEBUG file found in overrides folder, enable debug logging
if _ov is not None and "DEBUG" in _ov:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                        filename=f"templater-{dayDate}.log", level=logging.DEBUG)
else:
    logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                        filename=f"templater-{dayDate}.log", level=logging.INFO)

    """            So, this is complicated but here we go.
    
    MultiProcessing.Manager creates a Task Queue, Progress Sender and Receiver
    These will later be shared between the Request Executioner Pool and the GUI Process.
    
    Then, setup GUI Process with GlobalLaunchParams["GUI"]
    start GUI Process and add it to Processes dictionary.
    
    Setup Request Executioner Pool using AsyncParallel and add it to Processes Dict.
    Then using ProgressSender/Receiver and TaskQueue run "PatientThread"; Infinitely loops \
        waiting for a job in the TaskQueue, once a job is found, Send it Directly to 
        the RequestExecPool.
        
    Infinitely Loop while any items are in Processes Dict checking
        if "GUI" Process is alive.
    If GUI Process is dead, .join() all processes in Processes Dictionary, send
        QueueEndSignal to the TaskQueue and close Progress Pipes.
        Once all of the multiprocessing Processes are dead, exit the loop.
    
    Shutdown logger, because its 5 o'clock and I need to go home.
     
    """

Processes = {}


def main():
    taskQueue = mp.JoinableQueue()
    progressSender, progressReceiver = mp.Pipe()
    Processes["TaskQueue"] = taskQueue

    GUIProc = mp.Process(target=startGUI, name="GUI", args=(
        GlobalLaunchParams.get("GUI", {}), taskQueue, progressReceiver, progressSender))
    GUIProc.start()
    Processes["GUI"] = GUIProc

    RequestExecPool = proc.AsyncParallel()
    Processes["ReqExecPool"] = RequestExecPool
    proc.runPatientThread(RequestExecPool, taskQueue, progressSender)

    while(Processes):
        if not Processes["GUI"].is_alive():
            for name, thread in Processes.items():
                if name != "GUI":
                    thread.join()
                    logging.info(f"Joined Process {name}.")

            taskQueue.put(proc._QueueEndSignal())
            logging.info("Sent TaskQueue End Signal.")

            if progressSender or progressReceiver:
                progressSender.close()
                progressReceiver.close()
                logging.info("Closed Progress Pipes")
            break
    logging.info("Ending program. Good night ;p")
    logging.shutdown()


if __name__ == '__main__':
    logging.info('Starting up Templater')
    logging.debug(
        f"Starting with following parameters: \n{GlobalLaunchParams}")

    main()

    logging.debug('All sub-processes dead, program ending.')
