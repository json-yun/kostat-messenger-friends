import win32gui
import win32api
import win32con
import time
from pynput.keyboard import Listener, Key, KeyCode
# from multiprocess import Process

class Messenger:
    DPOS = {7: (60, 60), 8: (170, 60), 9: (280, 60),
            4: (60, 160), 5: (170, 160), 6: (280, 160),
            1: (60, 260), 2: (170, 260), 3: (280, 260)}
    def __init__(self):
        self.hwnd_chatroom = None
        self.hwnd_emo = None
        self.hwnd_tabs = None
        self.hwnd_sheet = None
        self.hwnd_textbox = None
        self.pos = None
        self.hwnd_tabarrow_left = None
        self.hwnd_tabarrow_right = None
    def Return(self, hwnd):
        win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    def CloseWindow(self, hwnd):
        win32api.SendMessage(hwnd, win32con.WM_APP+12321, 0, 0)
        self.__init__()
    def Click(self, hwnd, x=0, y=0, up=False):
        lParam = win32api.MAKELONG(x,y)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        if up:
            win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)
    def Scroll(self, hwnd, times, x=80, y=80):
        lParam = win32api.MAKELONG(x,y)
        win32api.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, 39 * times, lParam)
    def GetChatroomHandle(self, wait=0):
        start_time = time.time()
        while True:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                classname = win32gui.GetClassName(hwnd)
                if classname == "TfrmDccChat":
                    self.hwnd_chatroom = hwnd
                    return self.hwnd_chatroom
            else:
                return 0
            if time.time() - start_time > wait:
                return 0
            win32api.Sleep(150)
    def GetEmoHandle(self, wait=0):
        start_time = time.time()
        while True:
            hwnd = win32gui.GetForegroundWindow()
            classname = win32gui.GetClassName(hwnd)
            if classname == "TfrmEmoticon":
                self.hwnd_emo = hwnd
                self.pos = 0
                self.GetTabHandles(wait=0.5)
                self.GetSheetHandle()
                win32api.Sleep(50)
                win32api.SendMessage(self.hwnd_sheet, win32con.WM_MOUSEMOVE, 0, 11141290)
                return self.hwnd_emo
            elif (self.hwnd_emo is not None) and (not win32gui.FindWindow(None, "이모티콘")):
                self.hwnd_emo = None
            if time.time() - start_time > wait:
                return 0
            win32api.Sleep(150)
    def GetTabHandles(self, wait=0):
        start_time = time.time()
        while True:
            hwnd_1 = win32gui.FindWindowEx(self.hwnd_emo, None, "TEzFlatPanelW", None)
            hwnd_2 = win32gui.FindWindowEx(hwnd_1, None, "TEzImagePanelW", None)
            hwnd_3 = win32gui.FindWindowEx(hwnd_2, None, "TEzImagePanelW", None)
            hwnd_4 = win32gui.FindWindowEx(hwnd_3, None, "TElScrollBox", None)
            self.hwnd_tabs = []
            win32gui.EnumChildWindows(hwnd_4, lambda x, _: self.hwnd_tabs.append(x) if win32gui.GetClassName(x) == "TEmotiTabList" else None, None)
            self.hwnd_tabarrow_left = win32gui.FindWindowEx(hwnd_3, None, "TspSkinXFormButtonW", None)
            self.hwnd_tabarrow_right = win32gui.FindWindowEx(hwnd_3, self.hwnd_tabarrow_left, "TspSkinXFormButtonW", None)

            if self.hwnd_tabs:
                return self.hwnd_tabs
            elif time.time() - start_time > wait:
                return 0
            win32api.Sleep(150)
    def GetSheetHandle(self):
        hwnd_1 = win32gui.FindWindowEx(self.hwnd_emo, None, "TEzFlatPanelW", None)
        hwnd_2 = win32gui.FindWindowEx(hwnd_1, None, "TEzImagePanelW", None)
        hwnd_3 = win32gui.FindWindowEx(hwnd_2, None, "TElPageControl", None)
        hwnd_4 = win32gui.FindWindowEx(hwnd_3, None, "TElTabSheet", None)
        self.hwnd_sheet = win32gui.FindWindowEx(hwnd_4, None, "TElScrollBox", None)
        return self.hwnd_sheet
    def GetTextboxHandle(self):
        self.hwnd_textbox = win32gui.FindWindowEx(self.hwnd_chatroom, None, "TRichEdit", None)
        return self.hwnd_textbox

    def SwitchTabWindow(self):
        if self.GetChatroomHandle():
            rect = win32gui.GetWindowRect(self.hwnd_chatroom)
            height = rect[3]-rect[1]
            self.Click(self.hwnd_chatroom, 30, height-70, True)
            win32api.Sleep(50)
            self.GetEmoHandle(wait=0.5)
        else:
            hwnd = win32gui.GetForegroundWindow()
            if win32gui.GetClassName(hwnd) == "TfrmEmoticon":
                self.CloseWindow(hwnd)
                self.hwnd_emo = None
                self.hwnd_tabs = None
                self.hwnd_sheet = None
                self.hwnd_textbox = None
                self.pos = None
                self.hwnd_tabarrow_left = None
                self.hwnd_tabarrow_right = None
    def SendEmo(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if win32gui.GetClassName(hwnd) == "TfrmEmoticon":
                self.CloseWindow(hwnd)
                if self.GetChatroomHandle(wait=0.3):
                    self.Return(self.GetTextboxHandle())
        except:
            pass
    def SelectEmoItem(self, num):
        if self.hwnd_emo is None:
            return
        hwnd = win32gui.GetForegroundWindow()
        if (hwnd == self.hwnd_emo) or (hwnd == self.GetEmoHandle()):
            self.Click(self.hwnd_sheet, self.DPOS[num][0], self.DPOS[num][1], True)
    def ScrollSheet(self, times):
        if self.hwnd_emo is None:
            return
        hwnd = win32gui.GetForegroundWindow()
        if (hwnd == self.hwnd_emo) or (hwnd == self.GetEmoHandle()):
            self.Scroll(self.hwnd_sheet, times)
    def MoveTab(self, offset):
        if self.hwnd_emo is None:
            return
        hwnd = win32gui.GetForegroundWindow()
        if (hwnd == self.hwnd_emo) or (hwnd == self.GetEmoHandle()):
            if self.hwnd_tabs:
                self.pos += offset
                self.pos = self.pos % len(self.hwnd_tabs)
                self.Click(self.hwnd_tabs[self.pos], up=True)
    def MoveTabTo(self, idx):
        if self.hwnd_emo is None:
            return
        hwnd = win32gui.GetForegroundWindow()
        if (hwnd == self.hwnd_emo) or (hwnd == self.GetEmoHandle()):
            if self.hwnd_tabs:
                self.pos = idx % len(self.hwnd_tabs)
                self.Click(self.hwnd_tabs[self.pos], up=True)
    def CancelSelection(self):
        try:
            if self.hwnd_chatroom and (self.GetEmoHandle() == win32gui.GetForegroundWindow()):
                hwnd_1 = win32gui.FindWindowEx(self.hwnd_chatroom, None, "TEzFlatPanelW", None)
                hwnd_2 = win32gui.FindWindowEx(hwnd_1, None, "TezFlatButtonW", None)
                if hwnd_2:
                    self.Click(hwnd_2, 0, 0, True)
                    win32gui.SetForegroundWindow(self.hwnd_emo)
        except:
            return

messenger = Messenger()
class HotkeyListener(Listener):
    TIMELIMIT = 0.00
    KEY_HANDLERS = {("Key.tab",): lambda allow_dup: messenger.SwitchTabWindow() if allow_dup else None,
                    (97,): lambda _: messenger.SelectEmoItem(1),
                    (98,): lambda _: messenger.SelectEmoItem(2),
                    (99,): lambda _: messenger.SelectEmoItem(3),
                    (100,): lambda _: messenger.SelectEmoItem(4),
                    (101,): lambda _: messenger.SelectEmoItem(5),
                    (102,): lambda _: messenger.SelectEmoItem(6),
                    (103,): lambda _: messenger.SelectEmoItem(7),
                    (104,): lambda _: messenger.SelectEmoItem(8),
                    (105,): lambda _: messenger.SelectEmoItem(9),
                    (110,): lambda _: messenger.CancelSelection(),
                    ("Key.backspace",): lambda _: messenger.CancelSelection(),
                    ("Key.right",): lambda _: messenger.MoveTab(1),
                    (106,): lambda _: messenger.MoveTab(1),
                    ("Key.left",): lambda _: messenger.MoveTab(-1),
                    (111,): lambda _: messenger.MoveTab(-1),
                    ("Key.up",): lambda _: messenger.ScrollSheet(3),
                    (109,): lambda _: messenger.ScrollSheet(3),
                    ("Key.down",): lambda _: messenger.ScrollSheet(-3),
                    (107,): lambda _: messenger.ScrollSheet(-3),
                    ("Key.enter",): lambda allow_dup: messenger.SendEmo() if allow_dup else None,
                    (192,): lambda _: messenger.MoveTabTo(0),
                    (49,): lambda _: messenger.MoveTabTo(1),
                    (50,): lambda _: messenger.MoveTabTo(2),
                    (51,): lambda _: messenger.MoveTabTo(3),
                    (52,): lambda _: messenger.MoveTabTo(4),
                    (53,): lambda _: messenger.MoveTabTo(5),
                    (54,): lambda _: messenger.MoveTabTo(6),
                    (55,): lambda _: messenger.MoveTabTo(7),
                    (56,): lambda _: messenger.MoveTabTo(8),
                    (57,): lambda _: messenger.MoveTabTo(9),
                    (48,): lambda _: messenger.MoveTabTo(10),
                    (189,): lambda _: messenger.MoveTabTo(11),
                    (187,): lambda _: messenger.MoveTabTo(12),
                    (220,): lambda _: messenger.MoveTabTo(13)
                    }
    def __init__(self, ignore_key=(21,25)):
        super().__init__(self.on_press, self.on_release)
        self.key_store = set()
        self.triggered_func = set()
        self.ignore_key = set(ignore_key)
        self.lasttime = time.time()
    def on_press(self, key):
        now = time.time()
        if now - self.lasttime < self.TIMELIMIT:
            return
        try:
            key = key.vk
        except:
            key = str(key)
        if key not in self.key_store.union(self.ignore_key):
            self.key_store.add(key) if key not in (21, 25) else None
            for triggers, function in self.KEY_HANDLERS.items():
                if all([True if trigger in self.key_store else False for trigger in triggers]):
                    if triggers not in self.triggered_func:
                        self.lasttime = now
                        function(self.key_store==set(triggers))
                        self.triggered_func.add(triggers)
                        return
    def on_release(self, key):
        try:
            key = key.vk
        except:
            key = str(key)
        self.key_store.discard(key)
        for triggers in self.triggered_func:
            if key in triggers:
                self.triggered_func.discard(triggers)
                break
    def is_alive(self, _is_in_loop: bool=False):
        if _is_in_loop:
            return super().is_alive()
        else:
            try:
                return self._listener.is_alive(True)
            except AttributeError:
                return False
    def start(self, _is_in_loop: bool=False):
        if _is_in_loop:
            super().start()
        else:
            self._listener = HotkeyListener(ignore_key=self.ignore_key)
            self._listener.start(True)
    def stop(self, _is_in_loop: bool=False):
        if _is_in_loop:
            super().stop()
        else:
            self._listener.stop(True)

if __name__=="__main__":
    listener = HotkeyListener()
    try:
        def listener_start():
            messenger = Messenger()
            listener = HotkeyListener()
            listener.start()
            
        # listener.start()
        print("activated")
        time.sleep(3)
        print("stopped")
        # listener.stop()
        time.sleep(3)
        # listener.start()
        time.sleep(3)
    except KeyboardInterrupt:
        listener.stop()
    except:
        raise
