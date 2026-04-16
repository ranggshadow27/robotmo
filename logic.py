import os
import sys
import glob
import time
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from threading import Event

class ElementNotFoundError(Exception):
    pass

def get_app_dir():
        if getattr(sys, 'frozen', False):
            # Kalau .exe
            return os.path.dirname(sys.executable)
        else:
            # Kalau jalan dari Python
            return os.path.dirname(os.path.abspath(__file__))

class TMOLogic:
    driver = None  # Static driver instance
    driver_initialized = False

    def __init__(self, config):
        self.config = config

    def initialize_driver(self):
        if not TMOLogic.driver_initialized or TMOLogic.driver is None:
            print("> Creating webdriver instance")
            TMOLogic.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            TMOLogic.driver_initialized = True
        else:
            try:
                # Coba cek apakah driver masih hidup
                TMOLogic.driver.current_url  # ini bakal error kalau session mati
                print("> Webdriver instance detected")
            except Exception as e:
                print("> Webdriver not found, waiting for new instance..")
                TMOLogic.driver.quit()  # bersihin dulu biar ga orphan process
                TMOLogic.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
                TMOLogic.driver_initialized = True
    
        return TMOLogic.driver

    def check_login_page(self):
        print("> Checking Login Page..")
        try:           
            WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='p_password']"))
            )
            print("> Login page detected: p_username and p_password elements found")
            return True
        except TimeoutException:
            print("> Login page not detected: p_username or p_password elements not found")
            return False
        except Exception as e:
            print(f"> Error checking login page: {e}")
            return False

    def fill_form(self, xpath, value, field_name, index, press_enter=False):
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            if element.is_enabled() and element.is_displayed():
                print(f"> {field_name} (baris {index}) ditemukan")
                element.clear()
                time.sleep(0.2)
                element.send_keys(value)
                if press_enter:
                    element.send_keys(Keys.RETURN)
            else:
                print(f"> {field_name} (baris {index}) tidak bisa diisi: disabled={not element.is_enabled()}, hidden={not element.is_displayed()}")
            return True
        
        except Exception as e:
            print(f"> Error mengisi {field_name} (baris {index}): {e}")
            raise ElementNotFoundError(f"{element} tidak ditemukan, proses dihentikan")
            return False

    def click_element(self, xpath, element_name, index):
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            element.click()
            print(f"> {element_name} diklik")
            return True
        except TimeoutException:
            print(f"> Timeout: {element_name} tidak ditemukan setelah 3 detik")
            raise ElementNotFoundError(f"{element_name} tidak ditemukan, proses dihentikan")
        except Exception as e:
            print(f"> Error mengklik {element_name} : {e}")
            return False

    def fill_modal_tmo(self, config, values, index):
        success = True
        for field, cfg in config.items():
            print(f"> Ini Value dari Formnya : {values[field]}")
            if not self.fill_form(
                xpath=cfg['xpath'],
                value=values[field],
                field_name=field,
                index=index,
                press_enter=cfg.get('press_enter', False)
            ):
                success = False
        return success

    def fill_textarea(self, xpath, value, index):
        try:
            textarea = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            if textarea.is_enabled() and textarea.is_displayed():
                print(f"> Textarea (baris {index}) ditemukan dan bisa diisi")
                print(f"> Teks yang akan diisi: {repr(value)}")
                try:
                    textarea.clear()
                    self.driver.execute_script("arguments[0].value = arguments[1];", textarea, value)
                    actual_value = self.driver.execute_script("return arguments[0].value;", textarea)
                    print(f"> Teks setelah diisi: {repr(actual_value)}")
                except Exception as e:
                    print(f"> Gagal mengisi textarea dengan JavaScript: {e}")
                    textarea.clear()
                    textarea.send_keys(value)
                    actual_value = self.driver.execute_script("return arguments[0].value;", textarea)
                    print(f"> Teks setelah fallback send_keys: {repr(actual_value)}")
            else:
                print(f"> Textarea (baris {index}) tidak bisa diisi: disabled={not textarea.is_enabled()}, hidden={not textarea.is_displayed()}")
            return True
        except Exception as e:
            print(f"> Error mengisi Textarea (baris {index}): {e}")
            return False

    def fill_select_based_on_sn(self, sn_xpath, select_xpath, select_xpath2, index, device):
        try:
            sn_input = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, sn_xpath))
            )
            sn_value = self.driver.execute_script("return arguments[0].value;", sn_input)
            print(f"> Nilai SN {device} (baris {index}): {sn_value}")

            if device == "transceiver":
                if sn_value.startswith("C"):
                    select_modem_element = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, select_xpath))
                    )
                    select_modem = Select(select_modem_element)
                    select_modem.select_by_value("HT2300")
                    print(f"> Select diisi dengan 'HT2300' untuk SN {sn_value} (baris {index})")

                    select_trans_element = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, select_xpath2))
                    )
                    select_trans = Select(select_trans_element)
                    select_trans.select_by_value("REVGO")
                    print(f"> Select diisi dengan 'REVGO' untuk SN {sn_value} (baris {index})")
                else:
                    print(f"> SN Transceiver tidak diawali dengan 'C', select tidak diisi (baris {index})")
            
            if device == "router":
                if sn_value.startswith("H"):
                    select_element = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, select_xpath))
                    )
                    select = Select(select_element)
                    select.select_by_value("Mikrotik")
                    print(f"> Select diisi dengan 'Mikrotik' untuk SN {sn_value} (baris {index})")
                else:
                    print(f"> SN Router tidak diawali dengan 'H', select tidak diisi (baris {index})")

            return True
        except Exception as e:
            print(f"> Error mengisi select berdasarkan SN {device} (baris {index}): {e}")
            return False

    def fill_sn_device_modals(self, config, values, index, progress_callback, step_increment):
        success = True
        total_steps = len(config)
        current_step = 0
        for device, cfg in config.items():
            try:
                if not self.click_element(
                    xpath=cfg['modal_button_xpath'],
                    element_name=f"{device} Modal Button",
                    index=index
                ):
                    success = False
                    continue
                current_step += 1
                progress_callback(current_step / total_steps * step_increment)

                try:
                    dropdown = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, "//*[@id='form_inquery_material_tmo']/div[1]/div[2]/select"))
                    )
                    if dropdown.is_enabled() and dropdown.is_displayed():
                        print(f"> Dropdown {device} Form (baris {index}) ditemukan dan bisa diisi")
                        dropdown.send_keys("SERIAL NUMBER")
                    else:
                        print(f"> Dropdown {device} Form (baris {index}) tidak bisa diisi: disabled={not dropdown.is_enabled()}, hidden={not dropdown.is_displayed()}")
                        success = False
                        continue
                except Exception as e:
                    print(f"> Error mengisi Dropdown {device} Form (baris {index}): {e}")
                    success = False
                    continue
                current_step += 1
                progress_callback(current_step / total_steps * step_increment)

                if not self.fill_form(
                    xpath=cfg['sn_input_xpath'],
                    value=values[device],
                    field_name=f"SN {device}",
                    index=index,
                    press_enter=True
                ):
                    success = False
                    continue
                current_step += 1
                progress_callback(current_step / total_steps * step_increment)
                
                time.sleep(1)
                
                try:
                    sn_button = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='list_material_tmo_table']/tbody/tr/td[7]/input"))
                    )
                    sn_button.click()
                    print(f"> Tombol SN {device} (baris {index}) diklik")
                except TimeoutException:
                    print(f"> Tombol SN {device} tidak muncul (baris {index}), menutup modal...")
                    modal_close = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[@id='modal1']"))
                    )
                    modal_close.click()
                    print(f"> Modal ditutup (baris {index})")
                current_step += 1
                progress_callback(current_step / total_steps * step_increment)
                
                if device == 'transceiver':
                    self.fill_select_based_on_sn(
                        device=device,
                        sn_xpath="//*[@id='p_odu']",
                        select_xpath2="//*[@id='form_view']/div[1]/div[2]/div/div[2]/select",
                        select_xpath="//*[@id='form_view']/div[1]/div[2]/div/div[4]/select",
                        index=index
                    )
                    current_step += 1
                    progress_callback(current_step / total_steps * step_increment)
                
                if device == 'router':
                    self.fill_select_based_on_sn(
                        device=device,
                        sn_xpath="//*[@id='p_router']",
                        select_xpath2="//*[@id='form_view']/div[1]/div[2]/div[1]/div[6]/select",
                        select_xpath="//*[@id='form_view']/div[1]/div[2]/div/div[9]/select",
                        index=index
                    )
                    current_step += 1
                    progress_callback(current_step / total_steps * step_increment)

            except ElementNotFoundError:
                raise
            except Exception as e:
                print(f"> Error mengisi Modal SN {device} (baris {index}): {e}")
                success = False
        return success
    
    def find_file(self, directory, device):
        file_pattern = os.path.join(directory, f"{device}*.*")
        files = glob.glob(file_pattern)
        if not files:
            raise FileNotFoundError(f"Tidak ada file '{device}' di {directory}")
        
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
    
    def fill_file_inputs(self, config, directory, index, progress_callback, step_increment):
        success = True
        total_steps = len(config)
        current_step = 0
        for device, cfg in config.items():
            try:
                original_file = self.find_file(directory, device)
                print(f"> File {device} terbaru ditemukan: {original_file}")

                file_ext = os.path.splitext(original_file)[1]
                timestamp = datetime.now().strftime("%H%M%S")
                new_filename = f"{device}{timestamp}{file_ext}"
                new_filepath = os.path.join(directory, new_filename)

                os.rename(original_file, new_filepath)
                print(f"> File direname menjadi: {new_filepath}")

                if not os.path.exists(new_filepath):
                    raise FileNotFoundError(f"File yang direname {new_filename} tidak ditemukan")

                file_input = self.driver.find_element(By.XPATH, cfg['xpath'])
                print(f"> Input file {device} (baris {index}) ditemukan dan bisa diisi")
                file_input.send_keys(new_filepath)
                print(f"> File diunggah: {new_filepath}")
                current_step += 1
                progress_callback(current_step / total_steps * step_increment)

            except Exception as e:
                print(f"> Error mengisi Input file {device} (baris {index}): {e}")
                success = False
        return success


    def load_json_data(self):
        """Baca semua file JSON extracted_tmo_*.json di folder exe"""
        app_dir = get_app_dir()  # Pakai fungsi ini!
        json_pattern = os.path.join(app_dir, "extracted_tmo_*.json")
        json_files = glob.glob(json_pattern)

        if not json_files:
            # Debug: kasih tahu di mana dia cari
            print(f"[DEBUG] Mencari JSON di: {app_dir}")
            print(f"[DEBUG] File yang ditemukan: {os.listdir(app_dir)}")
            raise FileNotFoundError(f"Tidak ada file extracted_tmo_*.json di folder:\n{app_dir}")

        data_list = []
        for file_path in sorted(json_files):
            print(f"> Load data dari: {os.path.basename(file_path)}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data_list.append(data)
            except Exception as e:
                print(f"> Gagal baca {file_path}: {e}")
    
        print(f"> Total TMO ditemukan: {len(data_list)}")
        return data_list

    def run_autofill(self, username, password, image_dir, excel_file, tmo_type, search_type, progress_callback, show_error, show_info):
        try:
            self.driver = self.initialize_driver()
            url = "https://cboss.mahaga-pratama.co.id/BB_NCC/tmo_ubiqu/index"
            self.driver.get(url)
            time.sleep(2)

            steps_per_row = 7
            login_steps = 4 if self.check_login_page() else 0

            if self.check_login_page():
                username_field = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[@id='p_username']"))
                )
                username_field.clear()
                username_field.send_keys(username)
                progress_callback(1 / (login_steps + steps_per_row))
                
                password_field = WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, "//*[@id='p_password']"))
                )
                password_field.clear()
                password_field.send_keys(password)
                progress_callback(2 / (login_steps + steps_per_row))
                
                submit_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@id='login-box']/div/div/form/fieldset/button"))
                )
                submit_button.click()
                progress_callback(3 / (login_steps + steps_per_row))
                
                try:
                    print("> Halaman login OTP:", self.driver.title)
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='p_otp']"))
                    )
                    otp_header = self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div/form/div/div/h2/b")
                    if otp_header.text == "Enter OTP Login":
                        print("> Halaman OTP terdeteksi")
                        show_info("Mohon masukan kode OTP untuk melanjutkan")
                    progress_callback(4 / (login_steps + steps_per_row))
                except TimeoutException:
                    print("> Halaman OTP tidak terdeteksi, melanjutkan...")
                except Exception as e:
                    print(f"> Error pada pengecekan OTP: {e}")
                    raise
                
                print("> Halaman setelah login:", self.driver.title)
                self.driver.get(url)
                time.sleep(1)
            
            # === TENTUKAN XPATH BERDASARKAN TMO TYPE ===
            if tmo_type == "Instalasi":
                tab_xpath = "//*[@id='myTab']/li[1]/a"
                search_dropdown_xpath = "//*[@id='form_inquery_tmo_install']/div[1]/div[2]/select"
                search_input_xpath = "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/form/div[1]/div[4]/input"
                tmo_button_xpath = "//*[@id='table_tmo_install']/tbody/tr/td[1]/a[2]"
                print("> Mode: Instalasi")
            else:  # Maintenance
                tab_xpath = "//*[@id='maint_tab']"
                search_dropdown_xpath = "//*[@id='form_inquery_tmo_maintenance']/div[1]/div[2]/select"
                search_input_xpath = "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[3]/div[1]/div[2]/div/form/div[1]/div[4]/input"
                tmo_button_xpath = "//*[@id='table_tmo_maintenance']/tbody/tr[1]/td[1]/a[2]"
                print("> Mode: Maintenance")
                
            # GANTI DI SINI: BUKAN pd.read_excel LAGI, TAPI BACA JSON
            data_list = self.load_json_data()
            total_rows = len(data_list)
            base_progress = login_steps / (login_steps + steps_per_row) if login_steps else 0
            row_weight = (1 - base_progress) / total_rows if total_rows > 0 else 1

            for index, row in enumerate(data_list):
                row_progress = base_progress + (index * row_weight)
                current_step = 0
                
                # 1. Klik Tab (Instalasi / Maintenance)
                self.click_element(tab_xpath, f"{tmo_type} Tab", index)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                # 2. Pilih Search Type
                try:
                    search_dropdown = WebDriverWait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, search_dropdown_xpath))
                    )
                    if search_dropdown.is_enabled() and search_dropdown.is_displayed():
                        select = Select(search_dropdown)
                        select.select_by_visible_text(search_type)
                        print(f"> Search type dropdown diisi dengan '{search_type}' (baris {index})")
                    else:
                        print(f"> Search type dropdown tidak bisa diisi (baris {index})")
                except Exception as e:
                    print(f"> Error mengisi search type dropdown (baris {index}): {e}")
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))

                spmk_value = str(row['spmk'])
                values = {
                    'technician_name': str(row.get('nama_teknisi', '')),
                    'technician_num': str(row.get('no_teknisi', '')),
                    'pic_name': str(row.get('nama_pic', '')),
                    'pic_num': str(row.get('no_pic', '')),
                    'weather': str(row.get('cuaca', '')),
                    'power_source': str(row.get('power_source', '')),
                    'power_source_backup': str(row.get('backup_power', '') or row.get('power_source_backup', '')),
                    'antenna': str(row.get('antenna', '')),
                    'sqf': str(row.get('sqf', '')),
                    'esno': str(row.get('esno', '')),
                    'grounding': str(row.get('grounding', '')),
                    'ifl': str(row.get('kabel_ifl', '')),
                    'action': str(row.get('action', ''))
                }
                sn_values = {
                    'transceiver': str(row.get('sn_transceiver', '')),
                    'modem': str(row.get('sn_modem', '')),
                    'dish': str(row.get('sn_dish', '')),
                    'rack': str(row.get('sn_rack', '')),
                    'stabilizer': str(row.get('sn_stabilizer', '') or row.get('sn_stabilizer', '')),
                    'router': str(row.get('sn_router', '')),
                    'ap1': str(row.get('sn_ap1', '')),
                    'ap2': str(row.get('sn_ap2', ''))
                }

                self.fill_form(search_input_xpath, spmk_value, "SPMK", index, press_enter=True)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                # 3. Klik tombol TMO
                time.sleep(1)
                self.click_element(tmo_button_xpath, "TMO Button", index)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                time.sleep(1)
                self.fill_modal_tmo(self.config['modal_tmo_configs'], values, index)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                self.fill_textarea("//*[@id='form_view']/div[1]/div[3]/div/div[9]/textarea", row.get('problem', ''), index)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                self.fill_modal_tmo(self.config['modal_tmo_action'], {'action': values['action']}, index)
                time.sleep(0.1)
                self.fill_sn_device_modals(self.config['sn_device_configs'], sn_values, index, progress_callback, row_weight / steps_per_row)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                self.fill_file_inputs(self.config['file_input_configs'], image_dir, index, progress_callback, row_weight / steps_per_row)
                current_step += 1
                progress_callback(row_progress + (current_step / steps_per_row * row_weight))
                
                print(f"> Autofill TMO selesai: SPMK {spmk_value}")
                time.sleep(1)

            show_info("Autofill TMO Selesai! Mohon Crosscheck Form TMO, Generate kode lapor & Submit TMO sebelum menutup dialog ini")

        except ElementNotFoundError as e:
            show_error(str(e))
        except Exception as e:
            show_error(f"Autofill gagal: {str(e)}")

    @classmethod
    def cleanup(cls):
        if cls.driver and cls.driver_initialized:
            try:
                cls.driver.quit()
            except:
                pass  # udah mati juga gapapa
            cls.driver = None
            cls.driver_initialized = False
            print("> Driver berhasil ditutup & flag direset")