# %%
import pyodbc
from tkinter import Tk, Label, Listbox, Scrollbar, Entry, Button, Frame, Y
import os

basedir = os.path.dirname(__file__)
# SQL Server connection details
server = '<Server name>'  # Replace with your server name
database = 'msdb'  # Replace with your database name
trusted_connection = 'yes'

# SQL Agent job owner
job_owner = '<Domain name>\\'+os.getlogin()

conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection};'
conn = pyodbc.connect(conn_str)

# Fetch SQL Agent jobs owned by the specified user
cursor = conn.cursor()
query = f"SELECT name FROM sysjobs WHERE enabled=1 and owner_sid = SUSER_SID('{job_owner}')"
cursor.execute(query)
jobs = cursor.fetchall()
conn.close()
#%%
# Create a Tkinter window
window = Tk()
window.title("SQL Agent Jobs")
#window.geometry("600x500")
#window.geometry(f"{window_width}x{window_height}") 

# Create a label for the job list
job_label = Label(window, text="SQL Agent Jobs:")
job_label.grid(row=0, column=0)

# Create a label for the outcome list
outcome_label = Label(window, text="Run Outcomes:")
outcome_label.grid(row=0, column=1)

# Create a label for the date list
outcome_date = Label(window, text="Run Dates:")
outcome_date.grid(row=0, column=2)

# Create a Frame to contain the listboxes
listbox_frame = Frame(window)
listbox_frame.grid(row=1, column=0, columnspan=3, padx=10)

# Create a scrollbar for the frame
def scroll(x, y):
    outcome_listbox.yview(x,y)
    outcome_datebox.yview(x,y)
    job_listbox.yview(x,y)

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

# Function to retrieve user input and update the results
def update_results():
    outcome_listbox.delete(0,'end')
    outcome_datebox.delete(0,'end')
    job_listbox.delete(0,'end')
    row_count = int(entry.get())
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection};'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
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
                if outcome[0]==1:
                    outcome_text = "✔️"
                    outcome_color = "green"
                elif outcome[0]==4:
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

# Create a label and an entry field for row count
row_count_label = Label(window, text="Number of Rows:")
row_count_label.grid(row=0, column=3)

entry = Entry(window, width=5)  # Assuming you use Entry field to capture the row count
entry.grid(row=0, column=4)
entry.insert(0,1)

# Add a button to trigger the retrieval with the specified row count
retrieve_button = Button(window, text="Retrieve", command=update_results)
retrieve_button.grid(row=0, column=5)

# Populate the job and outcome listboxes
update_results()

# Configure listbox item colors
job_listbox.itemconfig("end", fg="black")
outcome_listbox.itemconfig("end", fg="black")

# Remove the last empty item in job_listbox
job_listbox.delete("end")

# Start the Tkinter event loop
window.iconbitmap(os.path.join(basedir, "icon.ico"))
window.mainloop()
