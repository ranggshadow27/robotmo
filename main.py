# main.py — FINAL FIX LOG GAK KEDIP LAGI 100% JALAN
import customtkinter as ctk
from ui.xgui import RoboTMOAppUI
from core.logic import TMOLogic
from utils.config import modal_tmo_configs, modal_tmo_action, sn_device_configs, file_input_configs

import requests
from datetime import datetime
import pytz
from tkinter import messagebox
import threading
import sys

# ================== REDIRECT PRINT KE TEXTBOX ==================
# ================== REDIRECT PRINT KE TEXTBOX (FIXED: SELALU BARIS BARU!) ==================
class TextboxRedirector:
    def __init__(self, textbox):
        self.textbox = textbox
        self.buffer = ""  # Simpan teks sementara

    def write(self, text):
        if not text:
            return

        self.buffer += text

        # Kalau ada newline atau tanda ">" (log dari logic.py), langsung tulis ke textbox
        while '\n' in self.buffer or self.buffer.endswith('> '):
            # Split berdasarkan newline atau tanda ">" yang biasa dipake di logic.py
            if '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
            else:
                # Kalau nggak ada \n, tapi ada "> " di akhir → potong per log
                if self.buffer.endswith('> '):
                    line = self.buffer
                    self.buffer = ""
                else:
                    break  # Belum lengkap, tunggu dulu

            if line.strip():  # Kalau bukan kosong
                self.textbox.configure(state="normal")
                self.textbox.insert("end", line + "\n")  # PAKSA TAMBAH \n!
                self.textbox.see("end")
                self.textbox.configure(state="disabled")

    def flush(self):
        # Kalau ada sisa buffer, tulis juga (biar aman)
        if self.buffer.strip():
            self.textbox.configure(state="normal")
            self.textbox.insert("end", self.buffer + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")
            self.buffer = ""

# ================== VALIDASI AKSES ==================
API_URL = "https://script.google.com/macros/s/AKfycbyGv08iyugoWolQlg2AGZzZxooQy3nqd_S1x7n5GOTH0mwlqz-FpbldIuMPp-HJMwKI/exec?app_type=tmo_automation"
DEFAULT_TOKEN = "MHG_tmoAutomation@ratiPRAY"

def validate_access(callback):
    def run():
        try:
            r = requests.get(API_URL, timeout=12)
            data = r.json()
            if data.get("token") != DEFAULT_TOKEN:
                callback(False, "Key Error")
                return
            exp = datetime.fromisoformat(data.get("expired", "").replace("Z", "+00:00"))
            if datetime.now(pytz.timezone("Asia/Jakarta")) > exp.astimezone(pytz.timezone("Asia/Jakarta")):
                callback(False, "Failed Compile Data")
                return
            callback(True, "Automation Authorized!")
        except:
            callback(False, "Failed to Authorized")
    threading.Thread(target=run, daemon=True).start()

# ================== MAIN APP ==================
if __name__ == "__main__":
    root = ctk.CTk()
    config = { 'modal_tmo_configs': modal_tmo_configs, 'modal_tmo_action': modal_tmo_action,
               'sn_device_configs': sn_device_configs, 'file_input_configs': file_input_configs }
    logic = TMOLogic(config)
    app = RoboTMOAppUI(root, lambda **kw: None)

    def run_autofill_callback(**kwargs):
        kwargs['excel_file'] = None
        kwargs['tmo_type'] = app.tmo_type_combobox.get()
        kwargs['show_error'] = app.show_error
        kwargs['show_info'] = app.show_info
        logic.run_autofill(**kwargs)

    app.run_autofill_callback = run_autofill_callback
    app.update_log_active = True  # Tambah flag

    def start_tmo_with_validation():
        app.progress_bar.set(0)
        app.log_textbox.configure(state="normal")
        app.log_textbox.delete("1.0", "end")
        app.log_textbox.insert("end", "[INFO] Memulai validasi...\n")
        app.log_textbox.configure(state="disabled")
        app.button_go.configure(state="disabled", text="Automation is running...")
        app.button_extractor.configure(state="disabled")

        def on_validasi(sukses, msg):
            root.after(0, lambda: mulai_autofill(sukses, msg))

        def mulai_autofill(sukses, msg):
            app.log_textbox.configure(state="normal")
            app.log_textbox.insert("end", f"[VALIDASI] {msg}\n")
            app.log_textbox.configure(state="disabled")

            if not sukses:
                messagebox.showerror("Akses Ditolak", msg)
                app.button_go.configure(state="normal", text="Start TMO")
                app.button_extractor.configure(state="normal")
                return

            # MATIKAN update_log BIAR GAK BENTROK
            app.update_log_active = False

            # Redirect semua print ke textbox
            sys.stdout = TextboxRedirector(app.log_textbox)
            sys.stderr = TextboxRedirector(app.log_textbox)

            app.is_running = True

            def jalankan():
                try:
                    run_autofill_callback(
                        username=app.entry_username.get(),
                        password=app.entry_password.get(),
                        image_dir=app.image_dir,
                        search_type=app.search_type_combobox.get(),
                        progress_callback=app.update_progress
                    )
                finally:
                    app.is_running = False
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                    app.update_log_active = True  # Nyalain lagi
                    root.after(100, app.update_log)
                    root.after(0, lambda: app.button_go.configure(state="normal", text="Start TMO"))
                    root.after(0, lambda: app.button_extractor.configure(state="normal"))

            threading.Thread(target=jalankan, daemon=True).start()

        validate_access(on_validasi)

    app.button_go.configure(command=start_tmo_with_validation)
    root.protocol("WM_DELETE_WINDOW", lambda: [logic.cleanup(), root.destroy()])
    root.mainloop()