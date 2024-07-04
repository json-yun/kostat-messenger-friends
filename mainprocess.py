# from multiprocess import Process, Pipe
import time
from threading import Thread, Event
from multiprocessing import Process, Pipe, freeze_support
from Socket_Singleton import Socket_Singleton, MultipleSingletonsError
import socket
import sys
from pystray import Icon, Menu, MenuItem
from PIL import Image
import recent_watchdog
import window_interface
import hotkeys
from emoticon_module import path, resource_path, read_config, set_config, MENAME, MENAME_KOR
# from session_event_listener import WindowClassRegister
from win10toast import ToastNotifier
import session_event_listener

class StoppableThread(Thread):
    def __init__(self, user=None, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=False):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self._stop_event = Event()
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()

def main(sysarg):
    freeze_support()
    def run_tray():
        print("run tray")
        def exit_action(icon, item):
            icon.stop()

        image = Image.new('RGB', (64, 64), color='white')
        image = Image.open(resource_path("res/icon.ico"))
        menu = (MenuItem('열기', start_window), MenuItem('종료', exit_action))
        icon = Icon("name", image, MENAME_KOR, menu)
        icon.run()

    def start_window():
        global window_thread
        nonlocal parent_conn, child_conn
        try:
            if not window_thread.is_alive():
                raise
        except:
            window_thread = Process(target=window_interface.gui_main, args=(child_conn,), daemon=True) # 인터페이스 프로세스 시작
            window_thread.start()
        else:
            parent_conn.send('lift')
    def inf_start(thread_object, arg):
        thread = thread_object(arg)
        thread.start()
        while not thread.stopped():
            print(thread.stopped())
            try:
                if not thread.is_alive():
                    raise
            except:
                thread = thread_object(arg)
                thread.start()
            else:
                time.sleep(1)
        thread.stop()
    def start_hotkey():
        global hotkey_thread, last_restarted
        
        try:
            if not hotkey_thread.is_alive():
                raise
        except:
            hotkey_thread.start()
            last_restarted = time.time()
        else:
            print("hotkey already running")
    def stop_hotkey():
        global hotkey_thread
        try:
            if not hotkey_thread.is_alive():
                raise
        except:
            pass
        else:
            print("Stopping")
            hotkey_thread.stop()
    def restart_hotkey(msg):
        global hotkey_thread, last_restarted
        print(msg)
        try:
            if hotkey_thread.is_alive():
                now = time.time()
                print("restarting")
                if now - last_restarted > 1:
                    last_restarted = now
                    hotkey_thread.stop()
                    time.sleep(1)
                    hotkey_thread = hotkeys.HotkeyListener()
                    hotkey_thread.start()
        except:
            pass

    def start_watchdog(id):
        global watchdog_thread
        try:
            if not watchdog_thread.is_alive():
                raise
        except:
            if recent_watchdog.EmoticonWatchdog(id).current_time != 0:
                watchdog_thread = recent_watchdog.EmoticonWatchdog(id, daemon=True)
                watchdog_thread.start()
        else:
            print("watchdog already running")
    def stop_watchdog():
        global watchdog_thread
        try:
            if not watchdog_thread.is_alive():
                raise
        except:
            pass
        else:
            watchdog_thread.stop()
        
    def pipe_listener():
        nonlocal parent_conn
        while True:
            try:
                item = parent_conn.recv()
                print("received: "+item)
            except EOFError:
                time.sleep(1)
            else:
                if 'start_hotkey' in item:
                    start_hotkey()
                elif 'stop_hotkey' in item:
                    stop_hotkey()
                elif 'start_watchdog' in item:
                    start_watchdog(item.split(' ')[-1])
                elif 'stop_watchdog' in item:
                    print("stop_watchdog")
                    stop_watchdog()

    def socket_server(window_start, watchdog_start, hotkey_start):
        if window_start:
            start_window()
        if watchdog_start:
            start_watchdog(watchdog_start)
        if hotkey_start:
            start_hotkey()
        while True:
            # 클라이언트의 연결 요청을 기다림
            client_socket, addr = server_socket.accept()
            # 클라이언트로부터 데이터를 받음
            msg = client_socket.recv(1024).decode('utf-8')
            msg = msg.split(" ")
            print(msg)
            # if 'tray_thread' in msg:
            #     if not tray_thread.is_alive():
            #         tray_thread = Thread(target=run_tray, daemon=True)
            #         tray_thread.start()
            if 'window_thread' in msg:
                start_window()
                
            client_socket.close()
    # 초기화
    if '-init' in sysarg[1:]:
        import initializer
        initializer.initialize()
        print("initialize complete")
        return 0
    
    try:
        me = Socket_Singleton(strict=False)
    except MultipleSingletonsError:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 39390))
        # 이미 실행 중인 경우, 서버에 메시지를 전달하고 종료
        client_socket.sendall('tray_thread window_thread'.encode('utf-8'))
        client_socket.close()
        return -1
    
    toaster = ToastNotifier()

    try:
        state_watchdog = read_config('state_watchdog')
        state_watchdog = state_watchdog if state_watchdog != '0' else False
    except FileNotFoundError:
        state_watchdog = False
    try:
        state_hotkey = read_config('state_hotkey')
        state_hotkey = True if state_hotkey != '0' else False
    except FileNotFoundError:
        state_hotkey = False
    # handle_instance, window_class = WindowClassRegister()
    # 서버 소켓 설정
    try:
        parent_conn, child_conn = Pipe()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 39390))
        server_socket.listen()
        silence = '-silence' in sysarg[1:]
        global hotkey_thread
        hotkey_thread = hotkeys.HotkeyListener()
        server_thread = Thread(target=socket_server, args=(not silence, state_watchdog, state_hotkey), daemon=True)
        server_thread.start()
        pipe_thread = Thread(target=pipe_listener, daemon=True)
        pipe_thread.start()
    except:
        raise
    else:
        toaster.show_toast(MENAME_KOR,
                           "백그라운드 프로세스가 실행 중입니다.",
                           icon_path=resource_path("./res\\icon.ico"),
                           duration=5,
                           threaded=True)
        session_listener = session_event_listener.WorkstationMonitor()
        session_listener.register_handler(session_event_listener.SessionEvent.SESSION_UNLOCK, restart_hotkey)
        Thread(target=session_listener.listen, daemon=True).start()
        print("run")
        run_tray()
    return 0
    # tray_thread = Thread(target=run_tray, daemon=True)
    # tray_thread.start()
    # while True:
    #     try:
    #         time.sleep(1)
    #     except KeyboardInterrupt:
    #         break

if __name__ == '__main__':
    sys.exit(main(sys.argv))