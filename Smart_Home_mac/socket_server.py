import socket
import json
import time


class Server:
    def __init__(self, ip, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (ip, port)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)
        print("等待连接...")
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"连接来自: {self.client_address}")

    def receive_string(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                decoded_data = data.decode("utf-8")
                print(f"收到字符串: {decoded_data}")
                return decoded_data

    def receive_mp3(self, file_path):
        print('开始接收mp3文件')
        with open(file_path, "wb") as file:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                if b'STOP' in data:
                    data = data.replace(b"STOP", b"")
                    file.write(data)
                    break
                file.write(data)
            print("MP3文件接收完毕")
        return file_path

    def receive_dict(self):
        while True:
            data = self.client_socket.recv(1024)
            if data:
                decoded_data = data.decode("utf-8")
                deserialized_dict = json.loads(decoded_data)
                print("收到字典数据:", deserialized_dict)
                return deserialized_dict

    def send_string(self, text):
        self.client_socket.sendall(text.encode("utf-8"))
        print("字符串已发送:"+text)

    def send_dict(self, dictionary):
        serialized_dict = json.dumps(dictionary)
        self.client_socket.sendall(serialized_dict.encode("utf-8"))
        print(f"字典已发送 , {dictionary}")

    def send_mp3(self, mp3_file_path):
        with open(mp3_file_path, "rb") as file:
            data = file.read()
            self.client_socket.sendall(data)
            self.client_socket.sendall(b'STOP')
            print("MP3文件已发送")

    def __del__(self):
        self.server_socket.close()
        self.client_socket.close()


if __name__ == '__main__':
    server = Server('0.0.0.0', 8001)
    time.sleep(5)
    server.send_mp3(r'response_test.mp3')
