import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from io import StringIO
import sys
from contextlib import redirect_stdout

class RoboTMOAppUI:
    def __init__(self, root, run_autofill_callback):
        self.root = root
        self.root.title("RoboTMO Instalation")
        self.root.geometry("360x520")  # Increased height for progress bar and log
        self.root.iconbitmap("mhg-ai-robo-inst.ico")
        ctk.set_appearance_mode("Dark")
        # ctk.set_default_color_theme("dark-blue")
        self.run_autofill_callback = run_autofill_callback
        self.log_stream = StringIO()
        self.is_running = False
        self.lock = threading.Lock()
        self.log_lines = []  # Store log lines to limit to 20

        # Konfigurasi grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), weight=1)

        # Row 1: Title
        self.label_title = ctk.CTkLabel(self.root, text="⚡ RoboTMO Instalation ⚡", font=("Inter", 14, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2)

        # Row 2: Login Info Label
        self.label_login = ctk.CTkLabel(self.root, text="NOC | Mahaga's Spearhead ", font=("Inter", 12))
        self.label_login.grid(row=1, column=0, columnspan=2, sticky="we")

        # Row 3: Login Info Label
        self.label_login = ctk.CTkLabel(self.root, text="CBOSS Login :", font=("Inter", 12))
        self.label_login.grid(row=2, column=0, padx=10, sticky="w")

        # Row 4: Username and Password
        self.entry_username = ctk.CTkEntry(self.root, placeholder_text="Username", font=("Inter", 12))
        self.entry_username.grid(row=3, column=0, padx=10, sticky="ew")
        self.entry_password = ctk.CTkEntry(self.root, placeholder_text="Password", show="•", font=("Inter", 13))
        self.entry_password.grid(row=3, column=1, padx=10, sticky="ew")

        # Row 5: Search Type Label
        self.label_search_type = ctk.CTkLabel(self.root, text="TMO Search Type :", font=("Inter", 12))
        self.label_search_type.grid(row=4, column=0, padx=10, sticky="w")

        # Row 6: Search Type Combobox
        self.search_type_combobox = ctk.CTkComboBox(
            self.root,
            values=["SPK NUMBER", "SO NUMBER", "SUBSCRIBER NUMBER", "SUBSCRIBER NAME"],
            font=("Inter", 12),
            state="readonly"
        )
        self.search_type_combobox.set("SPK NUMBER")
        self.search_type_combobox.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew")

        # Row 7: Image Directory Label
        self.label_image_dir = ctk.CTkLabel(self.root, text="Select Image Directory :", font=("Inter", 12))
        self.label_image_dir.grid(row=6, column=0, padx=10, sticky="w")

        # Row 8: Image Directory Selection
        self.button_image_dir = ctk.CTkButton(self.root, text="Choose", fg_color="#535353", hover_color="#676767", command=self.choose_image_dir, font=("Inter", 12))
        self.button_image_dir.grid(row=7, column=0, padx=10, sticky="w")
        self.label_image_path = ctk.CTkLabel(self.root, text="❎ No directory selected", font=("Inter", 12), text_color="#ff595e")
        self.label_image_path.grid(row=7, column=1, padx=10, sticky="w")

        # Row 9: Excel File Label
        self.label_excel = ctk.CTkLabel(self.root, text="Select Excel File :", font=("Inter", 12))
        self.label_excel.grid(row=8, column=0, padx=10, sticky="w")

        # Row 10: Excel File Selection
        self.button_excel = ctk.CTkButton(self.root, text="Choose", fg_color="#535353", hover_color="#676767", command=self.choose_excel_file, font=("Inter", 12))
        self.button_excel.grid(row=9, column=0, padx=10, sticky="w")
        self.label_excel_path = ctk.CTkLabel(self.root, text="❎ No file selected", font=("Inter", 12), text_color="#ff595e")
        self.label_excel_path.grid(row=9, column=1, padx=10, sticky="w")

        # Row 11: Copyright
        self.label_copyright = ctk.CTkLabel(self.root, text="©ratipray", font=("Inter", 10, 'bold'), text_color="#505050")
        self.label_copyright.grid(row=10, column=0, columnspan=2, sticky="we")

        # Row 12: Go Button
        self.button_go = ctk.CTkButton(self.root, text="Start TMO",fg_color="#A30052", hover_color="#CC0066", command=self.start_autofill, font=("Inter", 12, 'bold'))
        self.button_go.grid(row=11, column=0, columnspan=2, padx=10, sticky="ew")

        # Row 13: Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.root, progress_color="#A30052")
        self.progress_bar.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)

        # Row 14: Log Textbox
        self.log_textbox = ctk.CTkTextbox(self.root, height=100, font=("Inter", 12))
        self.log_textbox.grid(row=13, column=0, columnspan=2, padx=10, pady=6, sticky="nsew")
        self.log_textbox.insert("0.0", "Waiting for Start...\n")
        self.log_textbox.configure(state="disabled")

        # Variables to store paths
        self.image_dir = ""
        self.excel_file = ""

        # Start log update loop
        self.update_log()

    def choose_image_dir(self):
        self.image_dir = filedialog.askdirectory(title="Select Image Directory")
        if self.image_dir:
            self.label_image_path.configure(text=f"Selected : {os.path.basename(self.image_dir)} ✅")
            self.label_image_path.configure(text_color="#57cc99")

    def choose_excel_file(self):
        self.excel_file = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel files", "*.xlsx *.xls")])
        if self.excel_file:
            self.label_excel_path.configure(text=f"Selected : {os.path.basename(self.excel_file)} ✅")
            self.label_excel_path.configure(text_color="#57cc99")

    def update_log(self):
        if self.is_running:
            with self.lock:
                # Get new log content
                new_log = self.log_stream.getvalue()
                # Split into lines and keep only the last 20
                self.log_lines = new_log.splitlines()[-20:]
                # Update textbox
                self.log_textbox.configure(state="normal")
                self.log_textbox.delete("1.0", "end")
                self.log_textbox.insert("1.0", "\n".join(self.log_lines) + "\n")
                # Scroll to the bottom
                self.log_textbox.see("end")
                self.log_textbox.configure(state="disabled")
        self.root.after(100, self.update_log)

    def start_autofill(self):
        if not self.entry_username.get():
            messagebox.showerror("Error", "Please enter username")
            return
        if not self.entry_password.get():
            messagebox.showerror("Error", "Please enter password")
            return
        if not self.image_dir:
            messagebox.showerror("Error", "Please select image directory")
            return
        if not self.excel_file:
            messagebox.showerror("Error", "Please select Excel file")
            return

        self.button_go.configure(state="disabled")
        self.is_running = True
        self.log_stream = StringIO()
        self.log_lines = []
        self.progress_bar.set(0)

        def run_in_thread():
            with redirect_stdout(self.log_stream):
                try:
                    self.run_autofill_callback(
                        username=self.entry_username.get(),
                        password=self.entry_password.get(),
                        image_dir=self.image_dir,
                        excel_file=self.excel_file,
                        search_type=self.search_type_combobox.get(),
                        progress_callback=self.update_progress
                    )
                finally:
                    self.is_running = False
                    self.root.after(0, lambda: self.button_go.configure(state="normal"))

        threading.Thread(target=run_in_thread, daemon=True).start()

    def update_progress(self, value):
        self.progress_bar.set(value)

    def show_error(self, message):
        self.root.after(0, lambda: messagebox.showerror("Error", message))

    def show_info(self, message):
        def reset_ui():
            self.progress_bar.set(0)
            self.log_lines = []
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("1.0", "Waiting for Start...\n")
            self.log_textbox.configure(state="disabled")

        self.root.after(0, lambda: [messagebox.showinfo("Success", message), reset_ui()])

    def destroy(self):
        self.is_running = False
        self.root.destroy()