import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import bcrypt

responses = {"name": "", "location": "", "operation": "", "feeling": ""}

class UsernameScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Enter Username")
        self.root.geometry("480x320")

        tk.Label(root, text="Username", font=("Arial", 20)).pack(pady=5)
        self.entry_username = tk.Entry(root, font=("Arial", 18))
        self.entry_username.pack(pady=5, ipadx=10, ipady=5)
        self.entry_username.focus_set()

        self.build_compact_keyboard(root, self.entry_username)

        tk.Button(root, text="Next", command=self.go_to_password, font=("Arial", 14), height=2, width=10).pack(pady=5)

    def build_compact_keyboard(self, parent, entry):
        keys = [
            ['1','2','3','4','5','6','7','8','9','0'],
            ['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l'],
            ['z','x','c','v','b','n','m','Space','Back','Clear']
        ]
        kb_frame = tk.Frame(parent)
        kb_frame.pack(pady=5)

        for row in keys:
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for key in row:
                action = lambda x=key: self.press_key(entry, x)
                b = tk.Button(row_frame, text=key, width=4, height=1, font=("Arial", 10), command=action)
                b.pack(side=tk.LEFT, padx=1, pady=1)

    def press_key(self, entry, key):
        if key == 'Back':
            current = entry.get()
            entry.delete(len(current)-1, tk.END)
        elif key == 'Clear':
            entry.delete(0, tk.END)
        elif key == 'Space':
            entry.insert(tk.END, ' ')
        else:
            entry.insert(tk.END, key)

    def go_to_password(self):
        username = self.entry_username.get().strip()
        if username:
            self.root.destroy()
            root_pw = tk.Tk()
            PasswordScreen(root_pw, username)
            root_pw.mainloop()
        else:
            messagebox.showerror("Input Error", "Please enter a username.")


class PasswordScreen:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title("Enter Password")
        self.root.geometry("480x320")

        tk.Label(root, text=f"User: {username}", font=("Arial", 14)).pack(pady=3)
        tk.Label(root, text="Password", font=("Arial", 20)).pack(pady=5)

        self.entry_password = tk.Entry(root, show="*", font=("Arial", 18))
        self.entry_password.pack(pady=5, ipadx=10, ipady=5)
        self.entry_password.focus_set()

        self.build_compact_keyboard(root, self.entry_password)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Back", command=self.back_to_username, font=("Arial", 14), height=2, width=8).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Login", command=self.verify_login, font=("Arial", 14), height=2, width=8).pack(side=tk.LEFT, padx=5)

    def build_compact_keyboard(self, parent, entry):
        keys = [
            ['1','2','3','4','5','6','7','8','9','0'],
            ['q','w','e','r','t','y','u','i','o','p'],
            ['a','s','d','f','g','h','j','k','l'],
            ['z','x','c','v','b','n','m','Space','Back','Clear']
        ]
        kb_frame = tk.Frame(parent)
        kb_frame.pack(pady=5)

        for row in keys:
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for key in row:
                action = lambda x=key: self.press_key(entry, x)
                b = tk.Button(row_frame, text=key, width=4, height=1, font=("Arial", 10), command=action)
                b.pack(side=tk.LEFT, padx=1, pady=1)

    def press_key(self, entry, key):
        if key == 'Back':
            current = entry.get()
            entry.delete(len(current)-1, tk.END)
        elif key == 'Clear':
            entry.delete(0, tk.END)
        elif key == 'Space':
            entry.insert(tk.END, ' ')
        else:
            entry.insert(tk.END, key)

    def back_to_username(self):
        self.root.destroy()
        root_username = tk.Tk()
        UsernameScreen(root_username)
        root_username.mainloop()

    def verify_login(self):
        password = self.entry_password.get()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,))
        result = cursor.fetchone()
        conn.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            self.root.destroy()
            launch_barcode_scanner()
        else:
            messagebox.showerror("Login Failed", "Incorrect password.")


class BarcodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Scanner")
        self.root.geometry("480x320")

        tk.Label(root, text="Scan or Enter Barcode:", font=("Arial", 16)).pack(pady=5)

        self.entry = tk.Entry(root, font=("Arial", 16))
        self.entry.pack(pady=5, ipadx=10, ipady=5)
        self.entry.bind("<Return>", self.scan_barcode)
        self.entry.focus()

        self.listbox = tk.Listbox(root, font=("Arial", 14), height=6)
        self.listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Clear List", command=self.clear_list, font=("Arial", 14), height=1, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save & Continue", command=self.save_and_continue, font=("Arial", 14), height=1, width=14).pack(side=tk.LEFT, padx=5)

    def scan_barcode(self, event=None):
        barcode = self.entry.get().strip()
        if barcode:
            self.listbox.insert(tk.END, barcode)
            self.entry.delete(0, tk.END)
            self.entry.focus()

    def clear_list(self):
        self.listbox.delete(0, tk.END)

    def save_and_continue(self):
        if self.listbox.size() == 0:
            messagebox.showinfo("Info", "No barcodes to save.")
            return
        with open("scanned_barcodes.txt", "a") as f:
            for i in range(self.listbox.size()):
                f.write(self.listbox.get(i) + "\n")
        self.root.destroy()
        launch_survey()


