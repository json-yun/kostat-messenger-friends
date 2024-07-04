from tkinter import *
from tkinter import messagebox, ttk
from emoticon_module import *
from threading import Thread
from recent_watchdog import find_userid
import time
import shutil
import os
from collections import defaultdict

WINDOWSIZE=(1920, 1080)

def gui_main(conn=None):
    def pipe_listener():
        global mainwindow
        while True:
            try:
                item = conn.recv()
            except EOFError:
                print("pipe conn EOFError")
                conn.close()
                break
            else:
                if item == 'lift':
                    print("lift")
                    mainwindow.lift()
                    mainwindow.wm_attributes("-topmost", 1)
                    mainwindow.wm_attributes("-topmost", 0)
                    mainwindow.focus_force()
    def stop_listener():
        # global conn
        # conn = None
        mainwindow.destroy()
    def on_select_present(*args):
        global listbox_num
        # listbox_absent.select_clear(0, END)
        listbox_num = 1
        show_preview()
    def on_select_absent(*args):
        global listbox_num
        # listbox_present.select_clear(0, END)
        listbox_num = 2
        show_preview()

    def moveitem(dev):
        if listbox_present.curselection():
            idx = listbox_present.curselection()
            listbox_num = 1
        else:
            idx = listbox_absent.curselection()
            listbox_num = 2
        if idx:
            if (dev != END) & (dev != 0):
                new_idx = idx[0] + dev
            else:
                new_idx = dev
            if listbox_num == 1:
                if (new_idx == END):
                    pass
                elif (new_idx < 0) | (new_idx >= listbox_present.size()):
                    return
                item = listbox_present.get(idx[0])
                listbox_present.delete(idx[0])
                listbox_present.insert(new_idx, item)
                listbox_present.select_set(new_idx)
                listbox_present.activate(new_idx)
                listbox_present.see(new_idx)
            if listbox_num == 2:
                if (new_idx == END):
                    pass
                elif (new_idx < 0) | (new_idx >= listbox_absent.size()):
                    return
                item = listbox_absent.get(idx[0])
                listbox_absent.delete(idx[0])
                listbox_absent.insert(new_idx, item)
                listbox_absent.select_set(new_idx)
                listbox_absent.activate(new_idx)
                listbox_absent.see(new_idx)

    def replace_item():
        if listbox_present.curselection():
            idx = listbox_present.curselection()
            if idx:
                listbox_absent.insert(END, listbox_present.get(idx[0]))
                listbox_present.delete(idx[0])
                new_idx=min(idx[0], listbox_present.size()-1)
                listbox_present.select_set(new_idx)
                listbox_present.activate(new_idx)
        elif listbox_absent.curselection():
            idx = listbox_absent.curselection()
            if idx:
                listbox_present.insert(END, listbox_absent.get(idx[0]))
                listbox_absent.delete(idx[0])
                new_idx=min(idx[0], listbox_absent.size()-1)
                listbox_absent.select_set(new_idx)
                listbox_absent.activate(new_idx)

    def open_enterwindow(window):
        def get_input(*args):
            nonlocal input_text
            input_text = entry.get()
            tl.destroy()
        tl = Toplevel(window, background="white")
        tl.geometry("+857+360")
        tl.title("")
        tl.resizable(False, False)
        tl.attributes('-toolwindow', True)
        tl.grab_set()
        label = Label(tl, text="메신저가 켜져있지 않거나 id를 찾을 수 없습니다.\n사용중인 메신저 id를 입력하세요", background="white")
        label.grid(row=0, column=0, columnspan=2, sticky="ew")

        entry = Entry(tl)
        entry.bind("<Return>", get_input)
        entry.grid(row=1, column=0, sticky="ew")
        
        input_text = ""
        button = Button(tl, text="입력", command=get_input)
        button.grid(row=1, column=1, sticky="ew")

        tl.wait_window(tl)

        return input_text

    def toggle_miscwindow():
        global miscwindow
        try:
            if miscwindow.winfo_exists():
                miscwindow.destroy()
            else:
                open_miscwindow()
        except:
            open_miscwindow()

    def open_miscwindow():
        def profile(checkbox_profile):
            i = switch_profile()
            if i == 1:
                checkbox_profile.select()
                label_profile.config(image=example_profile_invsbl)
            elif i == 0:
                checkbox_profile.deselect()
                label_profile.config(image=example_profile_default)
        def balloon(checkbox_balloon):
            i = switch_balloon()
            if i == 'excel':
                checkbox_balloon.select()
                label_balloon.config(image=example_balloon_excel)
                open_descwindow("채팅창 배경화면 변경 방법", how_to_background)
            else:
                checkbox_balloon.deselect()
                label_balloon.config(image=example_balloon_default)
        def switch_hotkey():
            state = var_hotkey.get()
            if state:
                print(state)
                conn.send('start_hotkey')
                set_config('state_hotkey', '1')
                open_descwindow("단축키 설명", key_description)
                return '1'
            else:
                print(state)
                conn.send('stop_hotkey')
                set_config('state_hotkey', '0')
                return '0'
        def switch_watchdog(window):
            state = var_watchdog.get()
            if state:
                name = find_userid()
                if name is not None:
                    name = name[0]
                else:
                    name = open_enterwindow(window).split(' ')[0]
                if name:
                    conn.send('start_watchdog ' + name)
                    set_config('state_watchdog', name)
                    shutil.copyfile(resource_path('res/tab_Favorite_select_clock.bmp'),
                                    path + 'Tab/tab_Favorite_select.bmp')
                    shutil.copyfile(resource_path('res/tab_Favorite_main_clock.bmp'),
                                    path + 'Tab/tab_Favorite_main.bmp')
                else:
                    checkbox_watchdog.deselect()
                return name
            else:
                conn.send('stop_watchdog')
                set_config('state_watchdog', '0')
                shutil.copyfile(resource_path('res/tab_Favorite_select_default.bmp'),
                                path + 'Tab/tab_Favorite_select.bmp')
                shutil.copyfile(resource_path('res/tab_Favorite_main_default.bmp'),
                                path + 'Tab/tab_Favorite_main.bmp')
                try:
                    config = configparser.RawConfigParser()
                    config.optionxform = str
                    config.read(FAVORITE)
                    user = config["USER"]["user"]
                    shutil.copyfile(FAVORITE, FAVORITE+"."+user+".bak")
                except (FileNotFoundError, KeyError):
                    pass
                except:
                    pass
                finally:
                    try:
                        shutil.copyfile(FAVORITE+".fav.bak", FAVORITE)
                        os.remove(FAVORITE+".fav.bak")
                    except FileNotFoundError:
                        os.remove(FAVORITE)
                return '0'
        def switch_autostart():
            state = var_autostart.get()
            keypath = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_WRITE)
            if state:
                winreg.SetValueEx(keypath, MENAME, 0, winreg.REG_SZ, '"'+MEPATH+'" -silence')
                checkbox_hotkey.config(state=NORMAL)
                if str(read_config('state_hotkey')) != '0':
                    checkbox_hotkey.select()
                checkbox_watchdog.config(state=NORMAL)
                if str(read_config('state_watchdog')) != '0':
                    checkbox_watchdog.select()
                state_autostart = True
            else:
                try:
                    winreg.DeleteValue(keypath, MENAME)
                except FileNotFoundError:
                    pass
                checkbox_hotkey.config(state=DISABLED)
                checkbox_watchdog.config(state=DISABLED)
                if var_hotkey.get():
                    checkbox_hotkey.deselect()
                    switch_hotkey()
                if var_watchdog.get():
                    checkbox_watchdog.deselect()
                    switch_watchdog(miscwindow)
                state_autostart = False
            winreg.CloseKey(keypath)
        def open_descwindow(title: str, image: PhotoImage):
            descwindow = Toplevel(miscwindow)
            descsize = (700, 350)
            descwindow.geometry(str(descsize[0])+"x"+
                                str(descsize[1])+"+"+
                                str((WINDOWSIZE[0]-descsize[0])//2)+"+"+
                                str((WINDOWSIZE[1]-descsize[1])//2))
            descwindow.resizable(False, False)
            descwindow.attributes('-toolwindow', True)
            descwindow.title(title)
            descwindow.configure(bg='white')
            label = Label(descwindow, image=image)
            label.pack()
            
        global miscwindow
        miscwindow = Toplevel(mainwindow)
        miscwindow.geometry("+"+
                            str((WINDOWSIZE[0]+mainsize[0])//2)+"+"+
                            str((WINDOWSIZE[1]-mainsize[1])//2))
        # miscwindow.geometry("+857+360")
        miscwindow.resizable(False, False)
        miscwindow.attributes('-toolwindow', True)
        miscwindow.title('추가설정')
        miscwindow.configure(bg='white')
        # miscwindow.protocol("WM_DELETE_WINDOW", toggle_miscwindow)
        
        state_profile = int(read_config('hide_profile'))
        state_balloon = read_config('balloon_type')
        state_balloon = state_balloon if state_balloon else 'default'
        state_watchdog = str(read_config('state_watchdog'))
        state_hotkey = str(read_config('state_hotkey'))
        try:
            state_autostart = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ), MENAME)
        except:
            state_autostart = False
        checkbox_profile = Checkbutton(miscwindow, text="프로필사진 투명하게", background='white', activebackground='white', command=lambda: profile(checkbox_profile))
        checkbox_profile.grid(sticky = 'w')
        label_profile = Label(miscwindow, image=example_profile_default)
        if state_profile:
            checkbox_profile.select()
            label_profile.config(image=example_profile_invsbl)
        label_profile.grid(padx=(20,0), sticky = 'w')

        checkbox_balloon = Checkbutton(miscwindow, text="엑셀타입 말풍선 사용", background='white', activebackground='white', command=lambda: balloon(checkbox_balloon))
        checkbox_balloon.grid(sticky = 'w')
        label_balloon = Label(miscwindow, image=example_balloon_default)
        if state_balloon == 'excel':
            checkbox_balloon.select()
            label_balloon.config(image=example_balloon_excel)
        label_balloon.grid(padx=(20,0), sticky = 'w')
        
        var_autostart = IntVar()
        checkbox_autostart = Checkbutton(miscwindow, text="부팅 시 자동 시작", background='white', activebackground='white', command=switch_autostart, variable=var_autostart)
        checkbox_autostart.grid(sticky = 'w')
        if state_autostart:
            checkbox_autostart.select()
        
        var_hotkey = IntVar()
        checkbox_hotkey = Checkbutton(miscwindow, text="키보드 단축키 사용", background='white', activebackground='white', command=switch_hotkey, variable=var_hotkey)
        checkbox_hotkey.grid(sticky = 'w')
        if not (state_hotkey == '0'):
            checkbox_hotkey.select()
            
        global checkbox_watchdog
        var_watchdog = IntVar()
        checkbox_watchdog = Checkbutton(miscwindow, text="즐겨찾기탭을 최근사용탭으로 변경", background='white', activebackground='white', command=lambda: switch_watchdog(miscwindow), variable=var_watchdog)
        checkbox_watchdog.grid(sticky = 'w')
        if not (state_watchdog == '0'):
            checkbox_watchdog.select()
        if not state_autostart:
            checkbox_hotkey.config(state=DISABLED)
            checkbox_hotkey.deselect()
            checkbox_watchdog.config(state=DISABLED)
            checkbox_watchdog.deselect()

    def save_changes():
        try:
            changed = listbox_present.get(0,END)
            using = tabdict.name('TabName')
            reference = tabdict_reference.name('TabName')
            for missing in list(set(using) - set(reference)):
                tabdict_reference[missing] = tabdict[missing]
            reference = tabdict_reference.name('TabName')
            idxs = [reference.index(i) for i in changed]
            changed = [list(tabdict.values())[0]]
            changed += [list(tabdict_reference.values())[i] for i in idxs]
            print(changed)
            i = save_emoticons_xml(changed, itemdict.values())
            messagebox.showinfo('', i)
        except:
            messagebox.showwarning('', "저장 중 오류가 발생했습니다.")
    def show_preview(*args):
        def load_images(frame):
            nonlocal photos
            photos = []
            try:
                folder = name_to_folder_index[k_name]
            except KeyError:
                return
            except NameError:
                return
            for i, p in enumerate(all_in_folder[folder]):
                photo = PhotoImage(file=EMOTICON+folder+'/'+p)
                photos.append(photo)
                row, col = divmod(i, 3)
                label = ttk.Label(frame, image=photo, background="white")
                label.grid(row=row, column=col, padx=2, pady=2)
        
        if listbox_present.curselection():
            idx = listbox_present.curselection()
            k_name = listbox_present.get(idx[0])
        elif listbox_absent.curselection():
            idx = listbox_absent.curselection()
            k_name = listbox_absent.get(idx[0])

        frame_inside_canvas = Frame(canvas, background="white")
        canvas.create_window((0, 0), window=frame_inside_canvas, anchor="nw")
        load_images(frame_inside_canvas)

        frame_inside_canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    listbox_num = 0
    # xml load
    xml_reference, root_reference, tabdict_reference, itemdict_reference, xml, root, tabdict, itemdict = load_data()
    # BTNBOTONG 1


    tabdict.move(tabdict.index('BtnBotong'), 0)
    for missing in list(set(tabdict.name()) - set(tabdict_reference.name())):
        tabdict_reference[missing] = tabdict[missing]
    present, absent = present_or_absent(tabdict, tabdict_reference)


    # datas for image preview
    tabname_list = tabdict_reference.name("TabName")
    tabfolder_list = [t.attrib['TabControlNM'] for t in tabdict_reference.values()]
    tabicons_list = tabdict_reference.name("Img_Down")
    item_tabname_list = itemdict_reference.name("TabName")
    item_filename_list = itemdict_reference.name("Name")

    all_in_folder = defaultdict(list)
    for i, n in enumerate(item_tabname_list):
        all_in_folder[n].append(item_filename_list[i])
    name_to_folder_index = dict(zip(tabname_list, tabfolder_list))
    name_to_icons = dict(zip(tabname_list, tabicons_list))


    global mainwindow
    mainwindow = Tk()
    mainwindow.title(MENAME_KOR)
    mainsize = (585, 360)
    mainwindow.geometry(str(mainsize[0])+"x"+
                        str(mainsize[1])+"+"+
                        str((WINDOWSIZE[0]-mainsize[0])//2)+"+"+
                        str((WINDOWSIZE[1]-mainsize[1])//2))
    mainwindow.resizable(False, False)
    mainwindow.configure(bg='white')
    mainwindow.iconbitmap(resource_path('res/icon.ico'))
    lift_thread = Thread(target=pipe_listener, daemon=True)
    lift_thread.start()
    mainwindow.protocol('WM_DELETE_WINDOW', stop_listener)

    example_profile_default = PhotoImage(file=resource_path("res/example_profile_default.png"))
    example_profile_invsbl = PhotoImage(file=resource_path("res/example_profile_invsbl.png"))
    example_balloon_default = PhotoImage(file=resource_path("res/example_balloon_default.png"))
    example_balloon_excel = PhotoImage(file=resource_path("res/example_balloon_excel.png"))
    how_to_background = PhotoImage(file=resource_path("res/how_to_background.png"))
    key_description = PhotoImage(file=resource_path("res/key_description.png"))
    # 이미지 표시 구간
    main_frame = Frame(mainwindow)
    main_frame.grid(row=0, column=3, sticky="sw", rowspan=15, padx=12)

    canvas = Canvas(main_frame, background="white", width=320, height=322)
    canvas.grid(row=0, column=3, sticky="nsw", rowspan=15, pady=5, padx=5)

    scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=4, sticky="ns", rowspan=15)

    canvas.configure(yscrollcommand=scrollbar.set)
    photos=[]
    # 끝


    list_present = present.name('TabName')
    list_absent = absent.name('TabName')
    listbox_present = Listbox(mainwindow, height=10, activestyle='none', exportselection=True)
    listbox_absent = Listbox(mainwindow, height=6, activestyle='none', exportselection=True)
    listbox_present.bind('<<ListboxSelect>>', on_select_present)
    listbox_absent.bind('<<ListboxSelect>>', on_select_absent)
    listbox_present.configure(selectbackground='#CDE1FA')
    listbox_present.configure(selectforeground='black')
    listbox_absent.configure(selectbackground='#CDE1FA')
    listbox_absent.configure(selectforeground='black')

    for i in list_present[1:]:
        listbox_present.insert(END, i)
    for i in list_absent:
        listbox_absent.insert(END, i)

    label_present = Label(mainwindow, text='[사용중 탭]')
    label_absent = Label(mainwindow, text='[미사용 탭]')
    label_present.grid(row=0, column=0, sticky="w", padx=8, pady=(8,0))
    label_absent.grid(row=10, column=0, sticky="w", padx=8, pady=(0,0))
    label_present.configure(bg='white')
    label_absent.configure(bg='white')

    # scrollbar_present = Scrollbar(mainwindow, orient='vertical')
    # scrollbar_present.pack(side='right', fill='y')
    # listbox_present.config(yscrollcommand=scrollbar_present.set)
    # scrollbar_present.config(command=listbox_present.yview)

    listbox_present.grid(row=1, column=0, sticky="n", padx=8, rowspan=8)
    listbox_absent.grid(row=11, column=0, sticky="n", padx=8, rowspan=4)

    def normal(button, image, *args):
        button.config(image=image[0])
    def hover(button, image, *args):
        button.config(image=image[1])
    def click(button, image, *args):
        button.config(image=image[2])

    # load buttons
    image_path = 'res/buttons/'
    types_image = ['normal.png', 'hover.png', 'click.png']
    up_image_path = [resource_path(i) for i in [image_path + 'up_'+t for t in types_image]]
    down_image_path = [resource_path(i) for i in [image_path + 'down_'+t for t in types_image]]
    top_image_path = [resource_path(i) for i in [image_path + 'top_'+t for t in types_image]]
    bottom_image_path = [resource_path(i) for i in [image_path + 'bottom_'+t for t in types_image]]
    add_image_path = [resource_path(i) for i in [image_path + 'add_'+t for t in types_image]]
    misc_image_path = [resource_path(i) for i in [image_path + 'misc_'+t for t in types_image]]
    save_image_path = [resource_path(i) for i in [image_path + 'save_'+t for t in types_image]]

    up_image = [PhotoImage(file=i) for i in up_image_path]
    down_image = [PhotoImage(file=i) for i in down_image_path]
    top_image = [PhotoImage(file=i) for i in top_image_path]
    bottom_image = [PhotoImage(file=i) for i in bottom_image_path]
    add_image = [PhotoImage(file=i) for i in add_image_path]
    misc_image = [PhotoImage(file=i) for i in misc_image_path]
    save_image = [PhotoImage(file=i) for i in save_image_path]
    button_up = Button(mainwindow, command=lambda: moveitem(-1), text="🔼", width=25, height=21, relief=FLAT, image=up_image[0], bd=0, highlightthickness=0)
    button_up.bind('<ButtonPress>', lambda event: click(button_up, up_image))
    button_up.bind('<ButtonRelease>', lambda event: hover(button_up, up_image))
    button_up.bind('<Enter>', lambda event: hover(button_up, up_image))
    button_up.bind('<Leave>', lambda event: normal(button_up, up_image))
    button_down = Button(mainwindow, command=lambda: moveitem(1), text="🔽", width=25, height=21, relief=FLAT, image=down_image[0], bd=0, highlightthickness=0)
    button_down.bind('<ButtonPress>', lambda event: click(button_down, down_image))
    button_down.bind('<ButtonRelease>', lambda event: hover(button_down, down_image))
    button_down.bind('<Enter>', lambda event: hover(button_down, down_image))
    button_down.bind('<Leave>', lambda event: normal(button_down, down_image))
    button_top = Button(mainwindow, command=lambda: moveitem(0), text="🔽", width=25, height=21, relief=FLAT, image=top_image[0], bd=0, highlightthickness=0)
    button_top.bind('<ButtonPress>', lambda event: click(button_top, top_image))
    button_top.bind('<ButtonRelease>', lambda event: hover(button_top, top_image))
    button_top.bind('<Enter>', lambda event: hover(button_top, top_image))
    button_top.bind('<Leave>', lambda event: normal(button_top, top_image))
    button_bottom = Button(mainwindow, command=lambda: moveitem(END), text="🔽", width=25, height=21, relief=FLAT, image=bottom_image[0], bd=0, highlightthickness=0)
    button_bottom.bind('<ButtonPress>', lambda event: click(button_bottom, bottom_image))
    button_bottom.bind('<ButtonRelease>', lambda event: hover(button_bottom, bottom_image))
    button_bottom.bind('<Enter>', lambda event: hover(button_bottom, bottom_image))
    button_bottom.bind('<Leave>', lambda event: normal(button_bottom, bottom_image))
    button_top.grid(row=4, column=1, sticky='nw')
    button_up.grid(row=5, column=1, sticky='nw')
    button_down.grid(row=6, column=1, sticky='nw')
    button_bottom.grid(row=7, column=1, sticky='nw')
        
    button_add = Button(mainwindow, command=replace_item, relief=FLAT, image=add_image[0], bd=0, highlightthickness=0, pady=8)
    button_add.grid(row=9, column=0, sticky="nsew", padx=8)
    button_add.bind('<ButtonPress>', lambda event: click(button_add, add_image))
    button_add.bind('<ButtonRelease>', lambda event: hover(button_add, add_image))
    button_add.bind('<Enter>', lambda event: hover(button_add, add_image))
    button_add.bind('<Leave>', lambda event: normal(button_add, add_image))
    
    button_misc = Button(mainwindow, command=toggle_miscwindow, relief=FLAT, image=misc_image[0], bd=0, highlightthickness=0)
    button_misc.bind('<ButtonPress>', lambda event: click(button_misc, misc_image))
    button_misc.bind('<ButtonRelease>', lambda event: hover(button_misc, misc_image))
    button_misc.bind('<Enter>', lambda event: hover(button_misc, misc_image))
    button_misc.bind('<Leave>', lambda event: normal(button_misc, misc_image))
    button_save = Button(mainwindow, command=save_changes, relief=FLAT, image=save_image[0], bd=0, highlightthickness=0)
    button_save.bind('<ButtonPress>', lambda event: click(button_save, save_image))
    button_save.bind('<ButtonRelease>', lambda event: hover(button_save, save_image))
    button_save.bind('<Enter>', lambda event: hover(button_save, save_image))
    button_save.bind('<Leave>', lambda event: normal(button_save, save_image))
    button_misc.grid(row=13, column=1, sticky='ws', pady=0)
    button_save.grid(row=14, column=1, sticky='ws', pady=0)

    

    mainwindow.mainloop()

if __name__ == '__main__':
    gui_main()