import logging
from threading import current_thread
import multiprocessing as mp
import time
import argparse

from constants import *
from utils.general import getOverrides, makeLogger
from gui import startGUI
import utils.parallelProcessing as proc

Processes = {}


def main():
    global logger
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
                        logger.info(f"Joined Process {name}.")

                taskQueue.put(proc._QueueEndSignal())
                logger.info("Sent TaskQueue End Signal.")

                if stateSender or stateReceiver:
                    stateSender.close()
                    stateReceiver.close()
                    logger.info("Closed Progress Pipes")
                break
        logger.info("Ending program. Good night ;p")
        logging.shutdown()
    # Intercept ctrl+c and end program gracefully
    except KeyboardInterrupt:
        """
            1. Send taskQueue End Signal
            2. Kill GUI proc
            3. block until is_alive is false
            4. Flush GUI resources using .close()
        """
        logger.warning(
            "Received KeyboardInterrupt, attempting to end Program gracefully")

        taskQueue.put(proc._QueueEndSignal())
        logger.warning("QueueEndSignal sent to taskQueue")

        try:
            logger.warning("Trying to kill GUI proc")
            Processes["GUI"].kill()

            while(Processes["GUI"].is_alive()):
                time.sleep(0.1)
                logger.warning(
                    "Blocked for (an additional?) 500 milliseconds to wait for program to be killed.")
            logger.warning(
                "GUI proc killed, attempting to release any resources held by GUI process.")

            Processes["GUI"].close()
            logger.warning(
                "GUI proc resources flushed gracefully; Proceeding with normal exit procedure.")
        except Exception as e:
            logger.error(e)
            logger.error("Error occurred while killing/cleaning GUI proc!")
            logger.error(
                "Please use TaskManager to make sure all python processes belonging to\n\tthe templater are closed!!")
            logger.error(
                "This is important as un-killed processed will take up open ports and system resources!!!")

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
    # parser = argparse.ArgumentParser(description='Request profile creator/manager made for  Fortnine.ca (Boutique Linus Inc.)')
    # parser.add_argument('editor', metavar='N', type=int, nargs='+',
    #                 help='an integer for the accumulator')
    try:
        _ov = getOverrides(OverridesFolder)

        # If DEBUG file found in overrides folder, enable debug logging
        if _ov and "debug" in _ov:
            makeLogger("debug")
            logging.debug("Attention: Logger started in logging.DEBUG mode")
        else:
            makeLogger("info")

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger("main")

        ch = logging.StreamHandler()
        ch.setLevel(logger.level)
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    except Exception as e:
        makeLogger("info")
        logging.error(
            "Following error raised while getting overrides, defaulting to logging.INFO:")
        logging.exception(e)

    logger.info('Starting up Templater')
    logger.debug(
        f"Launched with following parameters: \n{GlobalLaunchParams}")

    main()

    logger.debug('All sub-processes dead, program ending.')
