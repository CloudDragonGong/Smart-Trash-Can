import socket
import json
import time


class Client:
    def __init__(self, ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip, port)
        self.timeout = 120
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client_socket.settimeout(self.timeout)
            self.client_socket.connect(self.server_address)
            print("连接成功")
        except socket.timeout:
            print("连接超时")
        except ConnectionRefusedError:
            print("连接被拒绝")
        except Exception as e:
            print(f"连接错误: {e}")

    def send_mp3(self, mp3_file_path):
        with open(mp3_file_path, "rb") as file:
            data = file.read()
            self.client_socket.sendall(data)
            self.client_socket.sendall(b"STOP")
            print("MP3文件已发送")

    def send_string(self, text):
        self.client_socket.sendall(text.encode("utf-8"))
        print("字符串已发送")

    def send_dict(self, dictionary):
        serialized_dict = json.dumps(dictionary)
        self.client_socket.sendall(serialized_dict.encode("utf-8"))
        print("字典已发送")

    def receive_string(self,length=1024):
        while True:
            data = self.client_socket.recv(length)
            if data:
                data = data.decode('utf-8')
                return data

    def receive_dict(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                data = data.decode('utf-8')
                dictionary = json.loads(data)
                return dictionary

    def receive_mp3(self, mp3_filename):
        with open(mp3_filename, "wb") as file:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                if b'STOP' in data:
                    data = data.replace(b"STOP", b"")
                    file.write(data)
                    break
                file.write(data)
        print("MP3文件已接收并保存")

    def __del__(self):
        self.client_socket.close()


if __name__ == '__main__':
    client = Client('10.13.4.45', 8001)
    time.sleep(1)
    client.receive_mp3('test_receive.mp3')
