import os
import qt_multiprocessing
from qtpy import QtWidgets, QtCore


class MyPIDLabel(QtWidgets.QLabel):
    def print_pid(self):
        text = self.text()
        print(text, 'PID:', os.getpid())
        return text


class LabelProxy(qt_multiprocessing.WidgetProxy):
    PROXY_CLASS = MyPIDLabel
    GETTERS = ['text']


if __name__ == '__main__':
    with qt_multiprocessing.MpApplication() as app:  # Automatically sets WidgetProxy.__loop__
        lbls = []

        print("Main PID:", os.getpid())

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Create Label')
        lay.addRow(inp, btn)

        def create_label():
            # Create a new label in a different process every time Set Text is clicked.
            text = inp.text()
            lbl = LabelProxy(text)
            lbl.move(130 * len(lbls), 200)

            # Try to somewhat prove that the label is in a different process.
            # Not exposed (will call in other process. This will be None)
            print('Set Label text', text + '. Label text in this process', lbl.print_pid())

            lbls.append(lbl)  # Make sure it doesn't die? It may still not die due to dictionary cache

        btn.clicked.connect(create_label)

        # ===== Button to show label texts =====
        get_text_btn = QtWidgets.QPushButton('Get Labels')

        def print_labels():
            [lbl.print_pid() for lbl in lbls]  # Call to print the label pid
            print([lbl.text() for lbl in lbls])  # No initial text, but eventually syncs the text() method

        get_text_btn.clicked.connect(print_labels)
        lay.addRow(get_text_btn)

        widg.show()
