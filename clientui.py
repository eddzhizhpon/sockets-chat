import sys
from time import sleep

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QWidget,
    QLabel,
    QLineEdit,
    QPlainTextEdit
)

from PyQt5.QtCore import QObject, QThread, pyqtSignal

import client

class UpdateMessages(QObject):

    finished = pyqtSignal()
    progress = pyqtSignal(list)

    def __init__(self):
        super(UpdateMessages, self).__init__()
        self._isRunning = True

    def run(self):
        """Long-running task."""
        while self._isRunning:
            sleep(1)
            self.progress.emit(client.get_messages())
        self.finished.emit()

    def stop(self):
        self._isRunning = False


class Window(QWidget):
    username = None
    connect_btn = None
    destiny = None
    chat = None
    message = None
    send = None

    client = None

    def __init__(self):
        super().__init__()
        
        self.username = QLineEdit()
        
        self.connect_btn = QPushButton('Conectarse')
        self.connect_btn.setEnabled(True)
        self.connect_btn.clicked.connect(self.connect)

        self.destiny = QLineEdit()

        self.chat = QPlainTextEdit()
        self.chat.setReadOnly(True)

        self.message = QLineEdit()

        self.send = QPushButton('Enviar')
        self.send.setEnabled(False)
        self.send.clicked.connect(self.send_message)

        self.setWindowTitle('Chat')

        # Main layout
        layout = QFormLayout()

        # Username layout
        username_widget = QWidget()
        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username, 3)
        username_layout.addWidget(self.connect_btn, 1)
        username_widget.setLayout(username_layout)

        # Destiny layout
        send_widget = QWidget()
        send_layout = QHBoxLayout()
        send_layout.addWidget(self.message, 3)
        send_layout.addWidget(self.send, 1)
        send_widget.setLayout(send_layout)

        # Add widgets to the layout
        layout.addRow(QLabel('Usuario'), username_widget)
        layout.addRow(QLabel('Receptor'), self.destiny)
        layout.addRow(QLabel('Chat'), self.chat)
        layout.addRow(QLabel('Mensaje'), send_widget)

        # Set the layout on the application's window
        self.setLayout(layout)

    def connect(self):
        user = self.username.text()
        if user:
            client.connect(user)
            self.update_messages()
            self.connect_btn.setEnabled(False)
            self.send.setEnabled(True)
        else:
            print('Username empty')

    def send_message(self):
        des = self.destiny.text()
        msg = self.message.text()

        client.send_message(des, msg)

        self.message.setText('')

    def update_messages(self):
        self.update_messages = UpdateMessages()
        self.thread = QThread()
        self.update_messages.moveToThread(self.thread)

        self.thread.started.connect(self.update_messages.run)
        self.update_messages.finished.connect(self.thread.quit)
        self.update_messages.finished.connect(self.update_messages.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.update_messages.progress.connect(self.add_message)

        self.thread.start()

    def closeEvent(self, event):
        try:
            self.update_messages.stop()
            self.thread.quit()
            self.thread.wait()
        except:
            print('[INFO] thread not started')
        event.accept()
        print('[INFO] thread finished')

    def add_message(self, messages):
        for msg in messages:
            if msg:
                txt = f"{msg['username']} > {msg['message']}"
                self.chat.appendPlainText(txt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())