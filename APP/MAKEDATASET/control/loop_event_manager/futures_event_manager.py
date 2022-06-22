from types import FunctionType
from typing import Dict, List
from time import sleep
import numpy as np
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, EventData
from APP.MAKEDATASET.control.loop_event_manager.signal_handler import SignalHandler
from APP.MAKEDATASET.control.loop_event_manager import LoopEventManager

class FuturesLoopEventManager(LoopEventManager, Thread):
    def __init__(self, name: str, max_workers=15) -> None:
        """
        A Thread-class that is used to initialize a thread by each function stored in the signal_handlers.
        there may be several signal_handler

        args:
        name[str]: prefix_name for threads initialized in threadPoolExecutor
        """
        LoopEventManager.__init__(self,max_workers)
        Thread.__init__(self)
        
        thread_name_prefix = name
        self.event_executor = ThreadPoolExecutor(
            max_workers, thread_name_prefix)
        
    def add_new_thread_task(self, todo_function:FunctionType, data_to_work:any) -> None:
        if data_to_work is None:
            # this is need to run functions with not args
            print('run function without args')
            self.event_executor.submit(todo_function)
        else:
            self.event_executor.submit(todo_function, data_to_work)
        

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

    loop_manager = FuturesLoopEventManager('pool manager')
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
