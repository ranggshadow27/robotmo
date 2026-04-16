# automation.py (FINAL - CLEAN - SUPPORT SKIP IMAGE)

import os
import json
import re
import requests
import shutil
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urljoin
from tkinter import messagebox, Tk

def show_error(title, msg): 
    root = Tk(); root.withdraw(); messagebox.showerror(title, msg); root.destroy()
def show_warning(title, msg): 
    root = Tk(); root.withdraw(); messagebox.showwarning(title, msg); root.destroy()
def show_info(title, msg): 
    root = Tk(); root.withdraw(); messagebox.showinfo(title, msg); root.destroy()

# --- VALIDASI TOKEN ---
API_URL = "https://script.google.com/macros/s/AKfycbyGv08iyugoWolQlg2AGZzZxooQy3nqd_S1x7n5GOTH0mwlqz-FpbldIuMPp-HJMwKI/exec?app_type=tmo_automation"
DEFAULT_TOKEN = "MHG_tmoAutomation@ratiPRAY"

def validate_access():
    try:
        response = requests.get(API_URL, timeout=40)
        if response.status_code != 200:
            return False, "Gagal koneksi ke server validasi."
        data = response.json()
        if data.get("token") != DEFAULT_TOKEN:
            return False, "Unknown Key Error!"
        expired_str = data.get("expired", "-")
        if not expired_str:
            return False, "Expired Data"
        expired_dt = datetime.fromisoformat(expired_str.replace("Z", "+00:00"))
        now_jakarta = datetime.now(pytz.timezone("Asia/Jakarta"))
        if now_jakarta > expired_dt.astimezone(pytz.timezone("Asia/Jakarta")):
            return False, "Expired Data"
        return True, "Validasi sukses!"
    except Exception as e:
        return False, f"Error koneksi: {str(e)}"

def format_phone_number(phone):
    if not phone or phone == "❌NOT_FOUND❌":
        return "❌NOT_FOUND❌"
    cleaned = re.sub(r'\D', '', phone)
    if cleaned.startswith('62'):
        cleaned = '0' + cleaned[2:]
    elif cleaned.startswith('8'):
        cleaned = '0' + cleaned
    return cleaned if len(cleaned) >= 10 else phone

