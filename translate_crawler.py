from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


import pyperclip as pc 
import urllib.request
import requests
import platform
import time
import re
import _thread
import threading
import time
import os
import os.path
from pathlib import Path
import json
from datetime import datetime
import hashlib


class InternetScouting():
    def __init__(self):
        print("Initialize internet crawler ...")
        self.driver = None
        self.initialize_driver()
        self.list_links = []
        self.depth_threshold = 10  # số trang search result lấy link
        self.depth_search = 0
        self.request_count = 0
        self.current_word = ""
        # Chinh sua tham so o day
        self.start_index = 2584
        self.part_data = 6
        self.path_data = "./data/part_data/part_new_data_"+str(self.part_data)+".txt"
        self.path_missing = "./result/part_"+str(self.part_data)+"/index_miss.txt"
        self.path_result = "./result/part_"+str(self.part_data)+"/translate_result_part"+str(self.part_data)+"_"+str(self.start_index)+".txt"
        

    def initialize_driver(self):
        try:
            options = Options()
            #  Code to disable notifications pop up of Firefox Browser
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-infobars")
            options.add_argument("--mute-audio")
            options.add_argument("start-maximized")
            options.add_argument("--disable-extensions")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-application-cache')
            options.add_argument('--disable-gpu')
            options.add_argument("--disable-dev-shm-usage")

            # options.headless = True

            try:
                platform_ = platform.system().lower()
                if platform_ in ['linux', 'darwin']:
                    self.driver = webdriver.Firefox(options=options,executable_path="./driver/geckodriver")  # executable_path="./driver/geckodriver",
                else:
                    self.driver = webdriver.Firefox(options=options,
                                                    executable_path='./driver/geckodriver.exe')  # executable_path="./driver/geckodriver.exe",
            except Exception as ex:
                print("Khởi tạo Crawler lỗi", ex)
                self.driver.close()
                return

            # self.driver.maximize_window()
            self.driver.get('https://translate.google.com/?hl=vi&sl=ru&tl=vi&text=%D0%B4%D0%B0%D1%81%D1%8C%D0%B4%D0%B0%D1%81%D0%B4%20&op=translate')
            time.sleep(10)
            print("Initialize successful!")
        except Exception as e:
            print("Khởi tạo và đăng nhập crawler lỗi", e)

    def reset(self):
        self.request_count += 1
        if self.request_count == 200:
            self.driver.close()
            self.initialize_driver()
            self.request_count = 0
            return True

        return False

    def request_translate(self):
        trans_text_temp = ''
        list_source_text = self.get_list_translate()
        if len(list_source_text) == 0:
            print("Không có data để dịch")
            return

        url = 'https://translate.google.com/?hl=vi&sl=ru&tl=vi&text=%D0%B4%D0%B0%D1%81%D1%8C%D0%B4%D0%B0%D1%81%D0%B4%20&op=translate'

        self.driver.get(url)
        time.sleep(10)
        list_save_text = []
        source_tag = self.driver.find_element_by_class_name('er8xn')
        source_text = source_tag.text
        time.sleep(2)
        trans_tag = self.driver.find_element_by_class_name('VIiyi')
        trans_text = trans_tag.text
        print(source_text, trans_text)
        save_text = source_text + "|||" + trans_text
        # Chinh sua tham so o day
        for i in range(self.start_index, len(list_source_text)):

            print('Proccessing Input ',i)
            trans_text_temp = ''
            count_translations = 0
            is_miss = True
            while(count_translations<=5):
                count_translations+=1
                source_tag.clear()
                pc.copy(list_source_text[i])
                source_tag.send_keys(Keys.CONTROL+"v")
                time.sleep(1.5)
                try:
                    trans_tag = self.driver.find_element_by_class_name('VIiyi')
                    trans_text = trans_tag.text
                    trans_text = trans_text
                except:
                    print("ex")
                    continue
                trans_text_temp = trans_text
                if((self.check_translate(list_source_text[i],trans_text))and(trans_text==trans_text_temp)):
                    input_texts = list_source_text[i].split('\n\n')
                    output_texts = trans_text.split('\n\n')
                    is_miss=False
                    for idx in range(0,len(input_texts)):
                        save_text = input_texts[idx] + " ||| " + output_texts[idx]
                        list_save_text.append(save_text)
                    print('stranslate ',i,' done')
                    break
            
            
            self.save_translate_text(list_save_text)
            if is_miss:
                f = open(self.path_missing,"a")
                print('is missing')
                f.write(str(i)+'\n')
            
            if self.reset():
                while(True):
                    try:
                        self.driver.get('https://translate.google.com/?hl=vi&sl=ru&tl=vi&text=%D0%B4%D0%B0%D1%81%D1%8C%D0%B4%D0%B0%D1%81%D0%B4%20&op=translate')
                        time.sleep(5)
                        source_tag = self.driver.find_element_by_class_name('er8xn')
                        trans_tag = self.driver.find_element_by_class_name('VIiyi')
                        break
                    except:
                        pass

            



    def get_list_translate(self):
        print('Load data...........')
        with open(self.path_data, 'r', encoding='utf-8') as f:
            list_data = f.readlines()
        list_data = [x.replace('<**> ','\n\n').replace("'","").replace('"','').strip() for x in list_data]
        print('Load data success....')
        return list_data

    def save_translate_text(self, list_data):
        with open(self.path_result, 'w', encoding='utf-8') as f:
            for eachData in list_data:
                f.write(eachData + "\n")

    def check_translate(self,input_text, output_text):
        count_output_characters = output_text.count('\n\n')
        count_input_characters = input_text.count('\n\n')
        print('check ',count_input_characters,' ',count_output_characters)

        if (count_output_characters == count_input_characters):
            return True
        return False    


if __name__ == "__main__":
    ac = InternetScouting()
    ac.request_translate()



