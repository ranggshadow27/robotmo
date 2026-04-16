modal_tmo_configs = {
    'technician_name': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[1]/div[5]/input", 'press_enter': False},
    'technician_num': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[1]/div[6]/input", 'press_enter': False},
    'pic_num': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[2]/div[6]/input", 'press_enter': False},
    'pic_name': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[2]/div[5]/input", 'press_enter': False},
    'weather': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[2]/div[7]/input", 'press_enter': False},
    'power_source': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[2]/div[11]/input", 'press_enter': False},
    'power_source_backup': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[1]/div[2]/div[12]/input", 'press_enter': False},
    'antenna': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[3]/div/div[1]/input", 'press_enter': False},
    'sqf': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[3]/div/div[2]/input", 'press_enter': False},
    'esno': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[3]/div/div[3]/input", 'press_enter': False},
    'grounding': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[3]/div/div[6]/input", 'press_enter': False},
    'ifl': {'xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[4]/div/div/form/div[1]/div[3]/div/div[7]/input", 'press_enter': False},
}

modal_tmo_action = {
    'action': {'xpath': "//*[@id='p_action_chosen']/ul/li/input", 'press_enter': True}
}

sn_device_configs = {                                      
    'transceiver': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[1]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'modem': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[3]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'dish': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[5]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'rack': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[6]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'stabilizer': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[7]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'router': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[8]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'ap1': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[10]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"},
    'ap2': {'modal_button_xpath': "//*[@id='form_view']/div[1]/div[2]/div/div[11]/div/div/a", 'sn_input_xpath': "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[6]/div/div/div[2]/form/div[1]/div[4]/input"}
}

file_input_configs = {
    # 'transceiver': {'xpath': "//*[@id='file_transceiver']"},
    # 'modem': {'xpath': "//*[@id='file_modem']"},
    # 'dish': {'xpath': "//*[@id='file_dish']"},
    # 'rack': {'xpath': "//*[@id='file_rak']"},
    # 'stabillizer': {'xpath': "//*[@id='file_stabilizer']"},
    # 'router': {'xpath': "//*[@id='file_routerboard']"},
    # 'ap1': {'xpath': "//*[@id='file_ap1']"},
    # 'ap2': {'xpath': "//*[@id='file_ap2']"},
    'ba': {'xpath': "//*[@id='p_file']"}
}