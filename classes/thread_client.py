import tkinter as tk
import bluetooth as bt
import threading
import queue
import sys
import time
from classes.bluetooth_gui import BlueToothClient

class ThreadedClient():
    def __init__(self, master):
        self.master = master
        self.message_queue = queue.Queue()

        self.thread_stop = threading.Event()
        self.running = True
        self.connection_running = False
        self.all_data = []
        self.got_length = False

        self.gui = BlueToothClient(master, self.message_queue, self.end_gui, self.start_message_awaiting,
            self.end_bluetooth_connection)
        self.periodic_call()

    def start_message_awaiting(self):
        self.thread_stop.clear()
        self.await_messages = threading.Thread(target=self.await_messages_thread,
            daemon=True)
        self.connection_running = True
        self.await_messages.start()

    def stop_threads(self):
        try:
            sys.exit(1)
        except Exception as e:
            print(e)

    def periodic_call(self):
        self.gui.check_message_queue()
        if not self.running:
            self.stop_threads()
        else:
            self.master.after(100, self.periodic_call)

    def get_complete_message(self):
        try:
            more_data = True
            message_buffer = b''
            while more_data:
                data = self.gui.sock.recv(8192)

                if '\n'.encode('ascii') in data:
                    more_data = False
                    message_buffer += data
                else:
                    message_buffer += data
            return message_buffer
        except bt.btcommon.BluetoothError:
            self.connection_running = False

    def await_messages_thread(self):
        while self.connection_running:
            message = self.get_complete_message()
            if not self.connection_running:
                break
            try:
                self.message_queue.put(message)
            except AttributeError:
                pass

    def end_gui(self):
        self.running = False

    def end_bluetooth_connection(self):
        self.connection_running = False