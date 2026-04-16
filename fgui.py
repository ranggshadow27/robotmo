# fgui.py (FINAL - LENGKAP + SAVE TO JSON) — AS Toplevel

import customtkinter as ctk
import threading
import os
import json
import re
from tkinter import messagebox
from automation import run_full_extractor

def create_extractor_toplevel(master):
    if hasattr(master, "extractor_window") and master.extractor_window.winfo_exists():
        master.extractor_window.lift()
        return

    win = ctk.CTkToplevel(master)
    win.title("TMO Extractor Tool")
    win.geometry("920x720")
    win.minsize(920, 720)
    master.extractor_window = win
    win.transient(master)
    win.grab_set()
    # root.iconbitmap("mhg-ai-robo-inst.ico")  # Kalau ada icon
    

    # Setting tema
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Font
    try:
        roboto_font     = ("Roboto", 10)
        roboto_textbox  = ("Roboto", 12)
        roboto_bold     = ("Roboto", 12, "bold")
        roboto_title    = ("Roboto", 12, "bold")
    except:
        roboto_font     = ("Segoe UI", 10)
        roboto_textbox  = ("Segoe UI", 12)
        roboto_bold     = ("Segoe UI", 12, "bold")
        roboto_title    = ("Segoe UI", 14, "bold")

    win.option_add("*Font", roboto_font)

    # Main container
    main_container = ctk.CTkFrame(win, corner_radius=15, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=10, pady=20)
    main_container.grid_rowconfigure(0, weight=2)
    main_container.grid_rowconfigure(1, weight=1)
    main_container.grid_columnconfigure(0, weight=1)

    # TOP FRAME
    top_frame = ctk.CTkFrame(main_container)
    top_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

    # LEFT PANEL
    left_panel = ctk.CTkFrame(top_frame, width=240, corner_radius=12)
    left_panel.pack(side="left", fill="both", padx=(0, 8))
    left_panel.pack_propagate(False)

    ctk.CTkLabel(left_panel, text="Request TMO ID", font=roboto_title).pack(anchor="w", padx=10, pady=(5, 5))
    entry_tmo = ctk.CTkEntry(left_panel, placeholder_text="Masukkan TMO ID di sini...", height=30, font=roboto_bold)
    entry_tmo.pack(fill="x", padx=10, pady=(0, 5))

    ctk.CTkLabel(left_panel, text="Power Source", font=roboto_bold).pack(anchor="w", padx=10, pady=(5, 2))
    combo_source = ctk.CTkComboBox(left_panel, values=['PLN', 'Genset', 'PLTS', 'PLTMH'], font=roboto_bold)
    combo_source.set("PLN")
    combo_source.pack(fill="x", padx=10, pady=(0, 0))

    ctk.CTkLabel(left_panel, text="Backup Power", font=roboto_bold).pack(anchor="w", padx=10, pady=(5, 2))
    combo_backup = ctk.CTkComboBox(left_panel, values=['PLN', 'Genset', 'PLTS', 'PLTMH', '-'], font=roboto_bold)
    combo_backup.set("-")
    combo_backup.pack(fill="x", padx=10, pady=(0, 0))

    ctk.CTkLabel(left_panel, text="Action", font=roboto_bold).pack(anchor="w", padx=10, pady=(5, 2))
    combo_action = ctk.CTkComboBox(left_panel, values=[
        'MENYALAKAN PERANGKAT','MODEM 2300', 'MODEM 2010','ADAPTOR MODEM 2300', 'ADAPTOR MODEM 2010',
        'RECONFIG MODEM', 'ROUTER MIKROTIK','ROUTER GRANDSTREAM','RECONFIG ROUTER GRANDSTREAM',
        'RECONFIG ROUTER MIKROTIK','ADAPTOR ROUTER MIKROTIK','ADAPTOR ROUTER GRANDSTREAM',
        'REPOINTING', 'TRANSCEIVER HB220','TRANSCEIVER REVGO','TRANSCEIVER SKYWARE', 'STABILIZER', 
        'POE AP1', 'POE AP2', 'AP1', 'AP2',
        'KABEL LAN', 'KABEL IFL', 'KONEKTOR', 'REPOSISI', 'RELOKASI', 'TERMINAL POWER','PM', 'INSTALASI'
    ], font=roboto_bold)
    combo_action.set("PM")
    combo_action.pack(fill="x", padx=10, pady=(0, 0))

    # Login window (asli)
    CREDENTIAL_FILE = "login_credentials.txt"
    def load_credentials():
        if os.path.exists(CREDENTIAL_FILE):
            with open(CREDENTIAL_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                user = lines[0].split(":", 1)[1].strip() if lines else "noc.mahaga"
                pw = lines[1].split(":", 1)[1].strip() if len(lines) > 1 else "Shiftnoc123"
                return user, pw
        return "noc.mahaga", "Shiftnoc123"

    default_user, default_pw = load_credentials()

    def open_login_window():
        login_win = ctk.CTkToplevel(win)
        login_win.title("Login Information")
        login_win.geometry("300x360")
        login_win.resizable(False, False)
        login_win.transient(win)
        login_win.grab_set()

        frame = ctk.CTkFrame(login_win, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Login Credentials", font=roboto_title).pack(pady=(0, 20))

        ctk.CTkLabel(frame, text="Username", font=roboto_bold, anchor="w").pack(fill="x", pady=(0, 4))
        entry_user = ctk.CTkEntry(frame, font=roboto_textbox, height=32)
        entry_user.insert(0, default_user)
        entry_user.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(frame, text="Password", font=roboto_bold, anchor="w").pack(fill="x", pady=(0, 4))
        entry_pass = ctk.CTkEntry(frame, show="*", font=roboto_textbox, height=32)
        entry_pass.insert(0, default_pw)
        entry_pass.pack(fill="x", pady=(0, 15))

        show_var = ctk.BooleanVar()
        def toggle_password():
            entry_pass.configure(show="" if show_var.get() else "*")
        ctk.CTkCheckBox(frame, text="Show Password", variable=show_var, font=roboto_textbox, checkbox_width=15,checkbox_height=15, command=toggle_password).pack(pady=(0, 20))

        def save_and_close():
            user = entry_user.get().strip()
            pw = entry_pass.get().strip()
            if user and pw:
                with open(CREDENTIAL_FILE, "w", encoding="utf-8") as f:
                    f.write(f"Username: {user}\nPassword: {pw}\n")
                global default_user, default_pw
                default_user, default_pw = user, pw
            login_win.destroy()

        ctk.CTkButton(frame, 
                      text="Close (Auto Save)", 
                      fg_color="#535353",
            hover_color="#676767",
            height=38, font=roboto_bold,
                      command=save_and_close).pack(fill="x")

    ctk.CTkButton(left_panel, text="Login Information", height=28, font=roboto_bold, fg_color="#535353", command=open_login_window).pack(fill="x", padx=10, pady=(15, 0))

    show_browser_var = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(left_panel, text="Show Browser (debug)", font=roboto_textbox, variable=show_browser_var, checkbox_width=15,checkbox_height=15).pack(anchor="w", padx=10, pady=(10,0))

    skip_image_var = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(left_panel, text="Skip Image/BA Download (Fast)", 
                    font=roboto_textbox, variable=skip_image_var, 
                    checkbox_width=15, checkbox_height=15).pack(anchor="w", padx=10, pady=(5,0))
    
    generate_button = ctk.CTkButton(left_panel, text="Generate Extractor", height=28, font=roboto_bold, fg_color="#1f6aa5")
    
    def start_extraction():
        generate_button.configure(state="disabled", text="Extractor is running...")
        threading.Thread(target=run_full_extractor, args=(
            entry_tmo, combo_source, combo_backup, combo_action,
            textbox_source, textbox_extracted, textbox_log, textbox_problem,
            default_user, default_pw, 
            show_browser_var.get(),
            skip_image_var.get(),  # ← KIRIM STATUS SKIP IMAGE KE automation.py
            lambda: generate_button.configure(state="normal", text="Generate Extractor")
        ), daemon=True).start()

    generate_button.configure(command=start_extraction)
    generate_button.pack(fill="x", padx=10, pady=(20, 0))

    # Save to JSON (asli)
    def save_to_json():
        tmo_id = entry_tmo.get().strip()
        if not tmo_id:
            messagebox.showwarning("TMO ID Kosong", "Isi TMO ID dulu!")
            return

        extracted_text = textbox_extracted.get("1.0", "end-1c").strip()
        if not extracted_text or "SPMK" not in extracted_text:
            messagebox.showwarning("Belum Ada Data", "Lakukan Generate Extractor dulu!")
            return

        problem_text = textbox_problem.get("1.0", "end-1c").strip()

        data = {
            "tmo_id": tmo_id,
            "spmk": "Unknown",
            "nama_pic": "", "no_pic": "", "nama_teknisi": "", "no_teknisi": "",
            "cuaca": "", "sqf": "", "esno": "", "kabel_ifl": "",
            "antenna" : "0.97",
            "grounding" : "Terpasang",
            "power_source": combo_source.get(),
            "backup_power": combo_backup.get(),
            "action": combo_action.get(),
            "sn_transceiver": "", "sn_modem": "", "sn_dish": "", "sn_rack": "",
            "sn_stabilizer": "", "sn_router": "", "sn_ap1": "", "sn_ap2": "",
            "problem": problem_text if problem_text else "Tidak ada problem",
        }

        lines = extracted_text.split("\n")
        for line in lines:
            line = line.strip()
            if not line or "┃" not in line:
                continue
            clean = line.split("┃", 1)[1].strip() if "┃" in line else line
            if ":" not in clean:
                continue
            key_part, val = clean.split(":", 1)
            key = key_part.strip().lower()
            value = val.strip().split("✔")[0].split("❌")[0].split("(gagal)")[0].strip()

            if "spmk" in key: data["spmk"] = value
            elif "nama pic" in key: data["nama_pic"] = value
            elif "no. pic" in key or "no pic" in key: data["no_pic"] = value
            elif "nama teknisi" in key: data["nama_teknisi"] = value
            elif "no. teknisi" in key: data["no_teknisi"] = value
            elif "cuaca" in key: data["cuaca"] = value
            elif "sqf" in key: data["sqf"] = value
            elif "esno" in key: data["esno"] = value
            elif "kabel ifl" in key: data["kabel_ifl"] = value
            elif "transceiver" in key: data["sn_transceiver"] = value
            elif "modem" in key: data["sn_modem"] = value
            elif "dish" in key: data["sn_dish"] = value
            elif "rack" in key: data["sn_rack"] = value
            elif "stabilizer" in key or "stabilizer" in key: data["sn_stabilizer"] = value
            elif "router" in key: data["sn_router"] = value
            elif "ap1" in key: data["sn_ap1"] = value
            elif "ap2" in key: data["sn_ap2"] = value

        filename = f"extracted_tmo_data.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success!", f"Data saved!\n{filename}")
            textbox_log.insert("end", f"[SAVED] JSON: {filename}\n")
            textbox_log.see("end")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal simpan JSON:\n{str(e)}")

    ctk.CTkButton(left_panel, text="Save Extracted Data", height=28, font=roboto_bold,
                  hover_color="#308a61", fg_color="#2d6a4f", command=save_to_json).pack(fill="x", padx=10, pady=(10, 0))

    # PANEL TENGAH & KANAN
    source_panel = ctk.CTkFrame(top_frame, corner_radius=12)
    source_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))
    ctk.CTkLabel(source_panel, text="Source Data", font=roboto_title).pack(anchor="w", padx=10, pady=(5, 5))
    textbox_source = ctk.CTkTextbox(source_panel, height=600, font=roboto_textbox)
    textbox_source.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    extracted_panel = ctk.CTkFrame(top_frame, corner_radius=12)
    extracted_panel.pack(side="left", fill="both", expand=True)
    ctk.CTkLabel(extracted_panel, text="Extracted Data", font=roboto_title).pack(anchor="w", padx=10, pady=(5, 5))
    textbox_extracted = ctk.CTkTextbox(extracted_panel, font=roboto_textbox)
    textbox_extracted.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # BOTTOM FRAME
    bottom_frame = ctk.CTkFrame(main_container)
    bottom_frame.grid(row=1, column=0, sticky="nsew")
    bottom_frame.grid_rowconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure((0, 2), weight=1)

    log_panel = ctk.CTkFrame(bottom_frame, corner_radius=12)
    log_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
    ctk.CTkLabel(log_panel, text="Log Output", font=roboto_title).pack(anchor="w", padx=10, pady=(5, 10))
    textbox_log = ctk.CTkTextbox(log_panel, font=roboto_textbox)
    textbox_log.pack(fill="both", expand=True, padx=10, pady=(0, 20))

    problem_panel = ctk.CTkFrame(bottom_frame, corner_radius=12)
    problem_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
    ctk.CTkLabel(problem_panel, text="Problem", font=roboto_title).pack(anchor="w", padx=10, pady=(5, 10))
    textbox_problem = ctk.CTkTextbox(problem_panel, font=roboto_textbox)
    textbox_problem.pack(fill="both", expand=True, padx=10, pady=(0, 20))

    win.protocol("WM_DELETE_WINDOW", win.destroy)