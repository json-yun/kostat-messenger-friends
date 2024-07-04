# -*- coding: utf-8 -*-
"""
initializer
"""
import os
from emoticon_module import load_data, config_update, present_or_absent, save_emoticons_xml, MENAME, MENAME_KOR, ROOT
import win32com.client

def initialize():
    def create_shortcut():
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        shortcut_path = os.path.join(desktop, MENAME_KOR+".lnk")
        target = os.path.join(ROOT, MENAME+".exe")
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.Description = MENAME
        shortcut.save()

    def update():
        xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict = load_data()

        # config
        config_update(tabdict_reference.keys(), tabdict.keys())
        _, absentitem = present_or_absent(itemdict, itemdict_reference)
        if len(absentitem) > 0:
            itemdict.update(absentitem)
        save_emoticons_xml(tabdict.values(), itemdict.values())
    
    
    # 바로가기 생성
    create_shortcut()
    # emoticon.xml에 item 추가
    update()
    # restart
    os.system('taskkill /f /IM "KOSTAT Messenger friends.exe"')
    os.system('taskkill /f /IM EzQ.exe')
    os.system('start /d "C:\Kostat Messenger 2.0\" /b EzQ.exe')
    os.system('start /d "C:\Kostat Messenger 2.0\" /b EzQ.exe')
    try:
        os.remove(r"C:\Kostat Messenger 2.0\Skins\Html\images\emoticon\tab_setting.exe")
    except:
        pass
    # # pop up readme
    os.system(r'start notepad "C:\Kostat Messenger 2.0\readme.txt"')
