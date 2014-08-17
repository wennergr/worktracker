#!/usr/bin/python
from ConfigParser import ConfigParser

import getpass
import os
import gspread

from Tkinter import *

VERSION = 0.5

class Installer(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)

        self.status = StringVar(value="Waiting for user input")
        self.pack()
        self.create_widgets()

        self.bind_all("<Escape>", self.quit)

    def create_widgets(self):
        description = Label(self, text="Configration of workshop installer")
        description.grid(row=0, column=0, columnspan=3, sticky=W+E)

        username_label = Label(self, text="Google Driver Email")
        username_label.grid(row=1, column=0, sticky=W)
        self.username_input = Entry(self, width=35)
        self.username_input.grid(row=1, column=1, columnspan=2)

        password_label = Label(self, text="Google Driver Password")
        password_label.grid(row=2, column=0, sticky=W)
        self.password_input = Entry(self, width=35)
        self.password_input.grid(row=2, column=1, columnspan=2)

        document_id_label = Label(self, text="Spreadsheet document id")
        document_id_label.grid(row=3, column=0, sticky=W)
        self.document_id_input = Entry(self, width=35)
        self.document_id_input.grid(row=3, column=1, columnspan=2)

        button_ok = Button(self, text="Save", command=self.save, anchor=W)
        button_ok.grid(row=4, column=1, sticky=E)

        button_cancel = Button(self, text="Cancel", command=self.quit, anchor=E)
        button_cancel.grid(row=4, column=2)

        status_label = Label(self, textvariable=self.status, bd=1, relief=SUNKEN, anchor=E)
        status_label.grid(row=5, columnspan=3, sticky=W+E)
 

    def quit(self, event=None):
        self.master.destroy()
        exit(1)

    def save(self):
        self.config = self.create_config()
        self.create_spreadsheet(self.config)
        self.master.destroy()

    def create_config(self):
        config = ConfigParser()
        config.add_section("google-spreadsheet")
        config.set("google-spreadsheet", "username", self.username_input.get()),
        config.set("google-spreadsheet", "password", self.password_input.get()),
        config.set("google-spreadsheet", "document_id", self.document_id_input.get())

        return config

    def create_spreadsheet(self, config):
        backend = GSpreadsheetBackend(
            config.get("google-spreadsheet", "username"),
            config.get("google-spreadsheet", "password"),
            config.get("google-spreadsheet", "document_id")
        )

        self.status.set("Connecting to google driver ...")
        try:
            backend.connect()
        except Exception as e:
            self.status.set("Unble to connect: "+e.message)
            raise e

        self.status.set("Configuring spreadsheet ...")
        try:
            backend.prepare_document()
        except Exception as e:
            self.status.set("Unable to configure spreadsheet: "+e.message)
            raise e


        self.status.set("Saving configuration ...")
        config_file = config.write(open(os.path.expanduser('~/.worktracker.cfg'), "w"))

class GSpreadsheetBackend:

    def __init__(self, username, password, document_id):
        self.username = username
        self.password = password
        self.document_id = document_id

    def connect(self):
        self.gc = gspread.login(self.username, self.password)
        self.document = self.gc.open_by_key(self.document_id)

    def prepare_document(self):
        wks1 = self.document.sheet1
        wks1.update_acell("A1", "Spreadsheet backed by worktracker. Don't modify manually")
        wks1.update_acell("A2", "%s" %VERSION)

        if not self.document.worksheet("Tasks"):
            self.document.add_worksheet("Tasks", 1, 3)

        if not self.document.worksheet("Negative"):
            self.document.add_worksheet("Negative", 1, 3)

        if not self.document.worksheet("Positive"):
            self.document.add_worksheet("Positive", 1, 3)

def install():
    root = Tk()
    root.title("Workload configuration")
    root.resizable(0,0)

    app = Installer(root)
    app.mainloop()

    return app.config

if __name__ == "__main__":
    install()

