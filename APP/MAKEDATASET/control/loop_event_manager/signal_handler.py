from types import FunctionType
from queue import Queue
import sys
import traceback
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import EventData


class SignalHandler:
    def __init__(self, name: str, data_type_to_work: any = None) -> None:
        """this class is to support and Event_loop_Manager-class and  is used to bound  a DataApp-type with a function-list.
        have in mind that data( data_to_work_with) is being produced.
        when the data is produced we need to do something(an to-do) with it 
        to know the data is ready to work with it, we emit an event which is managed by the event_loop_manager

        Args:
            name (str): name of work which the data is related or where the data came from
            data_type_to_work (DataApp):  to check a match between the data_to_work and the argument that the functions in list_to_do receive

        """
        self.name = name
        self.Data_type_to_work = data_type_to_work if data_type_to_work else type(
            data_type_to_work)  # to get type of None
        # this list stores functions that must be executed(called,running) when emit is called and  must receive   an instance of  Data_type_to_work as an argument
        self.list_to_do = []
        self.list_to_emit_only_once = []
        # to put an event an queue, the event is handled by a event_loop_manager,
        self.buffer_event: Queue = None
        self.running = False

    def connect(self, to_do_function: FunctionType, emit_only_once: bool = False, wrap_in_loop: bool = False) -> None:
        """
        allow to add a new function(slot) to the list_to_do or list_todo_emit_only_once.
        if wrap_in_loop is set True. the function will be wrap in a loop, then  this function needs only a time to  call throw emit()

        Args:
            to_do_function (FunctionType): the function is execute by an event_manager each time emit() is called. the arguments of to_do_function must be an instance  of Data_type_to_work or None
            emit_only_once (bool, optional): set True if the function need to be execute only once (in the first emit() after call connect()). Defaults to False.
            wrap_in_loop (bool, optional): set True if is necessary to run the function after the first emit and repeat by its own . Defaults to False.
        """

        if wrap_in_loop:
            emit_only_once = True

        def wrap_fun_in_loop(to_do_function: FunctionType) -> FunctionType:
            def loop_function(*args, **kwargs):
                while self.check_running():
                    to_do_function(*args, **kwargs)
            return loop_function

        def wrap_fun_in_try(to_do_function: FunctionType) -> FunctionType:
            def try_function(*args, **kwargs):
                try:
                    to_do_function(*args, **kwargs)
                except Exception:
                    print(traceback.format_exc())
            return try_function

        if wrap_in_loop:
            to_do_function = wrap_fun_in_loop(to_do_function)

        to_do_function = wrap_fun_in_try(to_do_function)

        if emit_only_once:
            self.list_to_emit_only_once.append(to_do_function)
        else:
            self.list_to_do.append(to_do_function)

    def emit(self, data_to_work: any = None) -> None:
        """
        emit event.
        when emit is called, the name of the work_data_handler and the args(data_to_work) are put in a buffer_event and an event_manager is in charge of run the functions stored in list_to_do 

        emit must receive the same datatype-args with which the work_data_handler was instantiated. 

        Args:
            data_to_work (DataApp,optional) : default= None.the data that will be used  as an argument for the functions in list_to_do of the work_data_handler
        """

        # only put an event in the buffer if the are functions to run
        if self.list_to_do or self.list_to_emit_only_once:
            if isinstance(data_to_work, self.Data_type_to_work):
                if self.buffer_event:
                    self.buffer_event.put(EventData(self.name, data_to_work))

                else:
                    raise Exception(
                        f'Work-handler with name [{self.name}] has not been added to any loop-event_manager')
            else:

                print(
                    f'wrong type var in emit() function from work_data_handler with name [{self.name}]')

                raise Exception(
                    f'waiting ({self.Data_type_to_work}) got {type(data_to_work)}, it is not the Data_type with which the handler(name={self.name}) was instanced')

    def setup(self, buffer: Queue, check_running_status: FunctionType) -> None:
        """
        this will be configured when the work_data_handler is added to the event_manager
        to redirect to the buffer_event that belongs to the event_manager.
        to redirect to running-var-status that belong to the event_manager.

        Args:
            buffer (Queue): buffer used to put in queue the events. Queue_buffer that refers to the buffer_event in event_manager
            running_var_status (bool): if the loop event manager stop(No forced) the  functions from  list_to_do which are running(futures that have a loop)  will stop too, check connect() function
        """
        self.buffer_event = buffer
        self.check_running = check_running_status

    def get_name(self):
        return self.name

    def get_list_to_do(self) -> list:
        """
        the first time emit() is called, the function on list_to_emit_only_once will be cleared, and just function in list_to_do will executed in future emit()

        Returns:
            list: the first time it is the sum of list_to_do-functions and list_to_tod_emit_once_and_repeat-functions.
        """
        if not self.list_to_emit_only_once:
            return self.list_to_do
        else:
            list_to_do_total = self.list_to_emit_only_once+self.list_to_do
            self.list_to_emit_only_once.clear()
            return list_to_do_total
    
    def disconnect_function(self, objective_function:FunctionType):
        """ erase an specific function from the list_to_do"""
        index = None
        try:
            index = self.list_to_do.index(objective_function)
        except:
            print('functions is not in signal')
        if index is not None:
            self.list_to_do.pop(index)
    
    def disconnect_all(self):
        """ erase all functions stored in list_to_do"""
        self.list_to_do.clear()
        
