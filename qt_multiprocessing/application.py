from qtpy import QtWidgets
from .qt_proxy import WidgetProxy
from .qt_mp_event_loop import AppEventLoop


__all__ = ['MpApplication']


class MpApplication(QtWidgets.QApplication):
    """Application class that can send events to another process."""

    def __new__(cls, *args, **kwargs):
        """Actually create the new application."""
        app = cls.instance()
        if app is None:
            if len(args) == 0 and len(kwargs) == 0:
                args = ([],)
            return super().__new__(cls, *args, **kwargs)
        return app

    def __init__(self, *args, initialize_process=None, output_handlers=None, **kwargs):
        """Instantiate the application."""
        if len(args) == 0 and len(kwargs) == 0:
            args = ([],)

        super().__init__(*args, **kwargs)

        # Set the base proxy multiprocessing event loop
        if not hasattr(self, '__loop__'):
            self.__loop__ = AppEventLoop(initialize_process=initialize_process, output_handlers=output_handlers)
            WidgetProxy.__loop__ = self.__loop__

    def __enter__(self):
        """Enter the context manager (with statement)."""
        self.__loop__.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager (with statement). Run the event loop before exiting."""
        if exc_type is None:
            self.exec_()

            # Finish executing the multiprocessing event loop
            self.__loop__.__exit__(exc_type, exc_val, exc_tb)

            return True
        return False

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
        self.__loop__.save_variables(create_func, *args, event_key=event_key, re_register=re_register, **kwargs)

        if not self.__loop__.is_running():
            self.__loop__.start()

    def add_var_event(self, var_name, target, *args, has_output=None, event_key=None, **kwargs):
        """Add an event to be run in a separate process.

        Args:
            var_name (str): Variable name.
            target (str/function/method/callable): Function or string object and function name.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the executed event and put it on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        self.__loop__.add_var_event(var_name, target, *args, has_output=has_output, event_key=event_key, **kwargs)

        if not self.__loop__.is_running():
            self.__loop__.start()

    def add_mp_event(self, target, *args, has_output=None, event_key=None, cache=False, re_register=False, **kwargs):
        """Add an event to be run in a separate process.

        Args:
            target (function/method/callable/Event): Event or callable to run in a separate process.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the executed event and put it on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            cache (bool) [False]: If the target object should be cached.
            re_register (bool)[False]: Forcibly register this object in the other process.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        self.__loop__.add_event(target, *args, has_output=has_output, event_key=event_key,
                                cache=cache, re_register=re_register, **kwargs)

        if not self.__loop__.is_running():
            self.__loop__.start()

    def add_mp_cache_event(self, target, *args, has_output=None, event_key=None, re_register=False, **kwargs):
        """Add an event that uses cached objects.

        Args:
            target (function/method/callable/Event): Event or callable to run in a separate process.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the executed event and put it on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        self.__loop__.add_cache_event(target, *args, has_output=has_output, event_key=event_key,
                                      re_register=re_register, **kwargs)

        if not self.__loop__.is_running():
            self.__loop__.start()

    def mp_cache_object(self, obj, has_output=False, event_key=None, re_register=False):
        """Save an object in the separate processes, so the object can persist.

        Args:
            obj (object): Object to save in the separate process. This object will keep it's values between cache events
            has_output (bool)[False]: If True the cache object will be a result passed into the output_handlers.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
        """
        self.__loop__.cache_object(obj, has_output=has_output, event_key=event_key, re_register=re_register)

        if not self.__loop__.is_running():
            self.__loop__.start()
