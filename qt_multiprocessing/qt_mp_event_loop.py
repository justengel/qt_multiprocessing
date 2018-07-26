from queue import Empty
from qtpy import QtWidgets, QtCore

from mp_event_loop import Event, CacheEvent, mark_task_done, process_event, EventLoop


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
                try:
                    process_event(event, consumer_queue=self.consumer_queue)
                finally:
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
