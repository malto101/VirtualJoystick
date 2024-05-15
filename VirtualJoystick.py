# Author: Dhruv Menon
# Use case: This Python script creates a GUI application for a joystick controller. The GUI allows users to select a serial port, move a virtual joystick with their mouse, start and stop transmitting the joystick position (normalized to a range of -128 to 128) to the selected serial port.

import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports


class JoystickApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Joystick Controller")

        # Variables to store X and Y values of the joystick
        self.x_value = tk.StringVar()
        self.y_value = tk.StringVar()

        # Flag to indicate if transmitting is in progress
        self.transmitting = False

        # Initialize the GUI
        self.create_widgets()
        self.create_serial_connection()

    def create_widgets(self):
        # Create the canvas for the joystick
        self.canvas = tk.Canvas(self.root, bg="white")
        # Use sticky to make the canvas expand with the window
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Label and combobox for selecting serial port
        self.serial_label = tk.Label(self.root, text="Select Serial Port:")
        self.serial_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.serial_combobox = ttk.Combobox(self.root, width=15)
        self.serial_combobox.grid(
            row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Populate serial ports
        self.populate_serial_ports()

        # Start and stop transmitting buttons
        self.start_button = ttk.Button(
            self.root, text="Start Transmitting", command=self.start_transmitting)
        self.start_button.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.stop_button = ttk.Button(
            self.root, text="Stop Transmitting", command=self.stop_transmitting)
        self.stop_button.grid(row=1, column=3, padx=10, pady=5, sticky=tk.W)

        # Update joystick position continuously
        self.root.after(100, self.update_joystick)

        # Bind mouse events
        self.canvas.bind("<B1-Motion>", self.move_joystick)
        self.canvas.bind("<ButtonRelease-1>", self.release_joystick)

        # Bind canvas to window resize event
        self.root.bind("<Configure>", self.on_window_resize)

        # Initialize joystick position and size
        self.joystick_pos = (100, 100)
        self.joystick_size = 20

        # Draw initial joystick
        self.draw_joystick()

    def create_serial_connection(self):
        # Initialize serial port connection
        self.serial_port = serial.Serial()

    def populate_serial_ports(self):
        # Populate the combobox with available serial ports
        ports = self.get_serial_ports()
        if ports:
            self.serial_combobox['values'] = ports
            self.serial_combobox.current(0)
        else:
            self.serial_combobox['values'] = ['No serial ports available']

    def get_serial_ports(self):
        # Get a list of available serial ports
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports

    def update_joystick(self):
        # Update the X and Y values displayed on the GUI
        x, y = self.joystick_pos
        x_normalized = int((x - self.canvas.winfo_width() / 2)
                           * 256 / self.canvas.winfo_width())
        y_normalized = int((y - self.canvas.winfo_height() / 2)
                           * 256 / self.canvas.winfo_height())
        self.x_value.set(f"X: {x_normalized}")
        self.y_value.set(f"Y: {y_normalized}")

        # Call this method again after 100 milliseconds for continuous update
        self.root.after(100, self.update_joystick)

    def move_joystick(self, event):
        # Move the joystick to the position of the mouse cursor
        self.joystick_pos = (event.x, event.y)
        self.draw_joystick()

    def release_joystick(self, event):
        # Reset the joystick to the center when mouse button is released
        self.joystick_pos = (self.canvas.winfo_width() / 2,
                             self.canvas.winfo_height() / 2)
        self.draw_joystick()

    def start_transmitting(self):
        # Start transmitting x and y coordinates to the selected serial port
        serial_port = self.serial_combobox.get()
        if serial_port and not self.transmitting:
            self.transmitting = True
            self.serial_port.port = serial_port
            self.serial_port.baudrate = 9600
            self.serial_port.open()

            def transmit_coordinates():
                x, y = self.joystick_pos
                x_normalized = int(
                    (x - self.canvas.winfo_width() / 2) * 256 / self.canvas.winfo_width())
                y_normalized = int(
                    (y - self.canvas.winfo_height() / 2) * 256 / self.canvas.winfo_height())
                self.serial_port.write(
                    f"{x_normalized},{y_normalized}\n".encode())
                if self.transmitting:
                    self.root.after(100, transmit_coordinates)
                print(f"{x_normalized},{y_normalized}\n".encode())

            transmit_coordinates()

    def stop_transmitting(self):
        # Stop transmitting joystick coordinates
        self.transmitting = False

    def draw_joystick(self):
        # Draw the joystick at its current position
        self.canvas.delete("joystick")
        x, y = self.joystick_pos
        size = self.joystick_size
        self.canvas.create_oval(
            x - size, y - size, x + size, y + size, fill="red", tags="joystick")

    def on_window_resize(self, event):
        # Update joystick position and redraw it when window is resized
        self.joystick_pos = (self.canvas.winfo_width() / 2,
                             self.canvas.winfo_height() / 2)
        self.draw_joystick()


if __name__ == "__main__":
    root = tk.Tk()
    app = JoystickApp(root)
    root.mainloop()
