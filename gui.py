import tkinter as tk
import tkinter.scrolledtext as tkscrolled, tkinter.messagebox as popupBox
import gc
# import Pmw.Pmw_2_0_1.lib.PmwBalloon as tooltip

# Used for typing
import multiprocessing as mp
from multiprocessing.connection import Connection
from typing import List
import utils.parallelProcessing as proc

from objects import Profile, Request
from utils.general import parseCSV
from utils.requests import MakeRequests
import utils.config as cfg

# Initialize the GUI then start FrameController with minimum size.
# Finally run main tkinter's mainloop()
def startGUI(launchParams, taskQueue: mp.JoinableQueue,  stateReceiver: Connection, stateSender: Connection, master: bool):
    def key(x):
        # Ctrl + = (Equals key) switches to Selector Window
        # Ctrl + - (Minus Key) switches to Editor Frame
        if x.state == 4:
            if x.keysym.lower() == 'equal':
                master.show_frame(SelectorFrame)
            if x.keysym.lower() == 'minus':
                master.show_frame(EditorFrame)
        
        

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

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        label = tk.Label(self, text="Editor Mode")
        label.pack(pady=10, padx=10)

        switchbtn = tk.Button(self, text="Switch to User Mode",
                              command=lambda: controller.show_frame(SelectorFrame))
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
                case 0: # Select to edit mode
                    mainLabel = tk.Label(self, text="Select Profile to edit.")
                    
                case 1: # Select to delete
                    mainLabel = tk.Label(self, text="Select Profile to delete")
                    # self.tooltip.bind(mainLabel, "Warning!\nThis will delete the profile from the config file.\nThis is permanent!")
                    pass
                case _:
                    popupBox.showerror("Error!", f"EditorSelector class initialized with the invalid mode {mode}.")
                    self.destroy()
            self.mode = mode
            
            mainLabel.pack(padx=5, pady=2)
            
            self.config = cfg.get_config()
            profileList = cfg.get_profiles()
            for profile in profileList:
                profile: Profile
                uuid = profile.uuid
                if mode == 0:
                    btn = tk.Button(self, text=profile.profileName, command=lambda: self.editProfile(uuid))
                    # self.tooltip.bind(btn, f"Profile UUID:\n{uuid}")
                    btn.pack(padx=3,pady=4)
                if mode == 1:
                    btn = tk.Button(self, text=profile.profileName, command=lambda: self.delProfile(uuid))
                    # self.tooltip.bind(btn, f"Profile UUID:\n{uuid}")
                    btn.pack(padx=3,pady=4)
                    
        
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
            self.profile = Profile()
            
            
        self.profileName = tk.StringVar(self, self.profile .profileName)
        self.requests = self.profile.requests
        
        for reqIndex, request in enumerate(self.requests):
            self.tkRequestItems.append({"uri": tk.StringVar(
                self, request.uri), "reqtype": tk.StringVar(self, request.reqtype.upper())})
            self.tkRequestItems[reqIndex]["Entry"] = tk.Entry(
                self, textvariable=self.tkRequestItems[reqIndex]["uri"], width=45)
            self.tkRequestItems[reqIndex]["reuseSession"] = tk.IntVar(self, value=int(request.reuseSession))
            self.tkRequestItems[reqIndex]["ReuseBox"] = tk.Checkbutton(self, text='Reuse Session',variable=self.tkRequestItems[reqIndex]["reuseSession"], onvalue=1, offvalue=0)

        
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
            self.requests[tkReqIndex].reuseSession = bool(tkItemDict["reuseSession"].get())
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
        self.betterGrid(self.tkRequestItems[self.currentRequest]["Entry"], x=3, y=2)
        self.betterGrid(self.requestMethodDropdown[self.currentRequest], x=14, y=1.90)
        self.betterGrid(self.tkRequestItems[self.currentRequest]["ReuseBox"], x=2, y=3)
        self.betterGrid(self.requestMethodDropdown[self.currentRequest], x=14, y=4)
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
        self.tkRequestItems[len(self.tkRequestItems) - 1]["reuseSession"] = tk.IntVar(value=int(newReq.reuseSession))
        self.tkRequestItems[len(self.tkRequestItems) - 1]["ReuseBox"] = tk.Checkbutton(self, text='Reuse Session',variable=self.tkRequestItems[len(self.tkRequestItems) - 1]["reuseSession"], onvalue=1, offvalue=0)
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
    def __init__(self, parent, controller):
        """ 
            Creates a button for each Profile using Profile.profileName as Button Text.
            If request function sends progress of a Profile, button should block with possible addition of a progress bar.
        """
        tk.Frame.__init__(self, parent)

        config = cfg.get_config()
        profiles = config.profiles
        stateReceiver: Connection = controller.stateReceiver
        stateSender: Connection = controller.stateSender
        self.profileButtons = []
        if len(profiles) > 0:
            ProfilesLabel = tk.Label(self, text="Run profiles:")
            ProfilesLabel.pack(pady=10, padx=10)
            for profile in profiles:
                if "delMode" in vars(controller).keys():
                    button = tk.Button(self, text=profile.profileName,
                                   command=lambda: self.deleteProfile(config, profile, controller))
                else:
                    button = tk.Button(self, text=profile.profileName,
                                   command=lambda: DataEntry(profile=profile, taskQueue=controller.taskQueue, stateSender=stateSender))
                self.profileButtons.append(button)
                button.pack(padx=10, pady=10)
        else:
            ProfilesLabel = tk.Label(
                self, text="Error: No profiles in config file.")
            ProfilesLabel.pack(pady=10, padx=10)

        if stateSender and stateReceiver:
            self.disabledButtons: list[tk.Button] = []
            self.after_idle(self.checkInactiveButtons, stateReceiver)
            
    def deleteProfile(self, config, profile, controller):
        cfg.del_profile(config, profile)
        del controller.delMode
        self.destroy()

    # TODO Understand what button is being run, then add it to self.blockedButtons
    def checkInactiveButtons(self, stateReceiver: Connection):
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

        for button in self.profileButtons:
            if button in self.disabledButtons:
                button.setvar("state", "disabled")
            else:
                button.setvar("state", "normal")
        self.after(1500, self.checkInactiveButtons, stateReceiver)


# God I love StackOverflow
Screens = (EditorFrame, SelectorFrame)


class FrameController(tk.Tk):

    def __init__(self, launchParams: dict, taskQueue: mp.JoinableQueue, stateReceiver: Connection, stateSender: Connection, *args, **kwargs):

        tk.Tk.__init__(
            self, className='Fortnine Request Templates', *args, **kwargs)
        container = tk.Frame(self)
        self.taskQueue: mp.JoinableQueue = taskQueue
        self.stateReceiver = stateReceiver
        self.stateSender = stateSender

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
            
            self.__dict__.update(launchParams)
                # self.after(5000, printReceived, args=(stateReceiver)

    def show_frame(self, frame):
        frame = self.frames[frame]
        frame.tkraise()


class DataEntry(tk.Toplevel):
    def __init__(self, taskQueue, master=None, profile: Profile= None, stateSender=None):
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
        self.title("Input Request variables")
        self.profile = profile
        self.requests = profile.requests
        self.CurrentInput = 1
        self.InputFields = []
        self.taskQueue: mp.JoinableQueue = taskQueue
        self.stateSender = stateSender

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
            self, text="Make Request", command=lambda: self.SendRequest(self.requests, uuid=self.profile.uuid))
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