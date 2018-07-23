from qtpy import QtWidgets, QtCore


__all__ = ['CloseAllFilter']


class CloseAllFilter(QtCore.QObject):
    """Event filter for closing all windows if the widget is closed."""
    def eventFilter(self, receiver, event):
        results = super().eventFilter(receiver, event)
        if event.type() == QtCore.QEvent.Close and event.isAccepted():
            # Close all top level widgets that prevent the application from quitting.
            try:
                QtWidgets.QApplication.instance().error_dialog.setExceptHook(False)
            except (AttributeError, RuntimeError, ValueError):
                pass
            for win in QtWidgets.QApplication.instance().topLevelWidgets():
                if win != receiver:
                    try:
                        win.close()
                    except (AttributeError, RuntimeError):
                        pass
                    try:
                        win.deleteLater()
                    except (AttributeError, RuntimeError):
                        pass

        return results
