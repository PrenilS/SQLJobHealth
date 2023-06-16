# SQLJobHealth

This is a tkinter application which takes your windowns login name, appends it to a hardcoded domain name for your oranisation and uses that combination to log into a hardcoded SQL Server using Windows authentication.

It will create a GUI which displays all MS SQL Server jobs owned by the user, their most recent run and an icon representing the outcome of the run. 

There is a input box on the top right which will change the number of most recent runs to display for each job. The default is 1.

# Using
## Optional
Create a virtual environment using the requirement.txt file in the repos root.

## Change placeholders
You will need to change '<Domain name>' and '<Server name>' in sqljobchek.py.

## Package
You can package it into an application using the following code in the root of your directory from a terminal
```shell
python -m PyInstaller --onefile --noconsole -n "SQLJobHealth" --icon=icon.ico --add-data="icon.ico;."  sqljobcheck.py
```