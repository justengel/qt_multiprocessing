import os
import qt_multiprocessing

from qtpy import QtWidgets


class MyPIDLabel(QtWidgets.QLabel):
    def print_pid(self):
        text = self.text()
        print(text, 'PID:', os.getpid())
        return text


class MyPIDLabelProxy(qt_multiprocessing.WidgetProxy):
    PROXY_CLASS = MyPIDLabel
    GETTERS = ['text']


def run_app():
    with qt_multiprocessing.MpApplication() as app:
        print("Main PID:", os.getpid())

        # Proxy
        lbl = MyPIDLabelProxy("Hello")

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            text = inp.text()
            lbl.setText(inp.text())

            # Try to somewhat prove that the label is in a different process.
            # `print_pid` Not exposed (will call in other process. Result will be None)
            print('Set Label text', text + '. Label text in this process', lbl.print_pid())

            # `print_pid` will run in a separate process and print the pid.

        btn.clicked.connect(set_text)

        widg.show()


def create_process_widgets():
    lbl = MyPIDLabel('Hello')
    lbl.show()
    return {'label': lbl}


def run_without_proxy():
    with qt_multiprocessing.MpApplication(initialize_process=create_process_widgets) as app:
        print("Main PID:", os.getpid())

        widg = QtWidgets.QDialog()
        lay = QtWidgets.QFormLayout()
        widg.setLayout(lay)

        # Form
        inp = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton('Set Text')
        lay.addRow(inp, btn)

        def set_text():
            text = inp.text()
            app.add_var_event('label', 'setText', text)

            # The label does not exist in this process at all. Can only access by string names
            print('Set Label text', text + '.')

            # `print_pid` will run in a separate process and print the pid.
            app.add_var_event('label', 'print_pid')

        btn.clicked.connect(set_text)

        widg.show()


def run_manual():
    app = QtWidgets.QApplication([])
    mp_loop = qt_multiprocessing.AppEventLoop(initialize_process=create_process_widgets)
    print("Main PID:", os.getpid())

    widg = QtWidgets.QDialog()
    lay = QtWidgets.QFormLayout()
    widg.setLayout(lay)

    # Form
    inp = QtWidgets.QLineEdit()
    btn = QtWidgets.QPushButton('Set Text')
    lay.addRow(inp, btn)

    def set_text():
        text = inp.text()
        mp_loop.add_var_event('label', 'setText', text)

        # The label does not exist in this process at all. Can only access by string names
        print('Set Label text', text + '.')

        # `print_pid` will run in a separate process and print the pid.
        mp_loop.add_var_event('label', 'print_pid')

    btn.clicked.connect(set_text)

    widg.show()

    # Run the multiprocessing event loop
    mp_loop.start()

    # Run the application event loop
    app.exec_()

    # Quit the multiprocessing event loop when the app closes
    mp_loop.close()


if __name__ == '__main__':
    run_app()
    # run_without_proxy()
    # run_manual()
