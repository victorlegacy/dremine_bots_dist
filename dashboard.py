import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os

# === FUNCTIONS ===
def start_scraper():
    progress_bar.start()
    log_box.insert(tk.END, "\n Starting Twitter Account Scraper...\n")
    log_box.see(tk.END)
    threading.Thread(target=run_scraper_process, daemon=True).start()

def run_scraper_process():
    try:
        process = subprocess.Popen(["python", "src/twitter_scrape.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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

def view_discord_links():
    """Opens a modal to display Discord links from 'twitter_discord_links.csv'."""
    if not os.path.exists("twitter_discord_links.csv"):
        messagebox.showerror("Error", "twitter_discord_links.csv not found!")
        return

    # Create a new top-level window (modal)
    modal = tk.Toplevel(window)
    modal.title("Discord Links")
    modal.geometry("600x400")
    modal.configure(bg="#102542")

    # Title Label
    title = tk.Label(modal, text="Extracted Discord Links", font=("Helvetica", 14, "bold"), fg="white", bg="#102542")
    title.pack(pady=10)

    # Scrollable text box to show links
    discord_textbox = scrolledtext.ScrolledText(modal, width=70, height=20, font=("Consolas", 10), bg="#1A1A1A", fg="#00FFCC")
    discord_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Read and display the CSV content
    with open("twitter_discord_links.csv", "r", encoding="utf-8") as file:
        content = file.read()
        discord_textbox.insert(tk.END, content)

    discord_textbox.config(state=tk.DISABLED)  # Make it read-only

# === TKINTER UI ===
window = tk.Tk()
window.title("Twitter Discord Link Scraper")
window.geometry("700x550")
window.resizable(False, False)
window.configure(bg="#0A1F44")  # Dark blue background

# Title Label
title_label = tk.Label(window, text="1: X Profile Scrape", font=("Helvetica", 20, "bold"), fg="white", bg="#0A1F44")
title_label.pack(pady=20)

# Start Button
start_button = tk.Button(
    window, text="Start Scraping", command=start_scraper, font=("Helvetica", 14, "bold"),
    bg="#1E90FF", fg="white", activebackground="#4682B4", activeforeground="white",
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", highlightthickness=0
)
start_button.pack(pady=10, ipadx=10, ipady=5)

# View Discord Links Button
view_links_button = tk.Button(
    window, text="View Discord Links", command=view_discord_links, font=("Helvetica", 14, "bold"),
    bg="#28A745", fg="white", activebackground="#218838", activeforeground="white",
    relief="flat", bd=0, padx=20, pady=10, cursor="hand2", highlightthickness=0
)
view_links_button.pack(pady=10, ipadx=10, ipady=5)

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
