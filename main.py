from threading import current_thread
import multiprocessing as mp
import logging
import time
import argparse

from constants import *
from utils.general import getOverrides
from gui import startGUI
import utils.parallelProcessing as proc

Processes = {}


def main():
    current_thread().name = "Main Thread/Program Exit Handler"
    taskQueue = mp.JoinableQueue()

    try:
        Processes["TaskQueue"] = taskQueue
        stateSender, stateReceiver = mp.Pipe()

        GUIProc = mp.Process(target=startGUI, name="GUI", args=(
            GlobalLaunchParams.get("GUI", {}), taskQueue, stateReceiver, stateSender, True))
        GUIProc.start()
        Processes["GUI"] = GUIProc

        AsyncExecPool = proc.AsyncParallel()
        Processes["AsyncExecPool"] = AsyncExecPool
        proc.runPatientThread(AsyncExecPool, taskQueue, stateSender)

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
    # Intercept ctrl+c and end program gracefully
    except KeyboardInterrupt:
        """
            1. Send taskQueue End Signal
            2. Kill GUI proc
            3. block until is_alive is false
            4. Flush GUI recources using .close()
        """
        logging.warning(
            "Received KeyboardInterrupt, attempting to end Program gracefully")

        taskQueue.put(proc._QueueEndSignal())
        logging.warning("QueueEndSignal sent to taskQueue")

        try:
            logging.warning("Trying to kill GUI proc")
            Processes["GUI"].kill()

            while(Processes["GUI"].is_alive()):
                time.sleep(0.1)
                logging.warning(
                    "Blocked for (an additional?) 500 milliseconds to wait for program to be killed.")
            logging.warning(
                "GUI proc killed, attempting to release any recources held by GUI process.")

            Processes["GUI"].close()
            logging.warning(
                "GUI proc recources flushed gracefully.\n\tProceeding with normal exit procedure.")
        except Exception as e:
            logging.error(e)
            logging.error("Error occured while killing/cleaning GUI proc!")
            logging.error(
                "Please use TaskManager to make sure all python processes belonging to\n\tthe templater are closed!!")
            logging.error(
                "This is important as unkilled processed will take up open ports and system recources!!!")


def makeLogger(type: str):
    match type.lower():
        case "debug":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=f"templater-{dayDate}.log", level=logging.DEBUG)
        case "info":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=f"templater-{dayDate}.log", level=logging.INFO)
        case "critical":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=f"templater-{dayDate}.log", level=logging.CRITICAL)
        case "error":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=f"templater-{dayDate}.log", level=logging.ERROR)
        case "fatal":
            logging.basicConfig(format="%(levelname)s: %(module)s:  %(message)s",
                                filename=f"templater-{dayDate}.log", level=logging.FATAL)

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


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Request profile creater/manager made for  Fortnine.ca (Boutique Linus Inc.)')
    # parser.add_argument('editor', metavar='N', type=int, nargs='+',
    #                 help='an integer for the accumulator')
    try:
        # Have no idea why checked value exists but im pretty sure its needed at a certain point
        checked = False
        _ov = getOverrides(OverridesFolder)
        checked = True
        
        if isinstance(_ov, str):
            makeLogger("info")
            logging.error(_ov)
        
        # If DEBUG file found in overrides folder, enable debug logging
        if _ov is not None and "debug" in _ov:
            makeLogger("debug")
            logging.debug("Attention: Logger started in logging.DEBUG mode")
        else:
            makeLogger("info")

    except Exception as e:
        makeLogger("info")
        logging.error(
            "Error occured while getting overrides, defaulting to logging.INFO, Stack trace will follow:")
        logging.exception(e)

    logging.info('Starting up Templater')
    logging.debug(
        f"Launched with following parameters: \n{GlobalLaunchParams}")

    main()

    logging.debug('All sub-processes dead, program ending.')
