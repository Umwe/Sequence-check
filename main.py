from sequence_checker_gui import SequenceCheckerGUI  # Assuming the GUI class is saved in sequence_checker_gui.py
import tkinter as tk

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.gui = SequenceCheckerGUI(self.root)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()