def extract_tmo_data(text):
    extracted_data = {
        'SPMK': "❌NOT_FOUND❌", 'Nama PIC': "❌NOT_FOUND❌", 'No PIC': "❌NOT_FOUND❌",
        'Nama Teknisi': "❌NOT_FOUND❌", 'No Teknisi': "❌NOT_FOUND❌",
        'Cuaca': "❌NOT_FOUND❌", 'Transceiver': "❌NOT_FOUND❌", 'Rack': "❌NOT_FOUND❌",
        'SN Modem': "❌NOT_FOUND❌", 'SN Dish': "❌NOT_FOUND❌", 'SN Rack': "❌NOT_FOUND❌",
        'SN Stabilizer': "❌NOT_FOUND❌", 'SN Router': "❌NOT_FOUND❌",
        'SN Ap1': "❌NOT_FOUND❌", 'SN Ap2': "❌NOT_FOUND❌",
        'SQF': "❌NOT_FOUND❌", 'EsNo': "❌NOT_FOUND❌", 'Kabel IFL': "❌NOT_FOUND❌"
    }

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    last_person = None  # "PIC" atau "TEKNISI"

    for line in lines:
        # Normalisasi spasi di sekitar titik dua
        normalized = re.sub(r'\s*:\s*', ':', line)  # PIC :  → PIC:
        lower = normalized.lower()

        # === DETEKSI PIC ===
        if lower.startswith('pic:'):
            nama = normalized[normalized.find(':')+1:].strip()
            if nama:
                extracted_data['Nama PIC'] = nama.split()[0] + ' ' + ' '.join(nama.split()[1:])  # pastiin utuh
                last_person = "PIC"
            continue

        # === DETEKSI TEKNISI ===
        if lower.startswith('teknisi:'):
            nama = normalized[normalized.find(':')+1:].strip()
            if nama:
                extracted_data['Nama Teknisi'] = nama
                last_person = "TEKNISI"
            continue

        # === DETEKSI HP / NO / TELP DI BARIS SENDIRI ===
        if re.match(r'^(hp|no|telp|phone)[\s:]+', lower):
            match = re.search(r'[\+0-9][\d\s\-]{8,}', line)
            if match:
                nomor = match.group(0)
                if last_person == "PIC":
                    extracted_data['No PIC'] = format_phone_number(nomor)
                elif last_person == "TEKNISI":
                    extracted_data['No Teknisi'] = format_phone_number(nomor)
            continue

        # === KALAU PIC / TEKNISI + NOMOR DI SATU BARIS (dengan atau tanpa slash) ===
        pic_match = re.search(r'pic\s*[:]\s*([a-z\s\.\-]+)(?:\s*/\s*|\s+)([\+0-9][\d\s\-]+)', line, re.IGNORECASE)
        if pic_match:
            extracted_data['Nama PIC'] = pic_match.group(1).strip()
            extracted_data['No PIC'] = format_phone_number(pic_match.group(2))
            last_person = "PIC"

        teknisi_match = re.search(r'teknisi\s*[:]\s*([a-z\s\.\-]+)(?:\s*/\s*|\s+)([\+0-9][\d\s\-]+)', line, re.IGNORECASE)
        if teknisi_match:
            extracted_data['Nama Teknisi'] = teknisi_match.group(1).strip()
            extracted_data['No Teknisi'] = format_phone_number(teknisi_match.group(2))
            last_person = "TEKNISI"

    # === TRANSCIVER & RAK (typo proof) ===
    trans = re.search(r'(?:Transceiver|Transciver|Tranceiver|Transciever)[\s:]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if trans:
        sn = re.search(r'\b[7C]\w*\b', trans.group(1))
        extracted_data['Transceiver'] = (sn.group(0) if sn else trans.group(1)).upper()

    rak = re.search(r'(?:Rack|Rak)[\s:]+([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if rak:
        extracted_data['Rack'] = rak.group(1).upper()

    # === FIELD LAIN (tetap sama) ===
    simple_patterns = {
        'SPMK': r'SPMK[-\s]*([^\n]+)',
        'Cuaca': r'Cuaca\s*:\s*([^\n]+)',
        'SN Transceiver': r'SN\s+Transceiver\s*:\s*([^\n]+)',
        'SN Modem': r'SN\s+Modem\s*:\s*([^\n]+)',
        'SN Dish': r'SN\s+Dish.*:\s*([^\n]+)',
        'SN Rack': r'SN\s+Rack\s+Indoor.*:\s*([^\n]+)',
        'SN Stabilizer': r'SN\s+Stabilizer\s*:\s*([^\n]+)',
        'SN Router': r'SN\s+Router.*:\s*([^\n]+)',
        'SN Ap1': r'SN\s+AP\s*1.*:\s*([^\n]+)',
        'SN Ap2': r'SN\s+AP\s*2.*:\s*([^\n]+)',
        'SQF': r'SQF\s*:\s*([^\n]+)',
        'EsNo': r'ESNO?\s*:\s*([^\n]+)',
        'Kabel IFL': r'Kabel\s+IFL\s*:\s*([^\n]+)',
    }

    for key, pat in simple_patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if key == 'SPMK':
                extracted_data[key] = val.split('-')[-1].strip()
            elif key in ['SN Modem', 'SN Router', 'SN Ap1', 'SN Ap2']:
                sn = re.search(r'\b[7C3H]\w*\b', val)
                extracted_data[key] = sn.group(0) if sn else val
            else:
                extracted_data[key] = val

    return extracted_data

# --- IMAGE MAP ---
IMAGE_MAP = [
        ("/html/body/div/div/section/div/div[1]/div[3]/div[2]/div/div[19]/div[2]/a/img", "ba"),
]
IMAGE_FOLDER = "downloaded_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def log(textbox_log, msg):
    textbox_log.insert("end", f"{msg}\n")
    textbox_log.see("end")

def download_custom_image(driver, img_element, custom_name):
    try:
        src = img_element.get_attribute("src")
        if not src: return None
        full_url = urljoin(driver.current_url, src)
        response = requests.get(full_url, stream=True, timeout=20)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%H%M%S")
            ext = os.path.splitext(full_url.split("?")[0])[1] or ".jpg"
            filename = os.path.join(IMAGE_FOLDER, f"{custom_name}{timestamp}{ext}")
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return os.path.basename(filename)
    except: pass
    return None

# --- MAIN EXTRACTOR ---
def run_full_extractor(entry_tmo, combo_source, combo_backup, combo_action,
                       textbox_source, textbox_extracted, textbox_log, textbox_problem,
                       username, password, show_browser=False, skip_image=False, on_complete=None):

    textbox_log.delete("1.0", "end")
    log(textbox_log, "[INFO] Memulai ekstraksi TMO...")

    valid, message = validate_access()
    if not valid:
        log(textbox_log, f"[ERROR] {message}")
        show_error("Akses Ditolak", message)
        if on_complete: on_complete()
        return

    tmo_id = entry_tmo.get().strip()
    if not tmo_id:
        show_error("Error", "TMO ID kosong!")
        if on_complete: on_complete()
        return

    url = f"https://taskwatch.simahaga.my.id/index.php/tmo/{tmo_id}/view"
    driver = None

    try:
        # === SETUP CHROME OPTIONS ===
        options = Options()
        if not show_browser:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # Kalau skip_image = True → matiin gambar total
        if skip_image:
            options.add_argument("--disable-images")
            options.add_argument("--blink-settings=imagesEnabled=false")
            log(textbox_log, "[MODE] FAST: Gambar dinonaktifkan (tanpa download BA)")
        else:
            log(textbox_log, "[MODE] FULL: Akan mendownload gambar BA")

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        # === LOGIN IF NEEDED ===
        if "login" in driver.current_url.lower():
            log(textbox_log, "[INFO] Login diperlukan...")
            try:
                wait.until(EC.presence_of_element_located((By.NAME, "username")))
                driver.find_element(By.NAME, "username").send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                driver.find_element(By.XPATH, "/html/body/div/div[1]/form/button").click()
                wait.until(EC.url_contains("index"))
                log(textbox_log, "[SUCCESS] Login berhasil!")
                log(textbox_log, "[INFO] Membuka TMO Request!")
                driver.get(url)
            except:
                show_error("[FAILED]", "Informasi login salah atau tmo-req gagal terload!")
                if on_complete: on_complete()
                return

        # === AMBIL RAW TEXT ===
        try:
            source_elem = wait.until(EC.presence_of_element_located((
                By.XPATH, '//*[@id="app"]/div/section/div/div[1]/div[2]/div[2]/div/div[2]/div/div[2]/div'
            )))
            source_text = source_elem.text
            textbox_source.delete("0.0", "end")
            textbox_source.insert("end", source_text)
            log(textbox_log, "[SUCCESS] Raw text berhasil diambil!")

            extracted = extract_tmo_data(source_text)

            try:
                spmk = driver.find_element(By.XPATH, '/html/body/div/div/section/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[2]/td[3]').text.strip()
                # spmk = spmk_raw.split("/")[3].strip() if len(spmk_raw.split("/")) > 3 else spmk_raw
            except:
                spmk = "❌SPMK_NOT_FOUND❌"

            # Tampilkan hasil dulu
            build_and_show_result(textbox_extracted, spmk, extracted, combo_source, combo_backup, combo_action, [], [], skip_image)
            save_current_data(entry_tmo, combo_source, combo_backup, combo_action, extracted, spmk, [], textbox_problem, textbox_log)
            show_info("SUCESS", "Form TMO berhasil diekstrak!")

            # === DOWNLOAD GAMBAR BA (hanya jika TIDAK skip) ===
            downloaded = []
            if skip_image:
                log(textbox_log, "[SKIP] Download gambar dilewati sesuai pilihan")
            else:
                log(textbox_log, "[INFO] Mengaktifkan gambar & download BA...")
                driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                    "behavior": "allow", "downloadPath": os.path.abspath(IMAGE_FOLDER)
                })
                driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return {length: 10};}});")
                driver.get(driver.current_url)  # Refresh biar gambar muncul

                for xpath, name in IMAGE_MAP:
                    try:
                        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, xpath)))
                        img = driver.find_element(By.XPATH, xpath)
                        saved = download_custom_image(driver, img, name)
                        if saved:
                            downloaded.append(saved)
                            log(textbox_log, f"   [OK] {saved}")
                        else:
                            log(textbox_log, f"   [GAGAL] {name}")
                    except:
                        log(textbox_log, f"   [GAGAL] {name} (tidak ditemukan)")

            # Update hasil akhir
            build_and_show_result(textbox_extracted, spmk, extracted, combo_source, combo_backup, combo_action, downloaded, [], skip_image)
            save_current_data(entry_tmo, combo_source, combo_backup, combo_action, extracted, spmk, downloaded, textbox_problem, textbox_log)

            if not skip_image and not downloaded:
                show_warning("[FAILED]", "Gambar BA gagal di-download (mungkin koneksi lemot)")
            elif not skip_image:
                show_info("[SUCCESS]", "Data TMO & Gambar BA berhasil diekstrak!")

        except TimeoutException:
            show_error("[FAILED]", "TMO Tidak Ditemukan, Data gagal diambil. Cek TMO ID atau koneksi!")

    except Exception as e:
        log(textbox_log, f"[FATAL] {str(e)}")
        show_error("Error Fatal", str(e))
    finally:
        if driver:
            driver.quit()
        log(textbox_log, "[INFO] Browser ditutup.")
        if on_complete:
            on_complete()

