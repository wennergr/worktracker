#!/usr/bin/python
from ConfigParser import ConfigParser

import getpass
import os
import gspread

VERSION = 0.5

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

        self.document.add_worksheet("Tasks", 1, 3)
        self.document.add_worksheet("Negative", 1, 3)
        self.document.add_worksheet("Positive", 1, 3)

def message(msg):
    print("> "+msg)

if __name__ == "__main__":
    message("Setup for worktrack logger")
    message("Before you start. Login to your google drive account and create and empty spreadsheet")
    username = raw_input("Google Driver username: ")
    password = getpass.getpass()
    document_id = raw_input("Id of spreadsheet: ")

    # Read configuration
    config = ConfigParser()
    config.add_section("google-spreadsheet")
    config.set("google-spreadsheet", "username", username),
    config.set("google-spreadsheet", "password", password),
    config.set("google-spreadsheet", "document_id", document_id)

    # Setup the backend
    backend = GSpreadsheetBackend(
        config.get("google-spreadsheet", "username"),
        config.get("google-spreadsheet", "password"),
        config.get("google-spreadsheet", "document_id")
    )

    message("Connecting to google driver")
    backend.connect()

    message("Configuring spreadsheet")
    backend.prepare_document()

    message("Saving configuration")
    config.write(open(os.path.expanduser('~/.worktracker.cfg'), "w"))

