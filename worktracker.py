#!/usr/bin/python
from Tkinter import *
from functools import partial

from ConfigParser import ConfigParser
from datetime import datetime
from Queue import Queue
from threading import Thread

import os
import gspread

class GSpreadsheetBackend:

    def __init__(self, username, password, document_id):
        self.username = username
        self.password = password
        self.document_id = document_id

    def connect(self):
        self.gc = gspread.login(self.username, self.password)
        self.document = self.gc.open_by_key(self.document_id)

    def write(self, type, message):
        wks = self.document.get_worksheet(type)
        row_index = wks.row_count
        wks.add_rows(1)

        wks.update_acell("A%d" %row_index, datetime.now().isoformat())
        wks.update_acell("B%d" %row_index, message)


class Application(Frame):

    STATE_TASK      = 1
    STATE_POSITIVE  = 2
    STATE_NEGATIVE  = 3

    def create_widgets(self):
        self.current_state = IntVar()
        self.current_state.set(self.STATE_TASK)

        button_task = Radiobutton(self, text="Task", variable=self.current_state, value=self.STATE_TASK, indicatoron=0)
        button_task.grid(row=0, column=0),

        button_positive = Radiobutton(self, text="Positive", variable=self.current_state, value=self.STATE_NEGATIVE, indicatoron=0)
        button_positive.grid(row=0, column=1),

        button_negative = Radiobutton(self, text="Negtive", variable=self.current_state, value=self.STATE_POSITIVE, indicatoron=0)
        button_negative.grid(row=0, column=2)

        self.buttons = {
            "task"        : button_task,
            "positive"    : button_positive,
            "negative"    : button_negative
        }

        self.text_input = Entry(self, width=60)
        self.text_input.grid(row=1, columnspan=3, sticky=W+E)
        self.text_input.focus()

    def select_button(self, key, event):
        self.buttons.get(key).select()
        self.text_input.focus()

    def __init__(self, backend, master, work_pool):
        Frame.__init__(self, master)

        self.backend = backend
        self.work_pool = work_pool

        work_pool.put(lambda : backend.connect())

        self.pack()
        self.create_widgets()

        # Save / Exit shortcuts
        self.bind_all("<Return>", self.save)
        self.bind_all("<Escape>", self.quit)

        # Select task shortcuts
        self.bind_all("<Control-1>", partial(self.select_button, "task"))
        self.bind_all("<Control-2>", partial(self.select_button, "positive"))
        self.bind_all("<Control-3>", partial(self.select_button, "negative"))

    def save(self, event):
        state = self.current_state.get()
        text_input = self.text_input.get().strip()

        if text_input:
            self.work_pool.put(lambda : backend.write(state, text_input))

        self.master.destroy()

    def quit(self, event):
        self.master.destroy()

queue = Queue()

def worker():
    while True:
        queue.get()()
        queue.task_done()

# Start worker thread
thread = Thread(target=worker)
thread.daemon = True
thread.start()

# Initiate the gui
root = Tk()
root.title("Workload tracker")
root.resizable(0,0)

# Do magic to get the window to be in focus
root.iconify()
root.deiconify()
root.lift()

# Read configuration
config = ConfigParser()
config.read(['worktracker.cfg', os.path.expanduser('~/.worktracker.cfg')])

backend = GSpreadsheetBackend(
    config.get("google-spreadsheet", "username"),
    config.get("google-spreadsheet", "password"),
    config.get("google-spreadsheet", "document_id")
)

app = Application(backend, root, queue)
app.mainloop()

# Wait until all work is done
queue.join()

