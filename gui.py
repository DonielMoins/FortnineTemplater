import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import tkinter.messagebox as popupBox
import gc
import re


import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import List
import utils.parallelProcessing as proc

from objects import Profile, Request
from utils.general import open_url, parseCSV
from constants import ProjDetails, DevDetails
from utils.requests import MakeRequests
import utils.config as cfg

# Initialize the GUI then start FrameController with minimum size.
# Finally run main tkinter's mainloop()


def startGUI(launchParams, taskQueue: mp.JoinableQueue,  stateReceiver: Connection, stateSender: Connection, master: bool):
    def key(x):
        # Ctrl + = (Equals key) switches to Selector Window
        # Ctrl + - (Minus Key) switches to Editor Frame
        # Ctrl + / switches to Credits Frame with an update checker
        if x.state == 4:
            match x.keysym.casefold():
                case 'equal':
                    master.show_frame(SelectorFrame, True)
                case 'minus':
                    master.show_frame(EditorFrame)
                case 'slash':
                    master.show_frame(CreditsFrame)
                case 'h':
                    # TODO ctrl + h opens screen with all shortcuts.
                    # master.show_frame(HelpFrame)
                    pass

    master = FrameController(launchParams, taskQueue,
                             stateReceiver, stateSender)
    if master:
        master.bind("<Key>", lambda x: key(x))
    master.geometry("")
    master.minsize(height=100, width=300)

    # mainloop, runs infinitely
    master.mainloop()


# EditorFrame
class EditorFrame(tk.Frame):

    def __init__(self, frameContainer, frameController):
        tk.Frame.__init__(self, frameContainer)
        self.parent = frameContainer
        label = tk.Label(self, text="Editor Mode")
        label.pack(pady=10, padx=10)

        switchbtn = tk.Button(self, text="Switch to User Mode",
                              command=lambda: frameController.show_frame(SelectorFrame, True))
        createProfilebtn = tk.Button(self, text="Create new Profile",
                                     command=lambda: self.openEditor())
        deleteProfilebtn = tk.Button(self, text="Delete pre-existing Profile",
                                     command=lambda: self.delProfile())
        editProfilesbtn = tk.Button(self, text="Edit Profile",
                                    command=lambda: self.editProfile())
        switchbtn.pack(pady=10, padx=10)
        createProfilebtn.pack(pady=10, padx=10)
        deleteProfilebtn.pack(pady=10, padx=10)
        editProfilesbtn.pack(pady=10, padx=10)

    def openEditor(self):
        _ = ProfileEditor(master=self.parent)

    def editProfile(self):
        EditorSelector(master=self.parent, mode=0)

    def delProfile(self):
        EditorSelector(master=self.parent, mode=1)


class EditorSelector(tk.Toplevel):
    def __init__(self, master=None, mode: int = -1):
        super().__init__(master=master)
        mainLabel = None
        # self.tooltip = tooltip.Balloon(master)
        match mode:
            case 0:  # Select to edit mode
                mainLabel = tk.Label(self, text="Select Profile to edit.")

            case 1:  # Select to delete
                mainLabel = tk.Label(self, text="Select Profile to delete")
                # self.tooltip.bind(mainLabel, "Warning!\nThis will delete the profile from the config file.\nThis is permanent!")
                pass
            case _:
                popupBox.showerror(
                    "Error!", f"EditorSelector class initialized with the invalid mode {mode}.")
                self.destroy()
        self.mode = mode

        mainLabel.pack(padx=5, pady=2)

        self.config = cfg.get_config()
        profileList = cfg.get_profiles(self.config)
        for profile in profileList:
            profile: Profile
            uuid = profile.uuid
            if mode == 0:
                btn = tk.Button(self, text=profile.profileName,
                                command=lambda: self.editProfile(uuid))
                # self.tooltip.bind(btn, f"Profile UUID:\n{uuid}")
                btn.pack(padx=3, pady=4)
            if mode == 1:
                btn = tk.Button(self, text=profile.profileName,
                                command=lambda: self.delProfile(uuid))
                # self.tooltip.bind(btn, f"Profile UUID:\n{uuid}")
                btn.pack(padx=3, pady=4)

    def delProfile(self, uuid):
        cfg.del_profile_uuid(self.config, uuid)
        pass

    def editProfile(self, uuid):
        pass


