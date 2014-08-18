#!/usr/bin/python
from Tkinter import *
from functools import partial

from ConfigParser import ConfigParser
from datetime import datetime
from Queue import Queue
from threading import Thread

import sys
import os
import gspread

STATE = {
    "task"      : 1,
    "="         : 1, # Task short version
    "negative"  : 2,
    "-"         : 2, # Negative short version
    "positive"  : 3,
    "+"         : 3  # Positive short version
}

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


class GuiApplication(Frame):

    def create_widgets(self):
        self.current_state = IntVar()
        self.current_state.set(STATE["task"])

        button_task = Radiobutton(self, text="Task", variable=self.current_state, value=STATE["task"], indicatoron=0)
        button_task.grid(row=0, column=0),

        button_positive = Radiobutton(self, text="Positive", variable=self.current_state, value=STATE["positive"], indicatoron=0)
        button_positive.grid(row=0, column=1),

        button_negative = Radiobutton(self, text="Negative", variable=self.current_state, value=STATE["negative"], indicatoron=0)
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
        self.bind_all("<Control-i>", partial(self.select_button, "task"))
        self.bind_all("<Control-o>", partial(self.select_button, "positive"))
        self.bind_all("<Control-p>", partial(self.select_button, "negative"))

    def save(self, event):
        state = self.current_state.get()
        text_input = self.text_input.get().strip()

        if text_input:
            self.work_pool.put(lambda : backend.write(state, text_input))

        self.master.destroy()

    def quit(self, event):
        self.master.destroy()

def gui_start(backend):
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

    app = GuiApplication(backend, root, queue)
    app.mainloop()

    # Wait until all work is done
    queue.join()
 
def cli_start(backend, args):
    def usage():
        print "Usage: %s [task|positive|negative] message" %sys.argv[0]

    if len(sys.argv) != 3:
        usage()

    type = STATE[sys.argv[1]]
    if not type:
        print "Invalid type: %s" %sys[argv[1]]

    message = sys.argv[2]

    backend.connect()
    backend.write(type, message)

if __name__ == "__main__":
    # Read configuration
    config = ConfigParser()
    if not config.read(['worktracker.cfg', os.path.expanduser('~/.worktracker.cfg')]):
        import worktracker_installer
        config = worktracker_installer.install()

    backend = GSpreadsheetBackend(
        config.get("google-spreadsheet", "username"),
        config.get("google-spreadsheet", "password"),
        config.get("google-spreadsheet", "document_id")
    )

    if len(sys.argv) <= 1:
        gui_start(backend)
    else:
        cli_start(backend, sys.argv)

