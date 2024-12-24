import tkinter as tk
from slider_puzzle.ui.puzzle_game import PuzzleGame


def run_ui():
    root = tk.Tk()
    PuzzleGame(root)
    root.mainloop()


if __name__ == "__main__":
    run_ui()
