import time
import glob
import shutil
import base64
import sqlite3
import configparser
import os
import hashlib
from threading import Thread, Event
import winreg
from emoticon_module import ROOT, FAVORITE, DATAPATH

MAXSIZE = 36
INTERVAL = 0.5

def encode(text):
    return base64.b64encode(text.encode('utf-16le')).decode()
def decode(code):
    return base64.b64decode(code).decode('utf-16le')
def find_userid():
    pathes = [i.replace("ChatList.edb-journal", "") for i in glob.glob(DATAPATH+"*\\ChatList.edb-journal")]
    target_hash = [i.split("\\")[-2].upper() for i in pathes]
    for path in pathes:
        chatlogs = glob.glob(path+"ChatLog_*.edb")
        candidates = [(i.split(".")[-2], hashlib.md5(i.split(".")[-2].encode()).hexdigest().upper()) for i in chatlogs]
        for name_r, name_h in candidates:
            if name_h in target_hash:
                return name_r, name_h
        shutil.copyfile(path+"ChatList.edb", path+"ChatList.edb.tmp")
        conn = sqlite3.connect(path+"ChatList.edb.tmp")
        cursor = conn.cursor()
        cursor.execute("SELECT MEMBERIDLIST FROM CHATROOM")
        idset = set()
        for idlist in cursor.fetchall():
            idset = idset | set([i.split("|")[0] for i in decode(idlist[0]).split(";")])
        for id_ in idset:
            name_h = hashlib.md5(id_.encode()).hexdigest().upper()
            if name_h in target_hash:
                return id_, name_h

        # for l in chatlogs:
        #     conn = sqlite3.connect(l)
        #     try:
        #         cursor = conn.cursor()
        #         cursor.execute("SELECT DISTINCT SENDERID FROM CHATLOG")
        #     except sqlite3.OperationalError:
        #         pass
        #     except:
        #         pass
        #     else:
        #         for b64 in cursor.fetchall():
        #             name_r = decode(b64[0])
        #             name_h = hashlib.md5(name_r.encode()).hexdigest().upper()
        #             if name_h in target_hash:
        #                 return name_r, name_h
        #     conn.close()
    return None

class EmoticonWatchdog(Thread):
    def __init__(self, user=None, group=None, name=None, args=(), kwargs={}, *, daemon=True):
        super().__init__(group=group, target=self.start_recent, name=name, args=args, kwargs=kwargs, daemon=daemon)
        if user is not None:
            self.user = user
            self.usercode = hashlib.md5(user.encode()).hexdigest()
        else:
            self.user, self.usercode = find_userid()
        self.user64 = encode(self.user)
        self.switch = False
        self.current_time = self.get_current_time()
        self._stop_event = Event()
    
    def get_current_time(self):
        files = [x[:-8] for x in glob.glob(DATAPATH+self.usercode+"/*.edb-journal") if not x.endswith('ChatList.edb-journal')]
        try:
            files.append(max(glob.glob(DATAPATH+self.usercode+"/ChatLog_*.edb"), key=os.path.getmtime))
        except ValueError:
            print("입력한 id의 기록을 찾을 수 없습니다. "+self.user+" "+self.usercode)
            self.stop()
            return 0
        files = [f.replace("\\", "/") for f in files]
        list_of_dates = []
        for file in files:
            temp = file+".tmp"
            print(temp)
            shutil.copyfile(file, temp)
            conn = sqlite3.connect(temp)
            cursor = conn.cursor()
            cursor.execute("SELECT SAVE_DATE FROM (SELECT * FROM CHATLOG ORDER BY ROWID DESC LIMIT 1)")
            list_of_dates.append(cursor.fetchall()[0][0])
            conn.close()
        list_of_dates.sort()
        return list_of_dates[-1]

    def compare_files_reverse(self, file1_path, file2_path):
        block_size = 4096  # 블록 크기 (조정 가능)
        
        try:
            with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
                file1.seek(-block_size, 2)  # 파일 포인터를 파일 끝으로 이동
                file2.seek(-block_size, 2)
                
                block1 = file1.read(block_size)
                block2 = file2.read(block_size)
                
                if block1 == block2:
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False

    def add_new_recent_item(self, dbfile):
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        cursor.execute(f"SELECT OPT1, SAVE_DATE FROM (SELECT * FROM CHATLOG ORDER BY ROWID DESC LIMIT 10) AS SQ WHERE SAVE_DATE > '{self.current_time}' AND OPT1 <> '' AND SENDERID = '{self.user64}'")
        list_of_emote = list(cursor.fetchall())
        conn.close()
        if list_of_emote:
            new = [decode(i[0]) for i in list_of_emote]
            config = configparser.RawConfigParser()
            config.optionxform = str
            config.read(FAVORITE)
            try:
                list_fav = list(config["FAVORITE"].values())
            except KeyError:
                list_fav = []
                config["FAVORITE"] = {}
            for i, n in enumerate(new):
                while n in list_fav:
                    list_fav.remove(n)
                list_fav.insert(i, n)
            new_dict = {}
            for i in range(0, min(len(list_fav), MAXSIZE)):
                new_dict[str(i)] = list_fav[i]
            config.read_dict({'FAVORITE': new_dict})
            self.current_time = list_of_emote[0][1]
            with open(FAVORITE, 'w') as configfile:
                config.write(configfile)
    
    # def start(self):
    #     self.switch = True
    #     super().start()

    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()

    def start_recent(self):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(FAVORITE)
        try:
            user = config["USER"]["user"]
            if user != self.user:
                raise KeyError
        except KeyError:
            try:
                shutil.copyfile(FAVORITE, FAVORITE+".fav.bak")
            except FileNotFoundError:
                pass
            except:
                pass
            try:
                shutil.copyfile(FAVORITE+"."+self.user+".bak", FAVORITE)
                os.remove(FAVORITE+"."+self.user+".bak")
                config.read(FAVORITE)
                user = config["USER"]["user"]
                if user != self.user:
                    raise FileNotFoundError
            except FileNotFoundError:
                list_fav = []
                config["FAVORITE"] = {}
                config["USER"] = {"user": self.user}
                with open(FAVORITE, 'w') as configfile:
                    config.write(configfile)
        
        while not self.stopped():
            try:
                files = [x[:-8] for x in glob.glob(DATAPATH+self.usercode+"/*.edb-journal") if not x.endswith('ChatList.edb-journal')]
                for file in files:
                    temp = file+".tmp"
                    if not self.compare_files_reverse(file, temp):
                        shutil.copyfile(file, temp)
                        self.add_new_recent_item(temp)
                time.sleep(INTERVAL)
                # journey파일 있는 것만 복사
                # journey파일 존재하는 동안 파일 비교하고 업데이트
                # 업데이트 있으면 sql문 수행, 최근사용 가져옴
                # journey파일 사라지면 마지막으로 복사, sql문 수행하고 파일 삭제
            except (KeyboardInterrupt, SystemExit):
                self.stop()
                break
            except:
                pass
        return
        


if __name__=="__main__":
    try:
        E = EmoticonWatchdog(daemon=False)
        E.start()
        E.join()
    except (KeyboardInterrupt, SystemExit):
        pass