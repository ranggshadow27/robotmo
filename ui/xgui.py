import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from io import StringIO
import sys
from contextlib import redirect_stdout
from core.logic import TMOLogic
from ui.fgui import create_extractor_toplevel  # Import dari fgui

class RoboTMOAppUI:
    def __init__(self, root, run_autofill_callback):
        self.root = root
        self.root.title("RoboTMO")
        self.root.geometry("360x620")
        self.root.minsize(360, 620)
        self.root.maxsize(360, 620)
        self.root.iconbitmap("mhg-ai-robo-inst.ico")  # Kalau ada icon
        ctk.set_appearance_mode("Dark")
        self.run_autofill_callback = run_autofill_callback
        self.log_stream = StringIO()
        self.is_running = False
        self.lock = threading.Lock()
        self.log_lines = []

        # Grid config (asli)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), weight=1)

        # Row 0: Title (asli)
        self.label_title = ctk.CTkLabel(self.root, text="⚡ RoboTMO ⚡", font=("Inter", 14, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2)

        # Row 1-2: Login Info (asli)
        self.label_login = ctk.CTkLabel(self.root, text="NOC | Mahaga's Spearhead ", font=("Inter", 12))
        self.label_login.grid(row=1, column=0, columnspan=2, sticky="we")
        self.label_login = ctk.CTkLabel(self.root, text="CBOSS Login :", font=("Inter", 12))
        self.label_login.grid(row=2, column=0, padx=10, sticky="w")

        # Row 3: Username & Password (asli)
        self.entry_username = ctk.CTkEntry(self.root, placeholder_text="Username", font=("Inter", 12))
        self.entry_username.grid(row=3, column=0, padx=10, sticky="ew")
        self.entry_password = ctk.CTkEntry(self.root, placeholder_text="Password", show="•", font=("Inter", 13))
        self.entry_password.grid(row=3, column=1, padx=10, sticky="ew")

        # Row 4-5: TMO Type (BARU!)
        self.label_tmo_type = ctk.CTkLabel(self.root, text="TMO Type :", font=("Inter", 12))
        self.label_tmo_type.grid(row=4, column=0, padx=10, sticky="w")
        self.tmo_type_combobox = ctk.CTkComboBox(
            self.root,
            values=["Instalasi", "Maintenance"],
            font=("Inter", 12),
            state="readonly"
        )
        self.tmo_type_combobox.set("Maintenance")  # Default
        self.tmo_type_combobox.grid(row=5, column=0, columnspan=2, padx=10, sticky="ew")

        # Row 6-7: Search Type (geser ke bawah)
        self.label_search_type = ctk.CTkLabel(self.root, text="TMO Search Type :", font=("Inter", 12))
        self.label_search_type.grid(row=6, column=0, padx=10, sticky="w")
        self.search_type_combobox = ctk.CTkComboBox(
            self.root,
            values=["SPK NUMBER", "ST NUMBER", "SUBSCRIBER NUMBER", "SUBSCRIBER NAME"],
            font=("Inter", 12),
            state="readonly"
        )
        self.search_type_combobox.set("SPK NUMBER")
        self.search_type_combobox.grid(row=7, column=0, columnspan=2, padx=10, sticky="ew")

        # Row 8-9: Image Directory (geser lagi)
        self.label_image_dir = ctk.CTkLabel(self.root, text="Select Image Directory :", font=("Inter", 12))
        self.label_image_dir.grid(row=8, column=0, padx=10, sticky="w")
        self.button_image_dir = ctk.CTkButton(self.root, text="Choose", fg_color="#535353", hover_color="#676767", command=self.choose_image_dir, font=("Inter", 12))
        self.button_image_dir.grid(row=9, column=0, padx=10, sticky="w")
        self.label_image_path = ctk.CTkLabel(self.root, text="No directory selected", font=("Inter", 12), text_color="#ff595e")
        self.label_image_path.grid(row=9, column=1, padx=10, sticky="w")

        # Row 10-11: Data Extractor
        self.label_extractor = ctk.CTkLabel(self.root, text="Data Extractor :", font=("Inter", 12))
        self.label_extractor.grid(row=10, column=0, padx=10, sticky="w")
        self.button_extractor = ctk.CTkButton(
            self.root,
            text="Open Data Extractor",
            font=("Inter", 12, 'bold'),
            fg_color="#535353",
            hover_color="#676767",
            command=self.open_data_extractor
        )
        self.button_extractor.grid(row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Row 12: Copyright
        self.label_copyright = ctk.CTkLabel(self.root, text="©ratipray", font=("Inter", 10, 'bold'), text_color="#505050")
        self.label_copyright.grid(row=12, column=0, columnspan=2, sticky="we", pady=(0, 0))

        # Row 13: Start Button
        self.button_go = ctk.CTkButton(
            self.root,
            text="Start TMO",
            font=("Inter", 12, 'bold'),
            command=self.start_tmo
        )
        self.button_go.grid(row=13, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Row 14: Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.root)
        self.progress_bar.grid(row=14, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # Row 15: Log
        self.log_textbox = ctk.CTkTextbox(self.root, height=120, font=("Inter", 12))
        self.log_textbox.grid(row=15, column=0, columnspan=2, padx=10, pady=(6,10), sticky="nsew")
        self.log_textbox.insert("0.0", "Waiting for Start...\n")
        self.log_textbox.configure(state="disabled")

        self.image_dir = ""
        self.update_log()

    def choose_image_dir(self):
        self.image_dir = filedialog.askdirectory(title="Select Image Directory")
        if self.image_dir:
            self.label_image_path.configure(text=f"Selected :\n{os.path.basename(self.image_dir)} ✅", text_color="#57cc99")

    def open_data_extractor(self):
        create_extractor_toplevel(self.root)  # Panggil fgui asli

    def start_tmo(self):
        if not self.entry_username.get():
            messagebox.showerror("Error", "Please enter username")
            return
        if not self.entry_password.get():
            messagebox.showerror("Error", "Please enter password")
            return
        if not self.image_dir:
            messagebox.showerror("Error", "Please select image directory")
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
                        search_type=self.search_type_combobox.get(),  # Pass search_type asli
                        progress_callback=self.update_progress
                    )
                finally:
                    self.is_running = False
                    self.root.after(0, lambda: self.button_go.configure(state="normal"))

        threading.Thread(target=run_in_thread, daemon=True).start()

    def update_progress(self, value):
        self.progress_bar.set(value)

    def update_log(self):
        if getattr(self, 'update_log_active', True):
            if self.is_running:
                with self.lock:
                    new_log = self.log_stream.getvalue()
                    lines = new_log.splitlines()[-50:]
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.delete("1.0", "end")
                    self.log_textbox.insert("1.0", "\n".join(lines) + "\n")
                    self.log_textbox.see("end")
                    self.log_textbox.configure(state="disabled")
            self.root.after(100, self.update_log)

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

        def show_and_unblock():
            messagebox.showinfo("Info", message)
            reset_ui()
            # UNBLOCK THREAD YANG NUNGGU OTP
            if hasattr(TMOLogic, 'otp_wait_event') and TMOLogic.otp_wait_event:
                TMOLogic.otp_wait_event.set()

        self.root.after(0, show_and_unblock)

    def destroy(self):
        self.is_running = False
        self.root.destroy()