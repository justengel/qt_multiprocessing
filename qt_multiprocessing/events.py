from mp_event_loop import Event, CacheEvent


__all__ = ['SaveVarEvent', 'VarEvent']


class SaveVarEvent(CacheEvent):
    """Save the given object as the given variable name. You can then call methods on the object with the variable name
    using a VarEvent.
    """
    def __init__(self, create_func, *args, has_output=True, event_key=None, cache=None, re_register=False,
                 **kwargs):
        """Create the event.

        Args:
            create_func (callable): Function that will create variables and return a dictionary of
                variable name, object pairs.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the results and put this event on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
            cache (dict)[None]: Custom cache dictionary.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        super().__init__(create_func, *args, has_output=has_output, event_key=event_key,
                         cache=cache, re_register=re_register, **kwargs)

    def exec_(self):
        """Get the command and run it"""
        # Get the command to run
        self.results = None
        self.error = None
        if callable(self.target):
            # Run the command
            try:
                results = self.run()

                # Results should be a dictionary.
                for key, value in results.items():
                    CacheEvent.register_object(value, key, cache=self.cache)

                self.results = True

            except Exception as err:
                self.error = err
        elif self.target is None and self.object is not None:
            self.results = self.object
        else:
            self.error = ValueError("Invalid target (%s) given! Type %s" % (repr(self.target), str(type(self.target))))


class VarEvent(CacheEvent):
    """Run a method on a variable in a different process."""
    def __init__(self, var_name, method_name, *args, has_output=True, event_key=None, cache=None, re_register=False,
                 **kwargs):
        """Create the event.

        Args:
            var_name (str): Variable name or object id to access a cached object.
            method_name (str): Method name of the variable name to call with the given args and kwargs.
            *args (tuple): Arguments to pass into the target function.
            has_output (bool) [False]: If True save the results and put this event on the consumer/output queue.
            event_key (str)[None]: Key to identify the event or output result.
            re_register (bool)[False]: Forcibly register this object in the other process.
            cache (dict)[None]: Custom cache dictionary.
            **kwargs (dict): Keyword arguments to pass into the target function.
            args (tuple)[None]: Keyword args argument.
            kwargs (dict)[None]: Keyword kwargs argument.
        """
        super().__init__(None, *args, has_output=has_output, event_key=event_key, cache=cache, re_register=re_register,
                         **kwargs)
        self.object_id = var_name
        self.method_name = method_name
