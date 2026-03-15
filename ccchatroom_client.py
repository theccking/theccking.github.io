import os
import socket
import threading
import tkinter as tk
import tkinter.messagebox as box

BUFFER_SIZE = 1024

def handle_input():
    root.title('消息输入框')
    root.protocol("WM_DELETE_WINDOW", lambda: None)

    input_box = tk.Entry(root, width=50)
    input_box.grid(row=0, column=0)

    def send_message():
        sock.send(input_box.get().encode())
        input_box.delete(0, tk.END)

    button = tk.Button(root, text='发送', command=send_message)
    button.grid(row=0, column=1)

    quit_button = tk.Button(root, text='退出', command=lambda: sock.send(b'\x00'))
    quit_button.grid(row=0, column=3)

    # set keybind enter to send message
    root.bind('<Return>', lambda event: send_message())

    root.mainloop()

def handle_receive():
    while True:
        data = sock.recv(BUFFER_SIZE).decode()
        if data == '\x00':
            root.destroy()
            return
        if data.startswith('\x01'):
            box.showerror("Sanction", data[1:])            
        else:
            print(data)

"""
CCChatroom 已经停止维护。一切问题均不会再进行修复。
"""

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    sock.connect((int(input("请输入服务器IP: ")), 8000))
    sock.send(b'\033[36m'+input('请输入昵称: ').encode()+b'\033[0m')
    
    os.system('cls') # reset \033 usages
    root = tk.Tk()
    
    thread = threading.Thread(target=handle_receive, daemon=True)
    thread.start()
    
    handle_input()