class ProfileEditor(tk.Toplevel):
    """Explanation:
            We create a non-resizable window, with the option to pass in a profile.
                if we pass a profile, get data from profile like requests and name, for later use
                if no profile was passed in, make a new one.

            then with self.profile, make a label using the profile name, another listing the number of profiles 
                and which request you are currently editing.

            So for each request in self.profile, prep tkinter widgets and add the tkinter variable/widget pairs
                to tkRequestItems list in a dictionary. I did this due to tkinter not supporting default variable
                classes provided by python.

            I made a "betterGrid" function because i just feel like its more flexible unlike the grid provided
                in tkinter.


    """

    def __init__(self, master=None, profile: Profile = None):
        self.profile = profile

        super().__init__(master=master)
        self.title("Profile Creator")
        self.width = 600
        self.height = 400
        self.minsize(self.width, self.height)
        self.resizable(0, 0)
        self.mult = 35

        self.tkRequestItems = []
        self.currentRequest = 0

        self.profile = profile
        if not self.profile:
            self.profile = Profile(fromDict={})

        self.profileName = tk.StringVar(self, self.profile .profileName)
        self.requests = self.profile.requests

        for reqIndex, request in enumerate(self.requests):
            self.tkRequestItems.append({"uri": tk.StringVar(
                self, request.uri), "reqtype": tk.StringVar(self, request.reqtype.upper())})
            self.tkRequestItems[reqIndex]["Entry"] = tk.Entry(
                self, textvariable=self.tkRequestItems[reqIndex]["uri"], width=45)
            self.tkRequestItems[reqIndex]["reuseSession"] = tk.IntVar(
                self, value=int(request.reuseSession))
            self.tkRequestItems[reqIndex]["ReuseBox"] = tk.Checkbutton(
                self, text='Reuse Session', variable=self.tkRequestItems[reqIndex]["reuseSession"], onvalue=1, offvalue=0)

        self.nameLabel = tk.Label(self, text="Profile Name:")
        self.nameEntry = tk.Entry(
            self, textvariable=self.profileName, width=40)
        self.currentRequestLabel = tk.Label(
            self, text=f"Viewing Request: {self.currentRequest + 1}/{len(self.requests)}")

        # Request part
        self.requestUriLabel = tk.Label(self, text="Request Uri:")
        self.requestMethodDropdown = [tk.OptionMenu(
            self, self.tkRequestItems[0]["reqtype"], *("GET", "HEAD", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"))]

        self.prevRequestbtn = tk.Button(
            self, text="Previous Request", command=lambda: self.prevReq(True))
        self.newRequestbtn = tk.Button(
            self, text="New Request", command=lambda: self.CreateRequest(True))
        self.nextRequestbtn = tk.Button(
            self, text="Next Request", command=lambda: self.nextReq(True))
        self.saveProfilebtn = tk.Button(
            self, text="Save Profile", command=lambda: self.saveProfile())
        self.redrawAll()

    def saveProfile(self):
        self.profile.profileName = self.profileName.get()
        for tkReqIndex, tkItemDict in enumerate(self.tkRequestItems):
            self.requests[tkReqIndex].uri = tkItemDict["uri"].get()
            self.requests[tkReqIndex].reqtype = tkItemDict["reqtype"].get()
            self.requests[tkReqIndex].reuseSession = bool(
                tkItemDict["reuseSession"].get())
            # self.requests[tkReqIndex].uri = tkItemDict["uri"].get()
            # self.requests[tkReqIndex].headers = tkItemDict["headers"].get()
        cfg.add_profile(cfg.get_config(), self.profile)

        # Cleanup properly?
        del self.profile
        del self.requests
        del self.tkRequestItems
        gc.collect()
        self.destroy()

    def clearScreen(self):
        for widget in self.winfo_children():
            widget.place_forget()

    def upperWidgets(self, redraw=False):
        self.currentRequestLabel.config(
            text=f"Viewing Request: {self.currentRequest + 1}/{len(self.requests)}")
        self.betterGrid(self.nameLabel, x=0.5, y=0.5)
        self.betterGrid(self.nameEntry, x=3, y=0.5)
        self.betterGrid(self.currentRequestLabel, x=12.5, y=0.5)

        if redraw:
            self.redrawAll()

    def bottomWidgets(self, redraw=False):
        if len(self.tkRequestItems) > 1:
            self.betterGrid(self.prevRequestbtn, x=3, y=9.3)
            self.betterGrid(self.nextRequestbtn, x=10.3, y=9.3)
        self.betterGrid(self.newRequestbtn, x=7, y=9.3)
        self.betterGrid(self.saveProfilebtn, x=7.1, y=10.4)
        if redraw:
            self.redrawAll()

    def showRequestWidgets(self, redraw=False):
        self.betterGrid(self.requestUriLabel, x=0.5, y=2)
        self.betterGrid(
            self.tkRequestItems[self.currentRequest]["Entry"], x=3, y=2)
        self.betterGrid(
            self.requestMethodDropdown[self.currentRequest], x=14, y=1.90)
        self.betterGrid(
            self.tkRequestItems[self.currentRequest]["ReuseBox"], x=2, y=3)
        self.betterGrid(
            self.requestMethodDropdown[self.currentRequest], x=14, y=4)
        if redraw:
            self.redrawAll()

    def prevReq(self, redraw=False):
        if len(self.tkRequestItems) > 1:
            if self.currentRequest == 0:
                self.currentRequest = len(self.tkRequestItems) - 1
            else:
                self.currentRequest -= 1
            if redraw:
                self.redrawAll()

    def nextReq(self, redraw=False):
        if len(self.tkRequestItems) > 1:
            if self.currentRequest == len(self.tkRequestItems) - 1:
                self.currentRequest = 0
            else:
                self.currentRequest += 1
            if redraw:
                self.redrawAll()

    def CreateRequest(self, redraw=False):
        newReq = Request()
        self.requests.append(newReq)
        self.tkRequestItems.append({"uri": tk.StringVar(
            self, newReq.uri), "reqtype": tk.StringVar(self, newReq.reqtype.upper())})
        self.tkRequestItems[len(self.tkRequestItems) - 1]["Entry"] = tk.Entry(
            self, textvariable=self.tkRequestItems[len(self.tkRequestItems) - 1]["uri"], width=45)
        self.requestMethodDropdown.append(tk.OptionMenu(self, self.tkRequestItems[len(
            self.tkRequestItems) - 1]["reqtype"], *("GET", "HEAD", "POST", "PATCH", "PUT", "DELETE", "OPTIONS")))
        self.tkRequestItems[len(
            self.tkRequestItems) - 1]["reuseSession"] = tk.IntVar(value=int(newReq.reuseSession))
        self.tkRequestItems[len(self.tkRequestItems) - 1]["ReuseBox"] = tk.Checkbutton(self, text='Reuse Session',
                                                                                       variable=self.tkRequestItems[len(self.tkRequestItems) - 1]["reuseSession"], onvalue=1, offvalue=0)
        if redraw:
            self.redrawAll()

    def redrawAll(self):
        self.clearScreen()
        self.upperWidgets()
        self.showRequestWidgets()
        self.bottomWidgets()

    def betterGrid(self, widget: tk.Widget, x: int, y: int):
        self.mult = self.mult // 1
        x = (x * self.mult) // 1
        y = (y * self.mult) // 1
        if y >= self.height:
            y = self.height - self.mult
        if x >= self.width:
            x = self.width - self.mult
        widget.place(x=x, y=y)


#  TODO Parse Progress Data
class SelectorFrame(tk.Frame):
    def __init__(self, frameContainer, FrameController):
        """ 
            Creates a button for each Profile using Profile.profileName as Button Text.
            If request function sends progress of a Profile, button should block with possible addition of a progress bar.
        """
        tk.Frame.__init__(self, frameContainer)
        self.frameController = FrameController
        config = cfg.get_config()
        profiles = config.profiles
        stateReceiver: Connection = FrameController.stateReceiver
        stateSender: Connection = FrameController.stateSender
        self.profileButtons = {}
        if len(profiles) > 0:
            ProfilesLabel = tk.Label(self, text="Run profiles:")
            ProfilesLabel.pack(pady=10, padx=10)
            for profile in profiles:
                if "delMode" in vars(FrameController).keys():
                    button = tk.Button(self, text=profile.profileName,
                                       command=lambda: self.deleteProfile(config, profile, FrameController))
                else:
                    button = tk.Button(self, text=profile.profileName,
                                       command=lambda profFromButton=profile: DataEntry(profile=profFromButton, taskQueue=FrameController.taskQueue, stateSender=stateSender))
                self.profileButtons.update({profile.uuid: button})
                button.pack(padx=10, pady=10)
        else:
            ProfilesLabel = tk.Label(
                self, text="Error: No profiles in config file.")
            ProfilesLabel.pack(pady=10, padx=10)

        if stateSender and stateReceiver:
            self.disabledButtons: list[str] = []
            self.after_idle(self.stateListener, stateReceiver)

    def deleteProfile(self, config, profile, controller):
        cfg.del_profile(config, profile)
        del controller.delMode
        self.destroy()

    def stateListener(self, stateReceiver: Connection):
        """
            If blockedButtons contains a button, grey it out, then re-add check to tkinter's idle loop.
            stateReceiver.recv() blocks, so if stateReceiver contains any data, stateReceiver.recv()
            then parse which Profile should be blocked.
            Add said button to sef.blockedButtons.

            Poll progress Pipe with timeout of 0.3 seconds
        """
        data = ""
        if stateReceiver.poll(0.3):
            data = stateReceiver.recv()
        if data != "":
            print(data)
            data: str
            uuidMatcher = re.match(
                r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}):\s(([+-]?)\s*(?:(?:(?:[^.]?(\d+))|(\d+\.\d+(?!\w+)))(?!\w+|\.))(?![([{]))", data)
            if len(uuidMatcher.groups()) >= 2:
                uuid = uuidMatcher.group(1)
                prog = float(uuidMatcher.group(2)) # Convert str to float

                if prog >= 100:
                    self.disabledButtons.remove(uuid)
                else:
                    if uuid not in self.disabledButtons:
                        self.disabledButtons.append(uuid)

        for uuid, button in self.profileButtons.items():
            button: tk.Button
            button["state"] = tk.DISABLED if uuid in self.disabledButtons else tk.NORMAL
               
        if self.frameController.activeFrame and self.frameController.activeFrame.lower() == self._name.removeprefix("!"):
            self.after(1500, self.stateListener, stateReceiver)


class CreditsFrame(tk.Frame):
    def __init__(self, frameContainer, FrameController):
        """ 
            Credits screen to display credits and extra info
        """
        tk.Frame.__init__(self, frameContainer)
        self.frameController = FrameController

        labels = []
        for dev in DevDetails:
            nameLabel = tk.Label(
                self, text=f"Developer: {dev.get('username', '')} {dev.get('name', '')}")
            ghLabel = tk.Label(
                self, text=f"Github: {dev.get('github', 'None Provided')}")
            emailLabel = tk.Label(
                self, text=f"Email: {dev.get('email', 'None Provided')}")

            if 'github' in dev.keys():
                ghLabel.bind("<Button-1>", lambda x: open_url(dev['github']))
            if 'email' in dev.keys():
                ghLabel.bind("<Button-1>", lambda x: open_url(dev['email']))

            labels.append(nameLabel)
            labels.append(ghLabel)
            labels.append(emailLabel)

        projGithubLabel = tk.Label(
            self, text=f"Project Github: {ProjDetails['github']}")
        projVersionLabel = tk.Label(
            self, text=f"Current Version: {ProjDetails['version']}")

        projGithubLabel.bind(
            "<Button-1>", lambda x: open_url(ProjDetails['github']))
        projVersionLabel.bind(
            "<Button-1>", lambda x: self.checkUpdate(projVersionLabel))

        labels.append(projGithubLabel)
        labels.append(projVersionLabel)
        for label in labels:
            label: tk.Widget
            label.pack()

    # TODO: make an update checker
    def checkUpdate(self, label):
        label: tk.Button
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            localSHA = repo.head.commit.hexsha
            remoteSHA = repo.remote("origin").refs.main.commit.hexsha
            if localSHA == remoteSHA:
                label['text'] = f"Current Version: Up-To-Date, {ProjDetails['version']}"
            else:
                label['text'] = f"Current Version: Outdated\nlocal: {localSHA}\norigin: {remoteSHA}"

        except ImportError as e:
            label['text'] = "Please run: 'pip install gitpython' in venv/console"


# God I love StackOverflow
Frames = (EditorFrame, SelectorFrame, CreditsFrame)


class FrameController(tk.Tk):

    def __init__(self, launchParams: dict, taskQueue: mp.JoinableQueue, stateReceiver: Connection, stateSender: Connection, *args, **kwargs):

        tk.Tk.__init__(
            self, className=' Fortnine Request Templates', *args, **kwargs)
        self.container = tk.Frame(self)
        self.taskQueue: mp.JoinableQueue = taskQueue
        self.stateReceiver = stateReceiver
        self.stateSender = stateSender

        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.activeFrame = None
        self.makeFrames()

        # GUI Parameters, edit at Start of file
        match launchParams.items():
            case "openEditor", True:
                self.show_frame(EditorFrame)
            case "openEditor", False:
                self.show_frame(SelectorFrame)

        if not self.activeFrame:
            self.show_frame(SelectorFrame)

        self.__dict__.update(launchParams)
        # self.after(5000, printReceived, args=(stateReceiver)

    def show_frame(self, frame, refreshFrame=False):
        self.activeFrame = str(frame.__name__).lower()
        if refreshFrame:
            self.refreshFrame(frame)
        frame = self.frames[frame]
        frame.tkraise()

    def makeFrames(self):
        # Here F in Each FrameClass e.g. EditorFrame, SelectorFrame
        for F in Frames:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def refreshFrame(self, frame):
        for F in Frames:
            if isinstance(F, frame):
                # Clear leftover vars and start fresh
                del self.frames[F]
                del frame
                frame = F(self.container, self)
                self.frames[F] = frame
                frame.grid(row=0, column=0, sticky="nsew")


class DataEntry(tk.Toplevel):
    def __init__(self, taskQueue, master=None, profile: Profile = None, stateSender=None):
        # TODO add drag and drop to facilitate Inputing CSV data
        """Create Data Entry window to paste in csv data then send request to AsyncExecPool.
            Can handle multiple requests, each request hosting a page with an Input Field

        Args:
            taskQueue (JoinableQueue): Task Queue to send Requests to.
            master (tk.Window?, optional): Master window that spawned frame. Defaults to None.
            requests (list, optional): Requests list taken from Profile.requests. Defaults to [].
        """
        super().__init__(master=master)
        
        assert isinstance(profile, Profile)
        
        self.resizable(0,0)
        self.title("Input Request variables")
        self.profile = profile
        self.requests = profile.requests
        self.CurrentInput = 1
        self.InputFields = []
        self.taskQueue: mp.JoinableQueue = taskQueue
        self.stateSender = stateSender

        self.profLabel = tk.Label(
            self, text=f"Profile Name: {self.profile.profileName}\t UUID: {self.profile.uuid}")
        
        # Prepares InputFields of all requests in profile
        for i in self.requests:
            input = tkscrolled.ScrolledText(self)
            self.InputFields.append(input)
            
        # Labels for drawLabels() 
        self.ReqPreviewLabel = tk.Label(
            self, text=f"Preview: {self.requests[self.CurrentInput - 1].uri}")
        self.ReqMethodLabel = tk.Label(
            self, text=f"Method: {self.requests[self.CurrentInput - 1].reqtype.upper()}")
        
        # Buttons for drawButtons()
        self.NextBtn = tk.Button(
            self, text="Next Request", command=lambda: self.ShowNextField())
        self.PrevBtn = tk.Button(
            self, text="Previous Request", command=lambda: self.ShowPrevField())
        self.makeReqBtn = tk.Button(
            self, text="Make Request", command=lambda: self.SendRequest(self.requests, uuid=self.profile.uuid))
        
        self.drawLabels()
        if len(self.InputFields) >= 1:
            self.drawInputField()
        self.drawButtons()
        self.sizes()
        



# .grid() cleared labels to begining of DataEntry screen.

    def drawLabels(self):
        self.profLabel.grid(padx=10, pady=10, sticky="new", columnspan=5)
        self.ReqPreviewLabel.configure(
            {"text": f"Preview: {self.requests[self.CurrentInput - 1].uri}"})

        self.ReqMethodLabel.configure(
            {"text": f"Method: {self.requests[self.CurrentInput - 1].reqtype.upper()}"})
        self.ReqPreviewLabel.grid(padx=10, row=1, rowspan=1)
        self.ReqMethodLabel.grid(padx=10, row=1, rowspan=1, column=1)

# .grid() cleared buttons to end of DataEntry screen.

    def drawButtons(self):
        if len(self.InputFields) > 1:
            if self.CurrentInput != 1:
                self.PrevBtn.grid(padx=5, row=7, pady=5, columnspan=1)

            if self.CurrentInput != len(self.InputFields):
                self.NextBtn.grid(padx=5, row=7, pady=5, column=3, columnspan=1)
                
        self.makeReqBtn.grid(padx=5, row=7, pady=5, column=2, columnspan=1)
        

# .grid() InputField from self.CurrentInput
# To facilitate changing GUI placement

    def drawInputField(self):
        self.InputFields[self.CurrentInput - 1].grid(row=2, rowspan=4, columnspan=10) 


# Clears DataEntry screen and displays entry fields for the next request.
    def ShowNextField(self):
        self.clear()
        self.CurrentInput += 1
        self.drawLabels()
        self.drawInputField()
        self.drawButtons()
        self.sizes()

# Clears DataEntry screen and displays entry fields for the Previous request.
    def ShowPrevField(self):
        self.CurrentInput -= 1
        self.clear()
        self.drawLabels()
        self.drawInputField()
        self.drawButtons()
        self.sizes()
        
    def sizes(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.geometry()

# Get Input of every Request, parse data, then send a requestTask with requests, FieldsData and stateSender to TaskQueue.
    def SendRequest(self, requests: List[Request], uuid: str):
        FieldsData = []
        for InputField in self.InputFields:
            fieldText: str = InputField.get('1.0', tk.END)
            FieldsData.append(parseCSV(fieldText))

        reqsTask = proc.TaskThread(
            fun=MakeRequests, args=(requests, FieldsData, uuid, self.stateSender, ))
        self.taskQueue.put(reqsTask)

        self.destroy()

    def clear(self):
        for widget in self.winfo_children():
            widget.grid_forget()
