
import base64
import threading
import argparse
import socket
import json
import cv2
import numpy as np
from PIL import ImageGrab
from pynput.mouse import Button, Listener as MouseListener, Controller as MouseController
from pynput.keyboard import Controller as KeyBoardController, Listener as KeyboardListener, Key
from time import sleep
import pyautogui
import sys


class ActionReplayer:
    screen_width, screen_height = pyautogui.size()

    def __init__(self):
        self.events = []
        self.kController = KeyBoardController()
        self.mController = MouseController()

    def get_key(self, key_str):
        try:
            if key_str.startswith('Key.'):
                key_name = key_str.split('.')[1]
                key = getattr(Key, key_name)
            else:
                key = key_str
            return key
        except AttributeError:
            pass

    def replay(self, event):
        print("Replaying event:", event)
        if event[0] == 'MOUSE_MOVE':
            self.mController.position = (
                event[1] * self.screen_width, event[2] * self.screen_height)
        elif event[0] == 'MOUSE_CLICK':
            self.mController.position = (
                event[1] * self.screen_width, event[2] * self.screen_height)
            button = Button.left if event[3] == 1 else Button.right if event[3] == 2 else Button.middle
            if event[4]:
                self.mController.press(button)
            else:
                self.mController.release(button)
        elif event[0] == 'MOUSE_SCROLL':
            self.mController.position = (
                event[1] * self.screen_width, event[2] * self.screen_height)
            self.mController.scroll(event[3], event[4])
        elif event[0] == 'KEY_DOWN':
            key = self.get_key(event[1])
            self.kController.press(key)
        elif event[0] == 'KEY_UP':
            key = self.get_key(event[1])
            self.kController.release(key)


