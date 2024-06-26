
# Remote Control Application

## Overview

This project provides a Python-based remote control application that allows users to remotely control another computer's mouse and keyboard and view its screen in real-time. It uses sockets for communication, OpenCV for screen display, and `pynput` for capturing and simulating mouse and keyboard events.

## Features

- **Remote Mouse and Keyboard Control:** Capture and replay mouse movements, clicks, scrolls, and keyboard presses/releases.
- **Real-time Screen Sharing:** Capture and display the screen in real-time.
- **Client-Server Architecture:** Connects a client to a server using a base64-encoded code representing the IP and port.

## Prerequisites

- Python 3.x
- Poetry for managing dependencies

You can install Poetry by following the instructions on the [Poetry installation page](https://python-poetry.org/docs/#installation).

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/remote-control.git
    cd remote-control
    ```

2. Install the dependencies using Poetry:

    ```sh
    poetry install
    ```

3. Activate the virtual environment:

    ```sh
    poetry shell
    ```

## Usage

### Running the Server

To start the server, run:

```sh
poetry run python remote_control.py -s
```

The server will display a code which can be used by the client to connect.

### Running the Client

To start the client, run:

```sh
poetry run python remote_control.py -c <code>
```

Replace `<code>` with the code provided by the server.

### Interactive Mode

If no arguments are provided, the script will prompt you to choose between running as a server or client:

```sh
poetry run python remote_control.py
```

Follow the prompts to run the application.

## Code Structure

### `ActionReplayer` Class

Handles the replaying of mouse and keyboard events.

- **Attributes:**
  - `screen_width`, `screen_height`: Screen dimensions.
  - `events`: List of events to replay.
  - `kController`: Keyboard controller.
  - `mController`: Mouse controller.

- **Methods:**
  - `get_key(key_str)`: Converts a key string to a `pynput` key object.
  - `replay(event)`: Replays a single event.

### `ActionRecorder` Class

Handles the recording of mouse and keyboard events.

- **Attributes:**
  - `screen_width`, `screen_height`: Screen dimensions.
  - `mController`: Mouse controller.
  - `mouse`: Mouse event handler.
  - `kController`: Keyboard controller.
  - `keyboard`: Keyboard event handler.

- **Methods:**
  - `on_move(x, y)`: Handles mouse move events.
  - `on_click(x, y, button, pressed)`: Handles mouse click events.
  - `on_scroll(x, y, dx, dy)`: Handles mouse scroll events.
  - `on_press(key)`: Handles key press events.
  - `on_release(key)`: Handles key release events.

### `ScreenReplayer` Class

Handles the display of screen data.

- **Methods:**
  - `display_image(image_data)`: Displays the received screen data.
  - `stop()`: Stops the screen display.

### `ScreenRecorder` Class

Captures and encodes the screen.

- **Static Methods:**
  - `get_screen_image()`: Captures the screen and returns the encoded image data.

### `Host` Class

Manages the server-side of the connection.

- **Attributes:**
  - `mouse`, `keyboard`, `screen`: Sockets for mouse, keyboard, and screen data.

- **Methods:**
  - `create_socket(port)`: Creates and binds a socket to a given port.
  - `connect_socket(server_socket)`: Listens for and accepts a connection.
  - `show_screen(screen_replayer)`: Continuously receives and displays screen data.
  - `handle_mouse(data)`: Handles mouse data received from the client.
  - `handle_keyboard(data)`: Handles keyboard data received from the client.

### `Client` Class

Manages the client-side of the connection.

- **Attributes:**
  - `mouse`, `keyboard`, `screen`: Sockets for mouse, keyboard, and screen data.

- **Methods:**
  - `create_socket(ip, port)`: Creates a socket and connects it to a given IP and port.
  - `screen_share()`: Continuously captures and sends screen data.
  - `handle_mouse()`: Continuously receives and replays mouse events.
  - `handle_keyboard()`: Continuously receives and replays keyboard events.

## License

This project is licensed under the MIT License.

## Acknowledgments

This project uses the following libraries and resources:
- OpenCV for image processing.
- pynput for capturing and controlling input devices.
- Pillow for image manipulation.
- pyautogui for screen size and resolution detection.

---

Feel free to customize this README file further based on your needs and any additional features you may add to the project.