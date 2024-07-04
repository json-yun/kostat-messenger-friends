# -*- coding: utf-8 -*-
"""
emoticons module
"""

import xml.etree.ElementTree as ET
import os
import configparser
import shutil
import time
import sys
import winreg

try:
    ROOT, _ = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\EZQ\Kostat Messenger Ⅱ", 0, winreg.KEY_READ), "EXECNAME")
except:
    print("메신저를 찾을 수 없습니다.")
    raise
ROOT = "/".join(ROOT.strip('"').split("\\")[:-1])
path = ROOT+'/Skins/Html/images/emoticon/'
pathchat = ROOT+'/Skins/Html/images/Chat/'
FAVORITE = ROOT+"/Skins/Html/images/emoticon/Favorite.ini"
EMOTICON = ROOT+"/Skins/Html/images/emoticon/"
DATAPATH = ROOT+"/data/"
MEPATH = sys.argv[0]
MENAME = "KOSTAT Messenger Friends"
MENAME_KOR = "통계청 메신저의 친구"

class IndexableDict(dict):
    """Never use int as key"""
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)
    
    def rearrange(self, idxs):
        miss = len(idxs)-len(self)
        if miss > 0:
            idxs += [2 ** 32] * miss
        elif miss < 0:
            idxs = idxs[:miss]
            
        zipped = list(zip(idxs, self.items()))
        sorted_zipped = list(zip(*sorted(zipped)))
        self.clear()
        self.update(self.__class__(dict(sorted_zipped[1])))
        return self
    
    def switch(self, idx0, idx1):
        idxs = list(range(len(self)))
        idxs[idx0], idxs[idx1] = idx1, idx0
        return self.rearrange(idxs)
    
    def move(self, old_idx, new_idx):
        idxs = list(range(len(self)))
        # old = idxs.pop(old_idx)
        # idxs = idxs[:new_idx] + [old] + idxs[new_idx:]
        if old_idx < new_idx:
            for i in range(old_idx+1, new_idx+1):
                idxs[i] -= 1
            idxs[old_idx] = new_idx
        else:
            for i in range(new_idx, old_idx):
                idxs[i] += 1
            idxs[old_idx] = new_idx
        return self.rearrange(idxs)
    
    def index(self, key):
        return list(self.keys()).index(key)
    
    def name(self, method = 'control'):
        if method == 'control':
            return list(super().keys())
        else:
            return [t.find(method).text for t in self.values()]
    
    def printitems(self, name_method = 'control', skip_zero = False, start_with_one = True):
        l = list(range(len(self)))
        if skip_zero:
            l.pop(0)
        p = (not skip_zero)*start_with_one
        for i in l:
            print(str(i+p)+ '. ' + self.name(name_method)[i])

def set_config(name, value, type=winreg.REG_SZ):
    try:
        keypath = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\"+MENAME, 0, winreg.KEY_WRITE)
    except FileNotFoundError:
        keypath = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\"+MENAME)
    return winreg.SetValueEx(keypath, name, 0, type, value)
def read_config(name):
    try:
        keypath = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\"+MENAME, 0, winreg.KEY_READ)
        return winreg.QueryValueEx(keypath, name)[0]
    except FileNotFoundError:
        return 0
def config_update(reference, partial):
    """type: tab.keys"""
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(path + 'config.ini')
    
    if 'TAB' not in config:
        config['TAB'] = {}
        
    for tabname in reference:
        if tabname in partial:
            config['TAB'][tabname] = '1'
        else:
            config['TAB'][tabname] = '0'
    
    # if 'CHAT' not in config:
    #     config['CHAT'] = {}
    # if 'hide_profile' not in config['CHAT']:
    #     config['CHAT']['hide_profile'] = '0'
    # if 'balloon_type' not in config['CHAT']:
    #     config['CHAT']['balloon_type'] = 'default'
    if not read_config('hide_profile'):
        set_config('hide_profile', '0')
    if not read_config('balloon_type'):
        set_config('balloon_type', 'default')
                
    with open(path + 'config.ini', 'w') as configfile:
        config.write(configfile)
        
def save_emoticons_xml(tabs, items):
    """tabs & items must be values not keys"""
    new_root = ET.Element("EmoticonList")
    for item in tabs:
        new_root.append(item)
    for item in items:
        new_root.append(item)
    try:
        with open(path + 'emoticons.xml', 'wb') as file:
            ET.ElementTree(new_root).write(file, encoding='utf-8', xml_declaration=True)
        return '저장완료'
    except:
        return '저장실패'
        
def apply_config(reference, partial):
    """type: dict"""
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(path + 'config.ini')
    try:
        for name, state in config['TAB'].items():
            if (state != '0') & (name in reference.keys()):
                partial[name] = reference[name]
            elif name in partial.keys():
                partial.pop(name)
    except:
        config_update(reference.keys(), partial.keys())
        raise
    
def present_or_absent(inputdict, reference):
    present = IndexableDict()
    absent = IndexableDict()
    for item in inputdict:
        if item in reference:
            present[item] = reference[item]
    for item in reference:
        if item not in inputdict:
            absent[item] = reference[item]
    
    return present, absent

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def switch_profile():
    if read_config('hide_profile') == '0':
        source = resource_path('res/chat_photobase_invsbl.png')
        destination = pathchat + 'chat_photobase.png'
        shutil.copyfile(source, destination)
        set_config('hide_profile', '1')
        return 1
    else:
        source = resource_path('res/chat_photobase_default.png')
        destination = pathchat + 'chat_photobase.png'
        shutil.copyfile(source, destination)
        set_config('hide_profile', '0')
        return 0
        
