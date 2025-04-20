import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
import threading
import re

class PhishingDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Website Detector")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 14))
        self.style.configure("TEntry", font=("Helvetica", 12))

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Title
        self.title_label = ttk.Label(
            self.main_frame,
            text="Phishing Website Detector",
            style="primary.TLabel",
            font=("Helvetica", 18, "bold")
        )
        self.title_label.pack(pady=10)

        # URL input
        self.url_frame = ttk.Frame(self.main_frame)
        self.url_frame.pack(fill=X, pady=10)

        self.url_label = ttk.Label(self.url_frame, text="Enter URL:", style="TLabel")
        self.url_label.pack(side=LEFT)

        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.pack(side=LEFT, padx=10, fill=X, expand=True)
        self.url_entry.insert(0, "https://govastly.com/")

        # Check button
        self.check_button = ttk.Button(
            self.main_frame,
            text="Check URL",
            style="success.TButton",
            command=self.check_url
        )
        self.check_button.pack(pady=20)

        # Result display
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_frame.pack(fill=BOTH, pady=10)

        self.status_label = ttk.Label(
            self.result_frame,
            text="Status: Waiting...",
            style="TLabel",
            font=("Helvetica", 16, "bold")
        )
        self.status_label.pack()

        self.message_label = ttk.Label(
            self.result_frame,
            text="",
            style="TLabel",
            wraplength=500
        )
        self.message_label.pack(pady=5)

        # Loading spinner
        self.spinner = ttk.Label(self.main_frame, text="", font=("Helvetica", 12))
        self.spinner.pack()

        # Loading animation state
        self.loading = False
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0

    def update_spinner(self):
        if self.loading:
            self.spinner.configure(text=self.spinner_chars[self.spinner_index])
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            self.root.after(100, self.update_spinner)

    def check_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        if not re.match(r'^https?://', url):
            url = "https://" + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)

        self.check_button.configure(state=DISABLED)
        self.status_label.configure(text="Status: Checking...", foreground="orange")
        self.message_label.configure(text="")
        self.loading = True
        self.update_spinner()

        # Run server request in a separate thread
        threading.Thread(target=self.send_request, args=(url,), daemon=True).start()

    def send_request(self, url):
        try:
           
            response = requests.post(
                "http://localhost:5051/predict",
                json={"url": url},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            status = "Suspicious" if data.get("phishing") else "Legit"
            message = data.get("message", "No message provided")
            color = "red" if data.get("phishing") else "green"

            self.root.after(0, lambda: self.update_result(status, message, color))
        except requests.RequestException as e:
            self.root.after(0, lambda: self.show_error(f"Error: Could not connect to server. {str(e)}"))
        finally:
            self.root.after(0, self.stop_loading)

    def update_result(self, status, message, color):
        self.status_label.configure(text=f"Status: {status}", foreground=color)
        self.message_label.configure(text=message)

    def show_error(self, error_message):
        self.status_label.configure(text="Status: Error", foreground="orange")
        self.message_label.configure(text=error_message)
        messagebox.showerror("Error", error_message)

    def stop_loading(self):
        self.loading = False
        self.spinner.configure(text="")
        self.check_button.configure(state=NORMAL)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = PhishingDetectorGUI(root)
    root.mainloop()