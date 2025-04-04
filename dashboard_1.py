import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import csv

# === FUNCTIONS ===
def start_scraper():
    progress_bar.start()
    log_box.insert(tk.END, "\n Starting Discord Channel Member Scraper...\n")
    log_box.see(tk.END)
    threading.Thread(target=run_scraper_process, daemon=True).start()

def run_scraper_process():
    try:
        process = subprocess.Popen(["src/discord_scrape.exe"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            log_box.insert(tk.END, line)
            log_box.see(tk.END)
        process.stdout.close()
        process.wait()
        log_box.insert(tk.END, "\n Process complete!\n")
    except Exception as e:
        log_box.insert(tk.END, f"\n Error: {e}\n")
    finally:
        progress_bar.stop()
def view_scraped_members():
    """Opens a modal with a table view of scraped Discord members."""
    if not os.path.exists("discord_scraped_members.csv"):
        messagebox.showerror("Error", "discord_scraped_members.csv not found!")
        return

    # Create a new top-level modal window
    modal = tk.Toplevel(window)
    modal.title("Scraped Discord Members")
    modal.geometry("700x400")
    modal.configure(bg="#102542")

    # Title Label
    title = tk.Label(modal, text="Extracted Discord Members", font=("Helvetica", 14, "bold"), fg="white", bg="#102542")
    title.pack(pady=10)

    # Frame for the table
    frame = tk.Frame(modal, bg="#102542")
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Create Treeview (Table)
    columns = ("#", "Username", "User ID", "Join Date")  # Adjust according to CSV structure
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

    # Define column headings
    tree.heading("#", text="#")
    tree.heading("Username", text="Server Name")
    tree.heading("User ID", text="Server Link")
    tree.heading("Join Date", text="Member")

    # Set column widths (auto-adjusting)
    tree.column("#", width=50, anchor="center")
    tree.column("Username", width=200, anchor="w")
    tree.column("User ID", width=150, anchor="center")
    tree.column("Join Date", width=150, anchor="center")

    # Add scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    tree.pack(fill=tk.BOTH, expand=True)

    # Read CSV and insert data into the table
    try:
        with open("discord_scraped_members.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for idx, row in enumerate(reader, start=1):
                tree.insert("", "end", values=(idx, *row))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data: {e}")

    # Make sure the table fills available space
    frame.pack_propagate(False)

    # Close button
    close_button = tk.Button(modal, text="Close", command=modal.destroy, font=("Helvetica", 12, "bold"),
                             bg="#DC3545", fg="white", padx=10, pady=5, relief="flat", cursor="hand2")
    close_button.pack(pady=10)

# === TKINTER UI ===
window = tk.Tk()
window.title("Discord Channel Member Scraper")
window.geometry("700x550")
window.resizable(False, False)
window.configure(bg="#0A1F44")  # Dark blue background

# Title Label
title_label = tk.Label(window, text="2: Get Channel Members", font=("Helvetica", 20, "bold"), fg="white", bg="#0A1F44")
title_label.pack(pady=20)

# Start Button
start_button = tk.Button(
    window, text="Start Scraping", command=start_scraper, font=("Helvetica", 14, "bold"),
    bg="#DC3545", fg="white", activebackground="#C82333", activeforeground="white",
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", highlightthickness=0
)
start_button.pack(pady=10, ipadx=10, ipady=5)

# View Scraped Members Button
view_members_button = tk.Button(
    window, text="View Scraped Members", command=view_scraped_members, font=("Helvetica", 14, "bold"),
    bg="#17A2B8", fg="white", activebackground="#138496", activeforeground="white",
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", highlightthickness=0
)
view_members_button.pack(pady=10, ipadx=10, ipady=5)

# Progress Bar
style = ttk.Style()
style.theme_use('default')
style.configure("blue.Horizontal.TProgressbar", background="#1E90FF")

progress_bar = ttk.Progressbar(window, orient=tk.HORIZONTAL, mode='indeterminate', length=400, style="blue.Horizontal.TProgressbar")
progress_bar.pack(pady=10)

# Log Box Frame for card-like effect
log_frame = tk.Frame(window, bg="#102542", bd=2, relief="ridge")
log_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

# Log Box Title
log_title = tk.Label(log_frame, text="UPDATES", font=("Helvetica", 12, "bold"), fg="white", bg="#102542")
log_title.pack(anchor='w', padx=10, pady=(10, 0))

# Log Output Box
log_box = scrolledtext.ScrolledText(
    log_frame, width=80, height=18, font=("Consolas", 10),
    bg="#102542", fg="#00FFCC", insertbackground="white",
    borderwidth=0, relief="flat"
)
log_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Run the Tkinter event loop
window.mainloop()
