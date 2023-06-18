# %%
import pyodbc
from tkinter import Tk, Label, Listbox, Scrollbar, Entry, Button, Frame, Y, messagebox, ttk
import os
import json
from pathlib import Path

# %% make appdata config folder
appdatadir = f'{Path.home()}\\AppData\\Roaming\\SQLJobHealth'
try:
    os.mkdir(appdatadir)
except:
    pass
config_path = os.path.join(appdatadir, "config.json")
if not os.path.exists(config_path):
    config = {}
    with open(config_path, "w") as file:
        json.dump(config, file)

basedir = os.path.dirname(__file__)

#%%
# Load the config from the JSON file
def load_config():
    config_path = os.path.join(appdatadir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = json.load(file)
    else:
        config = {}
    return config

# Save the config to the JSON file
def save_config(config):
    config_path = os.path.join(appdatadir, "config.json")
    with open(config_path, "w") as file:
        json.dump(config, file)

# Function to handle connection errors
def handle_connection_error():
    messagebox.showerror("Connection Error", "Error connecting to the database. Please check your server name and try again.")

# Function to retrieve user input and update the results
def update_results():
    outcome_listbox.delete(0, 'end')
    outcome_datebox.delete(0, 'end')
    job_listbox.delete(0, 'end')
    row_count = int(entry_row_count.get())
    server = server_entry.get()
    job_owner = job_owner_entry.get()

    # Update the config with the new values
    config["row_count"] = row_count
    config["server"] = server
    #config["job_owner"] = job_owner
    save_config(config)

    try:
        database = 'msdb'  # Replace with your database name
        trusted_connection = 'yes'

        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection};'
        conn = pyodbc.connect(conn_str)

        # Fetch SQL Agent jobs owned by the specified user
        cursor = conn.cursor()
        query = f"SELECT name FROM sysjobs WHERE enabled=1 and owner_sid = SUSER_SID('{job_owner}') order by name"
        cursor.execute(query)
        jobs = cursor.fetchall()

        job_outcomes = {}
        for job in jobs:
            job_name = job[0]

            # Fetch the most recent two run outcomes for the job
            query = f"SELECT TOP {row_count} run_status, run_date FROM sysjobhistory WHERE step_name like '(Job outcome)' and job_id = (SELECT job_id FROM sysjobs WHERE name = '{job_name}') ORDER BY run_date DESC, run_time DESC"
            cursor.execute(query)
            run_outcomes = cursor.fetchall()

            # Store the run outcomes in the job_outcomes dictionary
            job_outcomes[job_name] = [outcome for outcome in run_outcomes]
        
        # Close the database connection
        conn.close()

        for job_name, outcomes in job_outcomes.items():
            outcome_text = ""
            formatted_date = ""
            if len(outcomes) == 0:
                job_listbox.insert("end", job_name)
                outcome_listbox.insert("end", outcome_text)
                outcome_datebox.insert("end", formatted_date)
            else:
                for outcome in outcomes[:row_count]:
                    job_listbox.insert("end", job_name)
                    if outcome[0] == 1:
                        outcome_text = "✔️"
                        outcome_color = "green"
                    elif outcome[0] == 4:
                        outcome_text = "►"
                        outcome_color = "blue"
                    else:
                        outcome_text = "❌"
                        outcome_color = "red"
                    run_date = str(outcome[1])  # Convert run_date to string
                    formatted_date = f"{run_date[:4]}-{run_date[4:6]}-{run_date[6:]}"  # Format run_date
                    outcome_listbox.insert("end", outcome_text)
                    outcome_listbox.itemconfigure("end", foreground=outcome_color)
                    outcome_datebox.insert("end", formatted_date)
    except pyodbc.Error:
        handle_connection_error()
        entry_row_count.focus_force()
        server_entry.focus_force()
        job_owner_entry.focus_force()

# Create a scrollbar for the frame
def scroll(x, y):
    outcome_listbox.yview(x,y)
    outcome_datebox.yview(x,y)
    job_listbox.yview(x,y)

#%%
# Create a Tkinter window
window = Tk()
window.title("SQL Agent Jobs")

# Load the config
config = load_config()

# Retrieve the default values from the config
default_row_count = config.get("row_count", 1)
default_server = config.get("server", "")
default_job_owner = config.get("job_owner", os.getlogin())


# Create a label for the job list
job_label = Label(window, text="SQL Agent Jobs:")
job_label.grid(row=1, column=0)

# Create a label for the outcome list
outcome_label = Label(window, text="Run Outcomes:")
outcome_label.grid(row=1, column=1)

# Create a label for the date list
outcome_date = Label(window, text="Run Dates:")
outcome_date.grid(row=1, column=2)

# Create a Frame to contain the listboxes
listbox_frame = Frame(window)
listbox_frame.grid(row=2, column=0, columnspan=3, padx=10)

scrollbar = Scrollbar(listbox_frame, orient="vertical")
scrollbar.pack(side="right", fill=Y)
scrollbar.config( command = scroll)

# Create a listbox to display the job names
job_listbox = Listbox(listbox_frame, width=30, yscrollcommand=scrollbar.set)
job_listbox.pack(side="left", fill=Y, expand=True)

# Create a listbox to display the run outcomes
outcome_listbox = Listbox(listbox_frame, width=15, yscrollcommand=scrollbar.set)
outcome_listbox.pack(side="left", fill=Y, expand=True)

# Create a listbox to display the run dates
outcome_datebox = Listbox(listbox_frame, width=25, yscrollcommand=scrollbar.set)
outcome_datebox.pack(side="left", fill=Y, expand=True)


# Create a Frame to contain the inputs
input_frame = Frame(window)
input_frame.grid(row=0, column=0, columnspan=3, padx=10)

# Create a label and an entry field for row count
row_count_label = Label(input_frame, text="Number of Rows:")
row_count_label.pack(side="left", fill=Y, expand=True)

entry_row_count = ttk.Entry(input_frame, width=5)  # Assuming you use Entry field to capture the row count
entry_row_count.pack(side="left", fill=Y, expand=True)
entry_row_count.insert(0,default_row_count)

# Create a label and an entry field for server name
server_label = Label(input_frame, text="Server:")
server_label.pack(side="left", fill=Y, expand=True)

server_entry = ttk.Entry(input_frame, width=20)
server_entry.pack(side="left", fill=Y, expand=True)
server_entry.insert(0, default_server)  # Set default server name

# Create a label and an entry field for job owner
job_owner_label = Label(input_frame, text="Job Owner:")
job_owner_label.pack(side="left", fill=Y, expand=True)

job_owner_entry = ttk.Entry(input_frame, width=20)
job_owner_entry.pack(side="left", fill=Y, expand=True)
job_owner_entry.insert(0, default_job_owner)  # Set default job owner

# Create a Frame to contain the buttons
button_frame = Frame(window)
button_frame.grid(row=3, column=1, columnspan=1, padx=10)
# Add a button to trigger the retrieval with the specified row count
retrieve_button = Button(button_frame, text="Refresh", command=update_results)
retrieve_button.pack(side="left", fill=Y, expand=True)

# Populate the job and outcome listboxes
update_results()

# Configure listbox item colors
try:
    job_listbox.itemconfig("end", fg="black")
    outcome_listbox.itemconfig("end", fg="black")
except:
    print("")

# Remove the last empty item in job_listbox
job_listbox.delete("end")

# Start the Tkinter event loop
window.iconbitmap(os.path.join(basedir, "icon.ico"))
window.mainloop()
