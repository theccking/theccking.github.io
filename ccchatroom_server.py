import socket
import threading
import inspect
import ctypes
import time
import re

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 8000))

SUPER = []
BANNED = []
pb = ["宓", "yan", "ymy", "大王", "同性恋", "gay", "99", "fuck", "屎", "狗", "宇", "熊", "晶", "常", "cc", "爸", "妈", "宝", "forever", "wangyu", "wy", "jb", "菜", "cai", "baba"]
pbre = [r"[0-9a-zA-Z._]+$"]

def strhash(s: str) -> int:
    h = 0
    for i in range(len(s)):
        h = (h * 31 + ord(s[i])) & 0xFFFFFF
    return h

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        return
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread: threading.Thread):
    _async_raise(thread.ident, SystemExit)

class Client:
    def __init__(self, conn: socket.socket):
        self.conn = conn
        self.name = "\033[32m选择昵称中...\033[0m"
        self.nick = None
        self.thread = threading.Thread(target=self.handle)
        self.thread.start()

    def handle(self):
        while True:
            try:    
                name = self.recv(30).decode().strip()

                raw = name.replace("_","").replace("-","").replace("=","").replace("—","").replace(" ","")

                for i in pbre:
                    if re.match(i, name):
                        name = "爸"
                
                for i in pb:
                    if i in raw.lower():
                        raw = name.lower().replace(i, "爸")
                        name = raw
                
                for client in clients:
                    if client.name == name:
                        self.send('名称已被占用'.encode())
                        self.close()
                        return
                    if name in BANNED:
                        self.send('你已被 CCKick'.encode())
                        self.close()
                        return
                else:
                    break
            except UnicodeDecodeError:
                self.send('名称不能包含特殊字符'.encode())
                return
        
        if '#' in name:
            passcode, _, nick = name.partition('#')
            passcode = hex(strhash(passcode))[2:]
            name = f'{passcode} #{nick}'
        else: 
            passcode = None
            nick = name
        
        self.name = name
        self.nick = nick
        self.send('欢迎加入聊天室！\n'.encode())
        self.send('Lougu Platform 26w01a - 修复已知问题\n'.encode())
        broadcast(f'\033[32m* {nick} 已连接\033[0m'.encode(), True)

        while True:
            try:            
                if name in BANNED:
                    self.send('\033[31m* 你已被 CCKick\033[0m'.encode())
                    self.close()
                    return
                
                msg = self.recv()
                if msg == b'\x00':
                    self.close()
                    break

                if msg.startswith(b'/ban '):
                    _, _, banname = msg.partition(b' ')
                    if banname in BANNED:
                        self.send(f'\033[33m* {banname.decode()} 已经被 CCKick\033[0m'.encode())
                    elif banname in SUPER:
                        self.send(f'\033[33m* 舰长 {banname.decode()} 无法被 CCKick\033[0m'.encode())
                    else:
                        try:
                            banname = banname.decode()
                            BANNED.append(banname)
                            for client in clients:
                                if client.name == banname:
                                    broadcast(f'\033[33m* {banname} 已被 {nick} CCKick\033[0m'.encode(), True)
                                    client.close()
                                    self.send(f'\033[33m* 执行 CCKick {banname} 成功 \033[0m'.encode())
                                    break
                            else:
                                self.send(f'\033[33m* 名为 {banname} 的用户不在线\033[0m'.encode())
                        except UnicodeDecodeError:
                            self.send('指令使用格式错误，请查询使用文档'.encode())
                            
                elif msg == b'/list':
                    self.send(f"\033[33m* === 当前有 {len(clients)} 名用户在线 ===\033[0m".encode())
                    for client in clients:
                        self.send(f"\033[33m* {client.name}\033[0m\n".encode())

#                elif msg.startswith(b'/re '):
#                    _, _, bans = msg.partition(b' ')
#                    bans = bans.decode()
#                    pbre.append(bans)

                elif msg.startswith(b'/san '):
                    _, _, text = msg.partition(b' ')
                    broadcast(f"\x01{text.decode()}".encode())

                elif msg.startswith(b"hmmlr/sc "):
                    _, _, scname = msg.partition(b' ')
                    if scname in SUPER:
                        self.send(f'\033[33m* desc.sc.already\033[0m'.encode())
                    else:
                        try:
                            scname = scname.decode()
                            for client in clients:
                                if client.name == scname:
                                    broadcast(f'\033[33m* {scname} 已被 {nick} CCKick\033[0m'.encode(), True)
                                    SUPER.append(scname.encode())
                                    break
                            else:
                                self.send(f'\033[33m* 名为 {scname} 的用户不在线\033[0m'.encode())

                        except UnicodeDecodeError:
                            self.send('指令使用格式错误，请查询使用文档'.encode())
                                    
                elif passcode is not None:
                    broadcast(f'{passcode} \033[35m{nick}\033[0m: {msg.decode()}'.encode())
                else:
                    if name in SUPER:
                        broadcast(f'\033[41m[SC]\033[0m \033[35m{self.name}\033[0m: {msg.decode()}'.encode())
                    else:
                        broadcast(f'\033[35m{self.name}\033[0m: {msg.decode()}'.encode())
            except UnicodeDecodeError:
                self.send('消息不能包含特殊字符'.encode())
            time.sleep(1)

    def send(self, msg: bytes):
        try:
            self.conn.send(msg)
        except (ConnectionResetError, OSError):
            self.close(False)
    
    def close(self, halt=True):
        
        if halt:
            self.send(b'\x00')
        self.conn.close()
        
        if self in clients:
            clients.remove(self)
        
        if self.nick is not None:
            broadcast(f'\033[31m* {self.nick} 已退出\033[0m'.encode(), True)
        
        stop_thread(self.thread)

    def recv(self, buffer: int = 1024) -> bytes:
        try:
            return self.conn.recv(buffer)
        except (ConnectionResetError, OSError):
            self.close()
            return b''

def broadcast(msg, pr=False):
    for client in clients:
        client.send(msg)
    if pr:
        print(msg.decode())

clients: list[Client] = []

"""
CCChatroom 已经停止维护。一切问题均不会再进行修复。
"""

if __name__ == '__main__':
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        client = Client(conn)
        clients.append(client)
        