def switch_balloon():
    if read_config('balloon_type') == 'excel':
        source = resource_path('res/chat_balloon_yellow.9_default.png')
        destination = pathchat + 'chat_balloon_yellow.9.png'
        shutil.copyfile(source, destination)
        source = resource_path('res/chat_balloon_white.9_default.png')
        destination = pathchat + 'chat_balloon_white.9.png'
        shutil.copyfile(source, destination)
        set_config('balloon_type', 'default')
        return 'default'
    else:
        source = resource_path('res/chat_balloon_yellow.9_excel.png')
        destination = pathchat + 'chat_balloon_yellow.9.png'
        shutil.copyfile(source, destination)
        source = resource_path('res/chat_balloon_white.9_excel.png')
        destination = pathchat + 'chat_balloon_white.9.png'
        shutil.copyfile(source, destination)
        set_config('balloon_type', 'excel')
        return 'excel'

def load_data():
    """xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict"""
    try:
        xml_reference = ET.parse(path + 'reference.xml')
    except:
        print("reference.xml이 없습니다. 재설치 후 다시 시도하세요.")
        raise
    root_reference = xml_reference.getroot()
    tabs_reference = root_reference.findall('EmoticonTabitem')
    tabnames_reference = [t.attrib['TabControlNM'] for t in tabs_reference]
    items_reference = root_reference.findall('EmoticonItem')
    itemnames_reference = [t.find('Name').text for t in items_reference]
    xml = ET.parse(path + 'Emoticons.xml')
    root = xml.getroot()
    tabs = root.findall('EmoticonTabitem')
    tabnames = [t.attrib['TabControlNM'] for t in tabs]
    items = root.findall('EmoticonItem')
    itemnames = [t.find('Name').text for t in items]
    
    tabdict_reference = IndexableDict(dict(zip(tabnames_reference, tabs_reference)))
    itemdict_reference = IndexableDict(dict(zip(itemnames_reference, items_reference)))
    tabdict = IndexableDict(dict(zip(tabnames, tabs)))
    itemdict = IndexableDict(dict(zip(itemnames, items)))
    
    
    if 'BtnBotong' not in tabdict:
        tabdict['BtnBotong'] = tabdict_reference['BtnBotong']
    tabdict.move(tabdict.index('BtnBotong'), 0)
    
    return (xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict)



def certinput(prompt, start, end, raise_error = False):
    while True:
        i = input(prompt)
        try:
            if start <= int(i) <= end:
                return i
        except:
            if raise_error:
                raise
            else:
                continue

def ui_move(dictionary):
    while True:
        os.system('cls')
        print('옮기려는 이모티콘 번호를 입력해주세요:')
        dictionary.printitems('TabName', skip_zero=True)
        print('0. 나가기')
        old = int(certinput('>>> ', 0, len(dictionary)-1))
        if old != 0:
            print(dictionary.name('TabName')[old] + '을(를) 위치시킬 번호를 입력해주세요:')
            new = int(certinput('>>> ', 1, len(dictionary)-1))
            dictionary.move(old, new)
        else:
            break
        
def ui_add_remove(dictionary, reference):
    present, absent = present_or_absent(dictionary, reference)
    while True:
        os.system('cls')
        print('사용중인 이모티콘:')
        present.printitems('TabName', skip_zero=True)
        print('\n추가가능 이모티콘:')
        absent.printitems('TabName', start_with_one=True)
        print('\n원하는 작업의 번호를 입력하세요.\n1. 추가\n2. 삭제\n0. 나가기\n')
        c = certinput(">>> ", 0, 2)
        # config 연동기능 추가
        if c == '1':
            if len(absent) < 1:
                continue
            idx = int(certinput("추가할 이모티콘을 입력하세요.\n>>> ", 1, len(absent)))
            key = absent.name()[idx-1]
            present[key] = dictionary[key] = absent.pop(key)
            config['TAB'][key] = '1'
            dictionary.move(dictionary.index(key), len(dictionary)-1)
            present.move(present.index(key), len(present)-1)
        elif c == '2':
            if len(present) < 2:
                continue
            idx = int(certinput("삭제할 이모티콘을 입력하세요.\n>>> ", 1, len(present)-1))
            key = present.name()[idx]
            absent[key] = dictionary.pop(key)
            present.pop(key)
            config['TAB'][key] = '0'
        else:
            break
        
    
def do():
    xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict = load_data()
    
    _, absentitem = present_or_absent(itemdict, itemdict_reference)
    if len(absentitem) > 0:
        itemdict.update(absentitem)
        save_emoticons_xml(tabdict.values(), itemdict.values())
        # # restart
        # os.system('restart.bat')
        # # pop up readme
        # os.system('notepad.exe ' + path + 'readme.txt')
        return 0
    
    global config
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(path + 'config.ini')
    
    while False:
        os.system('cls')
        print('<<<<<<<원하는 작업의 번호를 입력하세요>>>>>>>')
        print('1. 이모티콘 순서 바꾸기')
        print('2. 이모티콘 추가/제거')
        hideshow = {'0': '가리기', '1': '보이기'}
        print('3. 채팅창 프로필사진 ' + hideshow[read_config('hide_profile')])
        balloon = {'default': '엑셀모양 말풍선으로 바꾸기',
                   'excel': '기본 말풍선으로 바꾸기'}
        print('4. ' + balloon[read_config('balloon_type')])
        print('5. 수정 취소')
        print('0. 저장 후 나가기')
        i = certinput(">>> ", 0, 5)
        if i == '1':
            ui_move(tabdict)
        elif i == '2':
            ui_add_remove(tabdict, tabdict_reference)
        elif i == '3':
            switch_profile()
        elif i == '4':
            switch_balloon()
        elif i == '5':
            xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict = load_data()
        else:
            save_emoticons_xml(tabdict.values(), itemdict.values())
            time.sleep(2)
            break
    return 0

if __name__ == '__main__':
    do()
