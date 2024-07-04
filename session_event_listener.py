from collections import defaultdict
from enum import Enum
import win32api
import win32con
import win32gui
import win32ts
from threading import Thread
import time

class SessionEvent(Enum):
    ANY = 0
    # window messages
    CHANGE = 0x2B1  # WM_WTSSESSION_CHANGE
    # WM_WTSSESSION_CHANGE events (wparam)
    CONSOLE_CONNECT = 0x1  # WTS_CONSOLE_CONNECT
    CONSOLE_DISCONNECT = 0x2  # WTS_CONSOLE_DISCONNECT
    REMOTE_CONNECT = 0x3  # WTS_REMOTE_CONNECT
    REMOTE_DISCONNECT = 0x4  # WTS_REMOTE_DISCONNECT
    SESSION_LOGON = 0x5  # WTS_SESSION_LOGON
    SESSION_LOGOFF = 0x6  # WTS_SESSION_LOGOFF
    SESSION_LOCK = 0x7  # WTS_SESSION_LOCK
    SESSION_UNLOCK = 0x8  # WTS_SESSION_UNLOCK
    SESSION_REMOTE_CONTROL = 0x9  # WTS_SESSION_REMOTE_CONTROL

class WorkstationMonitor:
    CLASS_NAME = "WorkstationMonitor"
    WINDOW_TITLE = "Workstation Event Monitor"

    def __init__(self):
        self.window_handle = None
        self.event_handlers = defaultdict(list)
        self.i = 0
        self._register_listener()

    def _register_listener(self):
        wc = win32gui.WNDCLASS()
        wc.hInstance = self.handle_instance = win32api.GetModuleHandle(None)
        wc.lpszClassName = self.CLASS_NAME+str(self.i)
        self.i += 1
        wc.lpfnWndProc = self._window_procedure
        self.window_class = win32gui.RegisterClass(wc)

        style = 0
        self.window_handle = win32gui.CreateWindow(self.window_class,
                                                self.WINDOW_TITLE,
                                                style,
                                                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                                0, 0, self.handle_instance, None)
        win32gui.UpdateWindow(self.window_handle)

        scope = win32ts.NOTIFY_FOR_THIS_SESSION
        # scope = win32ts.NOTIFY_FOR_ALL_SESSIONS
        win32ts.WTSRegisterSessionNotification(self.window_handle, scope)
    
    def listen(self):
        win32gui.PumpMessages()
        # win32gui.DestroyWindow(self.window_handle)
        # print("destroy")
        # win32gui.UnregisterClass(self.window_class, None)
        # print("unregeister")

    def stop(self):
        exit_code = win32con.WM_QUIT
        # win32gui.PostQuitMessage(0)
        win32gui.PostMessage(self.window_handle, exit_code, 0, 0)
        print("stopped")

    def _window_procedure(self, window_handle: int, message: int, wparam, lparam):
        """
        # WindowProc callback function

        https://msdn.microsoft.com/en-us/library/ms633573(v=VS.85).aspx
        """
        if message == SessionEvent.CHANGE.value:
            self._handle_session_change(SessionEvent(wparam), lparam)
            return 0  # 처리된 메시지에 대해 0을 반환
        elif message == win32con.WM_CLOSE:
            win32gui.DestroyWindow(window_handle)
            return 0
        elif message == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        elif message == win32con.WM_QUERYENDSESSION:
            return True  # 이 메시지는 True를 반환해야 합니다.
        else:
            # 처리하지 않은 메시지에 대해 DefWindowProc 호출
            return win32gui.DefWindowProc(window_handle, message, wparam, lparam)

    def _handle_session_change(self, event: SessionEvent, session_id: int):
        for handler in self.event_handlers[event]:
            handler(event)
        for handler in self.event_handlers[SessionEvent.ANY]:
            handler(event)
    
    def register_handler(self, event: SessionEvent, handler: callable):
        self.event_handlers[event].append(handler)



if __name__ == '__main__':
    def printunlock(*args):
        print(args)
        [print(type(i), i) for i in args]
    m = WorkstationMonitor()
    m.register_handler(SessionEvent.SESSION_UNLOCK, handler=printunlock)

    def stopafter():
        time.sleep(3)
        m.stop()
    t = Thread(target=stopafter)
    t.start()
    m.listen()
    t.join()
    import time
    time.sleep(10)
    print("start again")
    m.listen()

# destroywindow와 unregister는 동일 스레드 안에서 이루어져야 함
# 하지만 pumpmessages가 await해서 방법을 찾아야...
# pumpmessages 중단 못하면 그냥 상시 실행으로 두는 쪽으로.<<<<<<===
# 되긴 하는데 이전 기록까지 한꺼번에 나옴