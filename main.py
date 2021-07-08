from datetime import date
import logging

import multiprocessing as mp

from gui import startGUI
from utils.general import getOverrides
import utils.parallelProcessing as proc


today = date.today()
dayDate = today.strftime("%d-%m-%Y")

# Settings
_ov = getOverrides()
GlobalLaunchParams = {
    "GUI": {
        "openEditor": True
    }
}





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
    Then using stateSender/Receiver and TaskQueue run "PatientThread"; Infinitely loops \
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
    stateSender, stateReceiver = mp.Pipe()
    Processes["TaskQueue"] = taskQueue

    GUIProc = mp.Process(target=startGUI, name="GUI", args=(
        GlobalLaunchParams.get("GUI", {}), taskQueue, stateReceiver, stateSender, True))
    GUIProc.start()
    Processes["GUI"] = GUIProc

    RequestExecPool = proc.AsyncParallel()
    Processes["ReqExecPool"] = RequestExecPool
    proc.runPatientThread(RequestExecPool, taskQueue, stateSender)

    while(Processes):
        if not Processes["GUI"].is_alive():
            for name, thread in Processes.items():
                if name != "GUI":
                    thread.join()
                    logging.info(f"Joined Process {name}.")

            taskQueue.put(proc._QueueEndSignal())
            logging.info("Sent TaskQueue End Signal.")

            if stateSender or stateReceiver:
                stateSender.close()
                stateReceiver.close()
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