# --- BUILD RESULT (support skip_image) ---
def build_and_show_result(textbox_extracted, spmk, extracted, combo_source, combo_backup, combo_action, downloaded, failed, skip_image=False):
    result = f"┃ SPMK\t\t: {spmk}\n\n"
    result += "=========== Common Data ===========\n"
    result += f"┃ Nama PIC\t\t: {extracted.get('Nama PIC', '❌NOT_FOUND❌')}\n"
    result += f"┃ No. PIC\t\t: {extracted.get('No PIC', '❌NOT_FOUND❌')}\n"
    result += f"┃ Nama Teknisi\t\t: {extracted.get('Nama Teknisi', '❌NOT_FOUND❌')}\n"
    result += f"┃ No. Teknisi\t\t: {extracted.get('No Teknisi', '❌NOT_FOUND❌')}\n"
    result += f"┃ Cuaca\t\t: {extracted.get('Cuaca', '❌NOT_FOUND❌')}\n"
    result += f"┃ SQF\t\t: {extracted.get('SQF', '❌NOT_FOUND❌')}\n"
    result += f"┃ EsNo\t\t: {extracted.get('EsNo', '❌NOT_FOUND❌')}\n"
    result += f"┃ Kabel IFL\t\t: {extracted.get('Kabel IFL', '❌NOT_FOUND❌')}\n"
    result += f"┃ Power Source\t\t: {combo_source.get()}\n"
    result += f"┃ Backup PWR\t\t: {combo_backup.get()}\n\n"

    result += "=========== Device SN ===========\n"
    result += f"┃ SN Transceiver\t\t: {extracted.get('SN Transceiver', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN Modem\t\t: {extracted.get('SN Modem', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN Dish\t\t: {extracted.get('SN Dish', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN Rack\t\t: {extracted.get('SN Rack', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN Stabilizer\t\t: {extracted.get('SN Stabilizer', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN Router\t\t: {extracted.get('SN Router', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN AP1\t\t: {extracted.get('SN Ap1', '❌NOT_FOUND❌')}\n"
    result += f"┃ SN AP2\t\t: {extracted.get('SN Ap2', '❌NOT_FOUND❌')}\n\n"

    result += f"┃ Action\t\t:\n{combo_action.get()}\n\n"

    result += "=== Gambar Tersimpan ===\n"
    if skip_image:
        for _, name in IMAGE_MAP:
            result += f"┃ {name.upper()}\t\t: SKIPPED (Mode Cepat)\n"
    else:
        count = len(downloaded)
        for _, name_prefix in IMAGE_MAP:
            matched = next((f for f in downloaded if name_prefix in f), None)
            result += f"┃ {matched or name_prefix.upper()}\t\t: {'SUCCESS' if matched else 'FAILED'}\n"

    textbox_extracted.delete("0.0", "end")
    textbox_extracted.insert("end", result)

