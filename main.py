import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading
import pickle
from pynput import mouse

pyautogui.PAUSE = 0

class MacroRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title('CBACRO')
        self.root.geometry('400x550')
        self.root.configure(bg='#2E3440')
        self.root.resizable(False, False)
        self.macro_data = []
        self.recording = False
        self.playing = False
        self.listener = None
        self.stop_event = threading.Event()

        self.create_ui()

    def create_ui(self):
        self.canvas = tk.Canvas(self.root, width=400, height=550, bg='#2E3440', highlightthickness=0)
        self.canvas.pack()

        self.title_label = tk.Label(self.root, text='CBACRO', font=('Arial', 20, 'bold'), bg='#2E3440', fg='white')
        self.title_label.place(relx=0.5, y=30, anchor='center')

        button_style = {
            'font': ('Arial', 12),
            'fg': 'white',
            'bg': '#4C566A',
            'relief': 'flat',
            'bd': 0,
            'width': 20,
            'height': 2,
            'cursor': 'hand2'
        }

        self.add_button('Start Recording', self.start_recording, button_style, 100)
        self.add_button('Stop Recording', self.stop_recording, button_style, 160)
        self.add_button('Play Macro', self.play_macro, button_style, 220)
        self.add_button('Save Macro', self.save_macro, button_style, 280)
        self.add_button('Load Macro', self.load_macro, button_style, 340)
        self.add_button('Instructions', self.show_instructions, button_style, 400)

        self.footer_label = tk.Label(self.root, text='Sebastian Lobato 2025', font=('Arial', 10), bg='#2E3440', fg='white')
        self.footer_label.place(relx=0.5, y=510, anchor='center')

    def add_button(self, text, command, style, y_pos):
        button = tk.Button(self.root, text=text, command=command, **style)
        button.place(x=100, y=y_pos)
        button.bind('<Enter>', lambda e, b=button: b.config(bg='#81A1C1'))
        button.bind('<Leave>', lambda e, b=button: b.config(bg='#4C566A'))

    def show_instructions(self):
        instructions = (
            "Instructions (English):\n"
            "1. Click 'Start Recording' to begin capturing your mouse movements and clicks.\n"
            "2. Click 'Stop Recording' to stop capturing.\n"
            "3. Click 'Play Macro' to replay your recorded actions.\n"
            "4. Use 'Save Macro' to store your actions to a file.\n"
            "5. Click 'Load Macro' to retrieve a previously saved macro.\n\n"
            "Instrucciones (Español):\n"
            "1. Haz clic en 'Start Recording' para empezar a grabar tus movimientos y clics del mouse.\n"
            "2. Haz clic en 'Stop Recording' para detener la grabación.\n"
            "3. Haz clic en 'Play Macro' para reproducir las acciones grabadas.\n"
            "4. Usa 'Save Macro' para guardar tus acciones en un archivo.\n"
            "5. Haz clic en 'Load Macro' para cargar una macro guardada anteriormente."
        )
        messagebox.showinfo("Instructions", instructions)

    def start_recording(self):
        self.macro_data = []
        self.recording = True
        self.stop_event.clear()
        self.start_time = time.time()

        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        threading.Thread(target=self.record).start()
        print("Recording started...")

    def on_click(self, x, y, button, pressed):
        current_time = time.time() - self.start_time
        action = 'click_down' if pressed else 'click_up'
        self.macro_data.append((action, x, y, current_time))

    def record(self):
        last_x, last_y = pyautogui.position()
        try:
            while self.recording and not self.stop_event.is_set():
                x, y = pyautogui.position()
                current_time = time.time() - self.start_time
                if (x, y) != (last_x, last_y):
                    self.macro_data.append(('move', x, y, current_time))
                    last_x, last_y = x, y
                time.sleep(0.01)
        except Exception as e:
            print(f"Error during recording: {e}")

    def stop_recording(self):
        self.recording = False
        self.stop_event.set()
        if self.listener:
            self.listener.stop()
        print("Recording stopped.")

    def play_macro(self):
        if not self.macro_data:
            print("No macro data to play.")
            return

        print("Playing macro...")
        self.playing = True
        start_time = time.time()

        try:
            for action, x, y, timestamp in self.macro_data:
                while time.time() - start_time < timestamp:
                    time.sleep(0.001)

                if action == 'move':
                    pyautogui.moveTo(x, y, duration=0)
                elif action == 'click_down':
                    pyautogui.mouseDown(x, y)
                elif action == 'click_up':
                    pyautogui.mouseUp(x, y)
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            print("Macro finished.")

    def save_macro(self):
        try:
            with open('macro.pkl', 'wb') as f:
                pickle.dump(self.macro_data, f)
            print("Macro saved.")
        except Exception as e:
            print(f"Error saving macro: {e}")

    def load_macro(self):
        try:
            with open('macro.pkl', 'rb') as f:
                self.macro_data = pickle.load(f)
            print("Macro loaded.")
        except FileNotFoundError:
            print("No macro found.")
        except Exception as e:
            print(f"Error loading macro: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = MacroRecorder(root)
    root.mainloop()