class ActionRecorder:

    screen_width, screen_height = pyautogui.size()

    def __init__(self, mainloop, arg, keyboard, mouse):
        self.mController = MouseController()
        self.mouse = mouse
        mouse_listener = MouseListener(
            on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll
        )

        self.kController = KeyBoardController()
        self.keyboard = keyboard
        keyboard_listener = KeyboardListener(
            on_press=self.on_press, on_release=self.on_release
        )

        mouse_listener.start()
        keyboard_listener.start()
        mainloop(arg)
        keyboard_listener.stop()
        mouse_listener.stop()

    def on_move(self, x, y):
        self.mouse(
            ('MOUSE_MOVE', x / self.screen_width, y / self.screen_height))
        sleep(1/15)

    def on_click(self, x, y, button, pressed):
        self.mouse(('MOUSE_CLICK', x / self.screen_width, y / self.screen_height,
                    1 if button == Button.left else 2 if button == Button.right else 0, pressed))
        sleep(1/15)

    def on_scroll(self, x, y, dx, dy):
        self.mouse(('MOUSE_SCROLL',
                    x / self.screen_width, y / self.screen_height, dx, dy))
        sleep(1/15)

    def on_press(self, key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        self.keyboard(('KEY_DOWN', key_str))

    def on_release(self, key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = str(key)
        self.keyboard(('KEY_UP', key_str))


class ScreenReplayer:
    def display_image(self, image_data):
        # Decode the image
        frame = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        # Create a named window with the appropriate flags for fullscreen
        cv2.namedWindow('Screen Display', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            'Screen Display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.imshow('Screen Display', image)
        cv2.waitKey(1)  # Wait for a short duration to update display

    def stop(self):
        cv2.destroyAllWindows()





class ScreenRecorder:

    @staticmethod
    def get_screen_image():
        """
        Captures the screen and returns the image data to be sent through the socket.
        """
        # Capture the screen
        screen = ImageGrab.grab()
        screen_np = np.array(screen)
        screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # Encode the image
        _, frame = cv2.imencode('.jpg', screen_np)
        data = frame.tobytes()

        return data


class Host:

    def __init__(self):
        print("Initializing host...")
        server_socket, busy_port = self.create_socket(9990)

        ip = socket.gethostbyname(socket.gethostname())
        ip_parts = ip.split('.')
        ip_int = (int(ip_parts[0]) << 24) | (int(ip_parts[1]) << 16) | (
            int(ip_parts[2]) << 8) | int(ip_parts[3])
        port_int = busy_port
        ip_bytes = ip_int.to_bytes(4, 'big')
        port_bytes = port_int.to_bytes(2, 'big')
        code = base64.b64encode(ip_bytes + port_bytes).decode('utf-8')

        print(f"Listening for client at: {code}")
        client_socket = self.connect_socket(server_socket)

        mouse_socket, mouse = self.create_socket(busy_port + 1)
        keyboard_socket, keyboard = self.create_socket(mouse + 1)
        screen_socket, screen = self.create_socket(keyboard + 1)

        client_socket.send(json.dumps(
            {'mouse': mouse, 'keyboard': keyboard, 'screen': screen}).encode('utf-8'))

        self.mouse = self.connect_socket(mouse_socket)
        self.keyboard = self.connect_socket(keyboard_socket)
        self.screen = self.connect_socket(screen_socket)

        client_socket.close()

        screen_replayer = ScreenReplayer()

        try:
            ActionRecorder(self.show_screen, screen_replayer,
                           self.handle_keyboard, self.handle_mouse)
        except:
            screen_replayer.stop()
            self.stop()

    def stop(self):
        self.mouse.close()
        self.keyboard.close()
        self.screen.close()

    def create_socket(self, port):
        ip = socket.gethostbyname(socket.gethostname())
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                server_socket.bind((ip, port))
                print("Server socket bound to port:", port)
                break
            except:
                print(f"Port {port} in use, trying next one.")
                port += 1
        return server_socket, port

    def connect_socket(self, server_socket):
        server_socket.listen(1)
        client_socket, _ = server_socket.accept()
        server_socket.close()
        print("Client connected.")
        return client_socket

    def show_screen(self, screen_replayer):
        while True:
            try:
                data_size = int.from_bytes(
                    self.screen.recv(4), byteorder='big')
                data = bytearray()
                while len(data) < data_size:
                    packet = self.screen.recv(4096)
                    if not packet:
                        break
                    data.extend(packet)
                screen_replayer.display_image(data)
                self.screen.send(b'1')
            except Exception as e:
                print(e)
                self.stop()
                break

    def handle_mouse(self, data):
        try:
            data = json.dumps(data).encode('utf-8')
            self.mouse.sendall(len(data).to_bytes(4, byteorder='big'))
            self.mouse.recv(1)
            self.mouse.sendall(data)
            self.mouse.recv(1)
        except Exception as e:
            print(e)
            self.stop()

    def handle_keyboard(self, data):
        try:
            data = json.dumps(data).encode('utf-8')
            self.keyboard.sendall(len(data).to_bytes(4, byteorder='big'))
            self.keyboard.recv(1)
            self.keyboard.sendall(data)
            self.keyboard.recv(1)
        except Exception as e:
            print(e)
            self.stop()


class Client:

    def __init__(self, code):
        print("Initializing client...")
        decoded_bytes = base64.b64decode(code)
        ip_int = int.from_bytes(decoded_bytes[:4], 'big')
        port_int = int.from_bytes(decoded_bytes[4:], 'big')
        ip = "{}.{}.{}.{}".format(
            (ip_int >> 24) & 0xFF, (ip_int >> 16) & 0xFF, (ip_int >> 8) & 0xFF, ip_int & 0xFF)
        client_socket = self.create_socket(ip, port_int)
        info = json.loads(client_socket.recv(1024).decode('utf-8'))
        print("Received info:", info)

        self.mouse = self.create_socket(ip, info['mouse'])
        self.keyboard = self.create_socket(ip, info['keyboard'])
        self.screen = self.create_socket(ip, info['screen'])

        client_socket.close()

        try:
            threading.Thread(target=self.handle_keyboard).start()
            threading.Thread(target=self.handle_mouse).start()
            self.screen_share()
        except:
            self.stop()

    def stop(self):
        self.mouse.close()
        self.keyboard.close()
        self.screen.close()

    def create_socket(self, ip, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        print(f"Connected to server at {ip}:{port}")
        return client_socket

    def screen_share(self):
        while True:
            try:
                data = ScreenRecorder.get_screen_image()
                self.screen.sendall(len(data).to_bytes(4, byteorder='big'))
                self.screen.sendall(data)
                self.screen.recv(1)
            except Exception as e:
                print(e)
                self.stop()
                break

    def handle_mouse(self):
        replayer = ActionReplayer()
        while True:
            try:
                data_size = int.from_bytes(self.mouse.recv(4), byteorder='big')
                data = bytearray()
                self.mouse.send(b'1')
                while len(data) < data_size:
                    packet = self.mouse.recv(4096)
                    if not packet:
                        break
                    data.extend(packet)
                replayer.replay(json.loads(data.decode('utf-8')))
                self.mouse.send(b'1')
            except Exception as e:
                print(e)
                self.stop()
                break

    def handle_keyboard(self):
        replayer = ActionReplayer()
        while True:
            try:
                data_size = int.from_bytes(
                    self.keyboard.recv(4), byteorder='big')
                data = bytearray()
                self.keyboard.send(b'1')
                while len(data) < data_size:
                    packet = self.keyboard.recv(4096)
                    if not packet:
                        break
                    data.extend(packet)
                replayer.replay(json.loads(data.decode('utf-8')))
                self.keyboard.send(b'1')
            except Exception as e:
                print(e)
                self.stop()
                break


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-s', '--server', action='store_true', help='Connect as server')
    group.add_argument('-c', '--client', action='store_true', help='Connect as client')
    parser.add_argument('code', type=str, nargs='?',
                        help='Code (required if running as client)')

    args = parser.parse_args()

    # Check if no arguments were provided
    if not any(vars(args).values()):
        option = input("Run as (s)erver or (c)lient? ").strip().lower()
        if option == 's':
            args.server = True
        elif option == 'c':
            args.client = True
            args.code = input("Enter the code: ").strip()
        else:
            parser.error(
                "Invalid option, please choose 's' for server or 'c' for client.")

    if args.client and not args.code:
        parser.error("the following arguments are required: code")

    if args.client:
        Client(args.code)
    if args.server:
        Host()

    if len(sys.argv) == 2:
        code = sys.argv[1]
        Client(code)