# --- SAVE JSON ---
def save_current_data(entry_tmo, combo_source, combo_backup, combo_action, extracted, spmk, downloaded, textbox_problem, textbox_log):
    problem_text = textbox_problem.get("1.0", "end-1c").strip()
    json_data = {
        "tmo_id": entry_tmo.get().strip(),
        "spmk": spmk.replace("❌SPMK_NOT_FOUND❌", "-"),
        "nama_pic": extracted.get("Nama PIC", "-").replace("❌NOT_FOUND❌", "-"),
        "no_pic": extracted.get("No PIC", "-").replace("❌NOT_FOUND❌", "-"),
        "nama_teknisi": extracted.get("Nama Teknisi", "-").replace("❌NOT_FOUND❌", "-"),
        "no_teknisi": extracted.get("No Teknisi", "-").replace("❌NOT_FOUND❌", "-"),
        "cuaca": extracted.get("Cuaca", "-").replace("❌NOT_FOUND❌", "-"),
        "sqf": extracted.get("SQF", "-").replace("❌NOT_FOUND❌", "-"),
        "esno": extracted.get("EsNo", "-").replace("❌NOT_FOUND❌", "-"),
        "kabel_ifl": extracted.get("Kabel IFL", "-").replace("❌NOT_FOUND❌", "-"),
        "power_source": combo_source.get(),
        "backup_power": combo_backup.get(),
        "antenna": "0.97",
        "grounding": "Terpasang",
        "action": combo_action.get(),
        "sn_transceiver": extracted.get("SN Transceiver", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_modem": extracted.get("SN Modem", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_dish": extracted.get("SN Dish", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_rack": extracted.get("SN Rack", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_stabilizer": extracted.get("SN Stabilizer", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_router": extracted.get("SN Router", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_ap1": extracted.get("SN Ap1", "-").replace("❌NOT_FOUND❌", "-"),
        "sn_ap2": extracted.get("SN Ap2", "-").replace("❌NOT_FOUND❌", "-"),
        "problem": problem_text or "Tidak ada problem"
    }
    try:
        with open("extracted_tmo_data.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        log(textbox_log, "[SAVED] JSON berhasil disimpan!")
    except Exception as e:
        log(textbox_log, f"[ERROR] Gagal simpan JSON: {e}")