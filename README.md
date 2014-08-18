# Worktracker


System to keep track on day to day tasks. It tracks tasks common work tasks and positive and negative events.
Resulsts are stored in google spreadsheet document.

## Installation (macosx, standalone)

 1. Clone the repository
 2. Download and install depdenencies:
```pip install gspread py2app```
 
 3. Build application:
```python setup.py py2app```

 4. Startup the application: ```cd dist && open worktracker.app```

## Configure google driver
The installation system will ask you for your google driver
credentials during installation. It's recommended to use an app specific password and not your
primary usernaem and password. App specific password's can be configured on your [google security page](https://www.google.com/settings/security). You will also need to create an empty
google spreadsheet document and retrive the id from it. This id is part of the url.

Example:
https://docs.google.com/spreadsheets/d/4Hdf9bNqsdsdadwedf/edit

Your spreadsheet id is: 4Hdf9bNqsdsdadwedf


## Integration with Alfred 2
Worklog integrates with alfred 2 workflow. 

See the [alfred2](alfred2) folder for more details

