import json
from utils.general import getOverrides, logger_ml, makeLogger, basic_multiline_banner
from threading import current_thread
from gui import startGUI
from constants import *

import utils.parallelProcessing as proc
import multiprocessing as mp
import logging
import time

Processes = {}


def main():
    global logger
    current_thread().name = "Main Thread"
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
                        logger.debug(f"Joined Process {name}.")

                taskQueue.put(proc._QueueEndSignal())
                logger.debug("Sent TaskQueue End Signal.")

                if stateSender or stateReceiver:
                    stateSender.close()
                    stateReceiver.close()
                    logger.debug("Closed Progress Pipes.")
                break
        logger.debug('All sub-processes dead, logger shuting down.')
        logger_ml(logger, basic_multiline_banner("Templater Closing") + "\n")
        logging.shutdown()
    # Intercept ctrl+c and end program gracefully
    except KeyboardInterrupt:
        """
            1. Send taskQueue End Signal
            2. Kill GUI proc
            3. block until is_alive is false
            4. Flush GUI resources using .close()
        """
        logger.info(
            "Received KeyboardInterrupt, attempting to end Program gracefully")

        taskQueue.put(proc._QueueEndSignal())
        logger.debug("QueueEndSignal sent to taskQueue")

        try:
            logger.debug("Trying to kill GUI proc")
            Processes["GUI"].kill()

            while(Processes["GUI"].is_alive()):
                time.sleep(0.25)

                logger.debug(
                    "Blocked 250 milliseconds to wait for program to be killed.")
            logger.debug(
                "GUI proc killed, attempting to release any resources held by GUI process.")

            Processes["GUI"].close()
            logger.warn(
                "GUI proc resources flushed gracefully; Proceeding with normal exit procedure.")
        except Exception as e:
            logger.exception(e)
            logger.error("Error occurred while killing/cleaning GUI proc!")
            logger.warn(
                "Please use TaskManager to make sure all python processes belonging to\n\tthe templater are closed!!")
            logger.warn(
                "This is important as un-killed processed will take up open ports and system resources!")


if __name__ == '__main__':

    # parser = argparse.ArgumentParser(description='Request profile creator/manager made for  Fortnine.ca (Boutique Linus Inc.)')
    # parser.add_argument('editor', metavar='N', type=int, nargs='+',
    #                 help='an integer for the accumulator')

    params = GlobalLaunchParams

    try:

        # If DEBUG file found in overrides folder, enable debug logging
        for override in getOverrides(OverridesFolder):
            match override.casefold():
                case "debug":
                    params["logging_level"] = override.casefold()
                case _:
                    # Add more overrides
                    pass

        makeLogger(params["logging_level"]
                   if params["logging_level"] else "info")

        logger = logging.getLogger("Main")

    except Exception as e:
        makeLogger(None)
        logging.error(
            "Following error raised while getting overrides, defaulting to logging.INFO:")
        logging.exception(e)
        print(e.with_traceback())

    for line in basic_multiline_banner("Starting up Templater").splitlines():
        logger.info(line)
    logger.debug("Launched with following parameters:")
    logger_ml(logger=logger, textLines=json.dumps(GlobalLaunchParams,
              indent=2).splitlines())

    main()