def launch_barcode_scanner():
    root = tk.Tk()
    BarcodeScannerApp(root)
    root.mainloop()


def launch_survey():
    import sqlite3

    conn = sqlite3.connect('survey_responses.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, location TEXT, operation TEXT, feeling TEXT)''')
    conn.commit()

    root = tk.Tk()
    root.title("Package Survey")
    root.geometry("480x320")

    frame = tk.Frame(root)
    frame.pack(expand=True, fill='both')

    def clear_frame():
        for widget in frame.winfo_children():
            widget.destroy()

    def start_questionnaire():
        clear_frame()
        tk.Label(frame, text="Who are you?", font=("Arial", 12)).pack(pady=5)
        name_entry = tk.Entry(frame, font=("Arial", 12), width=20)
        name_entry.pack(pady=5)

        keyboard_frame = tk.Frame(frame)
        keyboard_frame.pack(pady=5)

        def insert_text(char):
            name_entry.insert(tk.END, char)

        def clear_text():
            name_entry.delete(0, tk.END)

        keys = [['Q','W','E','R','T','Y','U','I','O','P'], ['A','S','D','F','G','H','J','K','L'], ['Z','X','C','V','B','N','M'], ['Space', 'Clear']]

        for row in keys:
            row_frame = tk.Frame(keyboard_frame)
            row_frame.pack()
            for key in row:
                if key == 'Space':
                    btn = tk.Button(row_frame, text='Space', width=5, height=1, command=lambda k=' ': insert_text(k))
                elif key == 'Clear':
                    btn = tk.Button(row_frame, text='Clear', width=5, height=1, command=clear_text)
                else:
                    btn = tk.Button(row_frame, text=key, width=3, height=1, command=lambda k=key: insert_text(k))
                btn.pack(side='left', padx=1, pady=1)

        def submit_name():
            responses["name"] = name_entry.get()
            ask_location()

        tk.Button(frame, text="Next", font=("Arial", 12), command=submit_name).pack(pady=10)

    def ask_location():
        clear_frame()
        tk.Label(frame, text="Where are you?", font=("Arial", 12)).pack(pady=5)
        location_var = tk.StringVar()
        location_dropdown = ttk.Combobox(frame, textvariable=location_var, font=("Arial", 10), state="readonly", width=18)
        location_dropdown['values'] = ["Warehouse A", "Warehouse B", "Dock 1", "Dock 2", "Office", "Transit"]
        location_dropdown.pack(pady=5)

        def submit_location():
            responses["location"] = location_var.get()
            ask_operation()

        tk.Button(frame, text="Next", font=("Arial", 12), command=submit_location).pack(pady=10)

    def ask_operation():
        clear_frame()
        tk.Label(frame, text="What operation?", font=("Arial", 12)).pack(pady=5)
        operation_var = tk.StringVar()
        operation_dropdown = ttk.Combobox(frame, textvariable=operation_var, font=("Arial", 10), state="readonly", width=18)
        operation_dropdown['values'] = ["Find", "Receive", "Ship", "Move"]
        operation_dropdown.pack(pady=5)

        def submit_operation():
            responses["operation"] = operation_var.get()
            ask_feeling()

        tk.Button(frame, text="Next", font=("Arial", 12), command=submit_operation).pack(pady=10)

    def ask_feeling():
        clear_frame()
        tk.Label(frame, text="How do you feel?", font=("Arial", 12)).pack(pady=5)
        feeling_var = tk.StringVar()
        feeling_dropdown = ttk.Combobox(frame, textvariable=feeling_var, font=("Arial", 10), state="readonly", width=18)
        feeling_dropdown['values'] = ["Happy", "Worried", "Hurt", "Sad", "Angry", "Confused", "Relief", "Satisfaction", "Surprise", "Nostalgic", "Interest", "Horror"]
        feeling_dropdown.pack(pady=5)

        def submit_feeling():
            responses["feeling"] = feeling_var.get()
            cursor.execute('''INSERT INTO responses (name, location, operation, feeling) VALUES (?, ?, ?, ?)''', (responses["name"], responses["location"], responses["operation"], responses["feeling"]))
            conn.commit()
            clear_frame()
            tk.Label(frame, text="Responses saved! Thank you!", font=("Arial", 12), fg="green").pack(pady=20)
            tk.Button(frame, text="Return to Login", font=("Arial", 12), command=lambda: [root.destroy(), main()]).pack(pady=10)

        tk.Button(frame, text="Submit", font=("Arial", 12), command=submit_feeling).pack(pady=10)

    start_questionnaire()
    root.mainloop()
    conn.close()


def create_users_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)""")
    conn.commit()
    conn.close()


def main():
    create_users_db()
    root = tk.Tk()
    UsernameScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
