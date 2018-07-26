from queue import Empty
from qtpy import QtWidgets, QtCore

from mp_event_loop import Event, CacheEvent, mark_task_done, process_event, EventLoop

from .events import VarEvent, SaveVarEvent


__all__ = ['QtEventQueueManager', 'AppEventLoop']


class QtEventQueueManager(object):
    """In the separate process manage widget event.

    Note:
        A thread does not allow widgets to be created and causes possible thread safety issues.
    """
    def __init__(self, alive_event, event_queue, consumer_queue=None, app=None):
        self.alive_event = alive_event
        self.event_queue = event_queue
        self.consumer_queue = consumer_queue
        self.app = app

        self.event_mngr = QtCore.QTimer()
        self.event_mngr.setInterval(0)  # Run when Qt event loop is idle (This may consume too much processing
        self.event_mngr.timeout.connect(self.process_single_event)

    def process_single_event(self):
        """Get a single event off of the queue and execute it."""
        if self.alive_event.is_set():
            try:
                event = self.event_queue.get_nowait()
                process_event(event, consumer_queue=self.consumer_queue)
                mark_task_done(self.event_queue)
            except Empty:
                pass
        elif self.app:
            try:
                self.app.quit()
            except (AttributeError, RuntimeError):
                pass

    def start(self):
        self.event_mngr.start()

    def stop(self):
        try:
            self.alive_event.clear()
        except (AttributeError, RuntimeError):
            pass
        try:
            self.event_mngr.stop()
        except (AttributeError, RuntimeError):
            pass


class AppEventLoop(EventLoop):
    """Run a Qt application in a separate process while processing events."""
    def __init__(self, initialize_process=None, output_handlers=None, event_queue=None, consumer_queue=None, name='main',
                 has_results=True):
        """Create the event loop.

        Args:
            initialize_process (function)[None]: Function to create and show widgets returning a dict of widgets and
                variable names to save for use.
            output_handlers (list/tuple/callable)[None]: Function or list of funcs that executed events with results.
            event_queue (Queue)[None]: Custom event queue for the event loop.
            consumer_queue (Queue)[None]: Custom consumer queue for the consumer process.
            name (str)['main']: Event loop name. This name is passed to the event process and consumer process.
            has_results (bool)[True]: Should this event loop create a consumer process to run executed events
                through process_output.
        """

        # Variables
        self.initialize_process = initialize_process

        # Initialize
        super().__init__(event_queue=event_queue, consumer_queue=consumer_queue, output_handlers=output_handlers,
                         name=name, has_results=has_results)

    def save_variables(self, create_func, *args, event_key=None, re_register=False, **kwargs):
        """

        Args:
            create_func (function/method/callable): Callable that creates variables and returns a dictionary of
                variable name, object paris.
            *args (tuple): Arguments to pass into the target function.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        args = kwargs.pop('args', args)
        kwargs = kwargs.pop('kwargs', kwargs)

        # Make sure cache is not a kwargs
        kwargs.pop('cache', None)

        if isinstance(create_func, CacheEvent):
            event = create_func
        elif isinstance(create_func, Event):
            old_event = create_func
            obj = old_event.target
            event = SaveVarEvent(obj, has_output=False, event_key=event_key,
                                 cache=self.cache, re_register=re_register)
            event.args = old_event.args
            event.kwargs = old_event.kwargs
            event.event_key = old_event.event_key
        else:
            event = SaveVarEvent(create_func, *args, **kwargs, has_output=False, event_key=event_key,
                                 cache=self.cache, re_register=re_register)

        return super().add_event(event)

    def add_var_event(self, var_name, target, *args, has_output=None, event_key=None, re_register=False, **kwargs):
        """Add an event to be run in a separate process.

        Args:
            var_name (str): Variable name.
            target (str/function/method/callable): Function or string object and function name.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the executed event and put it on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        args = kwargs.pop('args', args)
        kwargs = kwargs.pop('kwargs', kwargs)

        # Make sure cache is not a kwargs
        kwargs.pop('cache', None)

        if isinstance(target, CacheEvent):
            event = target
        elif isinstance(target, Event):
            args = args or target.args
            kwargs = kwargs or target.kwargs
            has_output = has_output or target.has_output
            event_key = event_key or target.event_key
            target = target.target

            if has_output is None:
                has_output = True
            event = VarEvent(var_name, target, *args, **kwargs, has_output=has_output, event_key=event_key,
                             cache=self.cache, re_register=re_register)
        else:
            if has_output is None:
                has_output = True
            event = VarEvent(var_name, target, *args, **kwargs, has_output=has_output, event_key=event_key,
                             cache=self.cache, re_register=re_register)

        return super().add_event(event)

    def start_event_loop(self):
        """Start running the event loop."""
        self.alive_event.set()
        self.event_process = self.event_loop_class(name="AppEventLoop-" + self.name, target=self.run_event_loop,
                                                   args=(self.alive_event, self.event_queue, self.consumer_queue),
                                                   kwargs={'initialize_process': self.initialize_process})
        self.event_process.daemon = True
        self.event_process.start()

    @staticmethod
    def run_qt_process(alive_event, event_queue, consumer_queue, initialize_process=None):
        """Start an application and run an event loop for multiprocessing."""
        app = QtWidgets.QApplication([])

        # Create widgets and store the widgets
        cache = CacheEvent.CACHE  # This is the cache for this process
        if callable(initialize_process):
            variables = initialize_process()
            for key, val in variables.items():
                cache[key] = val

        for _ in range(event_queue.qsize()):
            event = event_queue.get_nowait()
            process_event(event, consumer_queue=consumer_queue)
            mark_task_done(event_queue)

        # Start the system to process events (Note threads cannot create widgets).
        # event_mngr = threading.Thread(target=run_qt_event_loop, args=(alive_event, event_queue, consumer_queue, app))
        # event_mngr.start()
        event_mngr = QtEventQueueManager(alive_event, event_queue, consumer_queue, app)
        event_mngr.start()

        # Run the application
        app.exec_()

        # Close the multiprocessing event loop widget manager
        event_mngr.stop()

    run_event_loop = run_qt_process
