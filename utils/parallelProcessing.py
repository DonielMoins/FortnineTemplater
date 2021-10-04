from utils.general import randomHex
from enum import Enum

import multiprocessing as mp
import threading as th
import traceback
import logging


class TaskTypes(Enum):
    QUEUE_END_SIGNAL = -1
    NORMAL = 0


class TaskThread:
    def __init__(self, fun=None, args=None, identifier=None, tasktype: TaskTypes = TaskTypes.NORMAL):
        """Defines one function and its arguments to be executed in one thread.

        Attention, never use "_QueueEndSignal" as identifier unless you want to end the Queue.

        Args:
                        fun (function): a function to be executed
                        args (tuple): arguments of the function
                        identifier (optional[str, None]): Task identifier string, If no value is provided, generates ID using func name and random 5 digit hex.
        """

        if not identifier:
            self.identifier = fun.__name__ + randomHex(len=5)
        else:
            self.identifier = identifier
        if not fun:
            if identifier != "_QueueEndSignal" or tasktype != TaskTypes.QUEUE_END_SIGNAL:
                raise ValueError(
                    f"fun must be a reference to a function and not {type(fun)}")
        else:
            self.fun = fun
            self.args = args
            # self.args = args[:2] + (self.identifier, ) + args[2:]


class TaskCmd:
    def __init__(self, cmd, cwd='.', stdin=None, stdout=None, stderr=None):
        """Defines one task to be executed as a command line command.

        Args:
                        cmd ([str]): Command to be executed on a command line
                        cwd (str, optional): Current working directory in which the task will be executed. Defaults to '.'.
                        stdin ([list[str]], optional): Process standard input. Defaults to None.
                        stdout ([type], optional): Process standard output. Defaults to None.
                        stderr ([type], optional): Process standard err. Defaults to None.
        """

        self.cmd = cmd
        self.cwd = cwd
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr


class AsyncParallel:
    pool = None
    max_processes = 1
    task_handler_list = {}

    def __init__(self, max_processes=max_processes):
        """Execute several functions (threads, processes) in parallel until return values called.

        Args:
                max_processes ([int], optional): Maximum number of tasks that will be run in parallel at the same time. Defaults to 1.

        """

        assert isinstance(max_processes, int)

        # prevent overwrite of previous settings
        if self.pool is not None:
            return

        self.pool = mp.Pool(processes=max_processes)
        self.max_processes = max_processes

    def join(self):
        if self.pool:
            self.pool.close()
            self.pool.join()

    def add_task(self, thread_task: TaskThread):

        assert isinstance(thread_task, TaskThread)
        # creates a pool of workers, add all tasks to the pool
        if self.pool is None:
            self.pool = mp.Pool(processes=self.max_processes)

        if thread_task.identifier not in self.task_handler_list:
            self.task_handler_list[thread_task.identifier] = []

        self.task_handler_list[thread_task.identifier].append(
            self.pool.apply_async(thread_task.fun, thread_task.args)
        )
        return thread_task.identifier

    def wait(self, identifier):
        for taskHandler in self.task_handler_list[identifier]:
            taskHandler.wait()

    def get_results(self, end=False):
        if self.pool is None:
            return None
        if end:
        # finish all tasks
            self.pool.close()
            self.pool.join()

        # retrieve the return values
        return_value_list = []
        safe_task_handler_list = self.task_handler_list.copy()
        for identifier in safe_task_handler_list:
            for taskHandler in safe_task_handler_list[identifier]:
                taskHandler.wait()
                # assert taskHandler.successful()
                return_value_list.append(taskHandler.get())

        # reset pool
        if end:
            self.pool = None
            self.task_handler_list = {}
        safe_task_handler_list = {}

        # return return_value_list
        fail_list = []
        for return_value in return_value_list:
            if isinstance(return_value, list):
                break
            process, task = return_value
            if process.returncode is None:
                continue
            if process.returncode != 0:
                fail_list.append(dict(process=process, task=task))

        if len(fail_list) > 0:
            return fail_list
        else:
            return None


class _QueueEndSignal(TaskThread):
    def __init__(self):
        super().__init__(None, None, identifier="_QueueEndSignal",
                         tasktype=TaskTypes.QUEUE_END_SIGNAL)


def runPatientThread(pool: AsyncParallel, taskQueue: mp.JoinableQueue, progressSender=None):
    logger = logging.getLogger(__name__)

    def loop(pool: AsyncParallel, taskQueue: mp.JoinableQueue, logger: logging.Logger):
        while True:
            try:
                task = taskQueue.get()

                assert isinstance(task, TaskThread or _QueueEndSignal)

                # if task is EndSignal, end loop.
                if isinstance(task, _QueueEndSignal):
                    taskQueue.task_done()
                    break
                if progressSender:
                    task.progressSender = progressSender
                pool.add_task(task)
                taskQueue.task_done()
                res = pool.get_results()
                if res:
                    logger.debug(res)
            except:
                traceback.print_exc()

    PatientThread = th.Thread(target=loop, args=(
        pool, taskQueue, logger), name="PatientThread")
    PatientThread.start()
    return PatientThread


if __name__ == '__main__':
    mp.freeze_support()
