from typing import Dict, List
from time import sleep
import numpy as np
from threading import Thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import traceback
from types import FunctionType
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, EventData
from APP.MAKEDATASET.control.loop_event_manager.signal_handler import SignalHandler


class LoopEventManager(Thread):
    def __init__(self, name: str, max_workers=15) -> None:
        """
        A Thread-class that is used to initialize a thread by each function stored in the signal_handlers.
        there may be several signal_handler

        args:
        name[str]: prefix_name for threads initialized in threadPoolExecutor
        """
        super().__init__()
        max_workers = max_workers
        thread_name_prefix = name
        self.running = True  # to stop the while in running loop function
        self.event_executor = ThreadPoolExecutor(
            max_workers, thread_name_prefix)
        # a buffer to put  a name and the args to work with a signal_handler
        self.buffer_event = Queue(50)
        # to store several signal_handlers and  its names
        self.dict_signal_handlers: Dict[str, SignalHandler] = {}
        # to run function that just run only once and which not need a own signal_handler. this functions not receive args
        self.own_data_handler = SignalHandler('function_without_own_handler')
        self.add_signal_handler(self.own_data_handler)

    def add_signal_handler(self, signal_handler: SignalHandler) -> None:
        """to add a signal_handler. each signal_handler has a list of functions to execute when an emit function is called

        Args:
            signal_handler (SignalHandler): this class is to support and Event_loop_Manager class and  is used to bound  a DataTypeApp with a function-list to executed when handler.emit() is called
        """
        print(f'adding data_work_handler: {signal_handler.name}')
        # its a shared buffer between all signal_handlers add to de the loop_manager
        signal_handler.setup(
            buffer=self.buffer_event, check_running_status=self.check_running)
        self.dict_signal_handlers.update(
            {signal_handler.get_name(): signal_handler})

    def add_signal_handlers_from_list(self, list_signal_handlers: List[SignalHandler]) -> None:
        """add multiple signalHandlers from a list

        Args:
            list_signal_handlers (list[SignalHandler]): list that has a last one signalHandler
        """
        # map(self.add_signal_handler,list_signal_handlers)# this makes a copy of signalHandler and not update the original objects
        for signal_handler in list_signal_handlers:  # this does not make a copy.
            self.add_signal_handler(signal_handler)

    def emit_function_only_once(self, function_to_work: FunctionType, wrap_in_loop: bool = False) -> None:
        """
        the functions will be add to the pool executer only once

        useful to run functions(without args) that not belong to a data_work_handler

        Args:
            function_to_work: if you need to run a function with args, wrap the function in a lambda function. Eg: function_to_work=lambda: function(arg1,arg2...) 
            loop_function (FunctionType): this this must not receive arguments receive
        """
        if wrap_in_loop:
            self.own_data_handler.connect(
                function_to_work, emit_only_once=True, wrap_in_loop=True)
        else:
            self.own_data_handler.connect(
                function_to_work, emit_only_once=True)

        self.own_data_handler.emit()

    def run(self) -> None:
        """
        this loop handler/check if there is an event in the buffer_event. 
        the buffer_event must receive an EventData instance. EventData has a name  to know which signal_handler must be called and has the args(DataApp) that must be used in the functions stored in the signal_handler
        """
        while self.running:
            try:
                # wait and get the events pushed by the emit function from the signal_handlers
                event_data: EventData = self.buffer_event.get()
                if event_data:  # this is needed  to put a last  data in buffer and close thread, other way ,buffer.get() force to wait and  keep alive the thread
                    # it's not need to check if work_handler exist in dict_handler.  when the emit() function is called it will raise an exception if handler is not add, because buffer_event will not be set up
                    work_handler = self.dict_signal_handlers.get(
                        event_data.name)
                    list_to_do = work_handler.get_list_to_do()
                    for to_do_function in list_to_do:
                        if work_handler.Data_type_to_work != type(None):
                            if self.running:
                                self.event_executor.submit(
                                    to_do_function, event_data.data_to_work)
                        else:
                            # this is need to run functions with not args
                            print('run function without args')
                            self.event_executor.submit(to_do_function)
            except Exception:
                print(f'error in emit function from {event_data.name}')
                print(traceback.format_exc())
                self.stop()
                break
        print('close loop-thread')

    def check_running(self):
        return self.running

    def stop(self) -> None:
        """
        stop running loop
        close all thread set up by event_executor
        """
        print("closing event manager")
        self.running = False
        self.buffer_event.put(None)

# TEST
# ##########################################


def run():
    def make_task(name: str):

        # todo
        def do_something(data_to_work: DataFromAcquisition):
            # the function must be build with the same datatype-args with which the data handler was instanced
            print(
                f'work {name}: shape rgb: {data_to_work.rgb.size},depth: {data_to_work.depth.size}')
            print('')

        return do_something

    loop_manager = LoopEventManager('pool manager')
    loop_manager.start()
    loop_manager.emit_function_only_once(lambda: print(
        'run only once and not repeat'), wrap_in_loop=False)
    work1_handler = SignalHandler(
        name='process1', data_type_to_work=DataFromAcquisition)
    work2_handler = SignalHandler(
        name='process2', data_type_to_work=DataFromAcquisition)
    loop_manager.add_signal_handlers_from_list([work1_handler, work2_handler])
    work1_handler.connect(make_task(work1_handler.name))
    work2_handler.connect(make_task(work2_handler.name))
    # work2_handler.emit(9)

    def loop_emit_triggers():
        print('trigger loop')
        loop_manager.emit_function_only_once(lambda: print(
            'run only once and not repeat'))  # run function without handler
        # do something...get something...
        img = np.zeros((640, 480))
        # the work_handler  is  going to work  only with the data type with which they were instantiated and with no args( args=None, behavior by default)
        # this is expected and valid
        work1_handler.emit(DataFromAcquisition(img, img))
        sleep(2)
        # the emit always must have the same datatype with which the data handler was instantiated
        work2_handler.emit(DataFromAcquisition(2*img, 2*img))
        sleep(3)
        # work2_handler.emit(9)# 9 is a int-var-type then it's not valid, this is not the data-type(DataFromAcquisition) with which the handler was instantiated
    # make test signals-emit
    loop_manager.emit_function_only_once(
        loop_emit_triggers, wrap_in_loop=True)  # run function without handler

    # work1_handler.emit()
    while True:
        check_input = input('press q to close')
        if check_input == 'q':
            break
    loop_manager.stop()


if __name__ == '__main__':
    run()
