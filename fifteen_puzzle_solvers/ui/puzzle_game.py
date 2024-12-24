import tkinter as tk
import threading
from tkinter import font

from fifteen_puzzle_solvers.services.algorithms import AStar
from fifteen_puzzle_solvers.services.solver import PuzzleSolver
from fifteen_puzzle_solvers.services.puzzle.shuffle import PuzzleShuffleService
from fifteen_puzzle_solvers.services.puzzle.constants import (
    HEURISTIC_OPTIONS, HEURISTIC_TOTAL, ALGORITHM_OPTIONS, ASTAR)


class PuzzleGame:
    def __init__(self, master):
        self.master = master
        self.master.title('Trò chơi 15-puzzle')
        self.master.geometry('1100x600')
        self.master.configure(bg='#FFFFFF')

        self.puzzle_size = 4
        self.puzzle = PuzzleShuffleService.shuffle_puzzle(self.puzzle_size)
        self.solution_steps = []
        self.current_step = 0
        self.num_expanded_nodes = 0
        self.solver = None

        self.tiles = []
        self.selected_algorithm = tk.StringVar(self.master, ASTAR)
        self.selected_heuristic = tk.StringVar(self.master, HEURISTIC_TOTAL)
        self.selected_size = tk.IntVar(self.master, self.puzzle_size)
        self.create_ui()

    def create_ui(self):
        # Create a main frame to hold everything
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Frame: Title, Size Selection, Shuffle Button, and Puzzle (Game area)
        left_frame = tk.Frame(main_frame, bg='#FFFFFF')
        left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        # Frame to contain Title, Size Selection, and Shuffle Button horizontally
        top_frame = tk.Frame(left_frame, bg='#FFFFFF')
        top_frame.pack(side=tk.TOP, pady=20)

        # Size Selection
        self.size_label = tk.Label(top_frame, text='Chọn kích thước:', font=('Arial', 14), fg='#333333', bg='#FFFFFF')
        self.size_label.pack(side=tk.LEFT, padx=10)

        self.size_menu = tk.OptionMenu(top_frame, self.selected_size, *range(3, 7), command=self.on_size_change)
        self.size_menu.config(font=('Arial', 12), relief='flat', width=10)
        self.size_menu.pack(side=tk.LEFT, padx=10)

        # Shuffle Button
        self.shuffle_button = tk.Button(top_frame, text='Trộn hình', command=self.shuffle_puzzle, bg='#28A745',
                                        fg='white', font=('Arial', 12), relief='solid', bd=2, width=15)
        self.shuffle_button.pack(side=tk.LEFT, padx=10)

        # Puzzle Frame (below the top_frame)
        self.puzzle_frame = tk.Frame(left_frame, bg='#FFFFFF')
        self.puzzle_frame.pack(pady=20)

        # Right Frame: Controls and Status
        right_frame = tk.Frame(main_frame, bg='#FFFFFF')
        right_frame.pack(side=tk.LEFT, padx=20, pady=20)

        # Controls Frame (Algorithm, Heuristic, Solve/Stop buttons)
        self.controls_frame = tk.Frame(right_frame, bg='#FFFFFF')
        self.controls_frame.pack(pady=10)

        # Algorithm Selection
        self.algorithm_label = tk.Label(self.controls_frame, text='Chọn thuật toán:', font=('Arial', 14), fg='#333333',
                                        bg='#FFFFFF')
        self.algorithm_label.grid(row=0, column=0, pady=5, padx=5, sticky='e')

        self.algorithm_menu = tk.OptionMenu(self.controls_frame, self.selected_algorithm, 'A*',
                                            command=self.on_algorithm_change)
        self.algorithm_menu.config(font=('Arial', 12), relief='flat', width=12)
        self.algorithm_menu.grid(row=0, column=1, pady=5, padx=5)

        # Heuristic Selection
        self.heuristic_label = tk.Label(self.controls_frame, text='Chọn Heuristic:', font=('Arial', 14), fg='#333333',
                                        bg='#FFFFFF')
        self.heuristic_label.grid(row=1, column=0, pady=5, padx=5, sticky='e')

        self.heuristic_menu = tk.OptionMenu(self.controls_frame, self.selected_heuristic, 'manhattan_distance', 'total',
                                            'misplaced')
        self.heuristic_menu.config(font=('Arial', 12), relief='flat', width=12)
        self.heuristic_menu.grid(row=1, column=1, pady=5, padx=5)

        # Solve Button
        self.solve_button = tk.Button(self.controls_frame, text='Giải quyết', command=self.start_solve_puzzle, bg='#FFC107',
                                      fg='black', font=('Arial', 12), relief='solid', bd=2, width=15)
        self.solve_button.grid(row=2, column=0, pady=10, padx=5, columnspan=2)

        # Stop Button
        self.stop_button = tk.Button(self.controls_frame, text='Dừng', command=self.stop_solve_puzzle, bg='#DC3545',
                                     fg='white', font=('Arial', 12), relief='solid', bd=2, width=15)
        self.stop_button.grid(row=3, column=0, pady=5, padx=5, columnspan=2)
        self.stop_button.grid_remove()  # Hide the stop button initially

        # Auto-Run Button (added button)
        self.auto_run_button = tk.Button(self.controls_frame, text='Chạy tự động', command=self.auto_run, bg='#17A2B8',
                                         fg='white', font=('Arial', 12), relief='solid', bd=2, width=15)
        self.auto_run_button.grid(row=4, column=0, pady=10, padx=5, columnspan=2)

        # Control buttons (Previous / Next Step)
        self.button_frame = tk.Frame(right_frame, bg='#FFFFFF')
        self.button_frame.pack(pady=5)

        self.previous_button = tk.Button(self.button_frame, text='Bước trước đó', command=self.previous_step,
                                         bg='#007BFF', fg='white', font=('Arial', 12), relief='solid', width=15)
        self.previous_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(self.button_frame, text='Bước tiếp theo', command=self.next_step, bg='#007BFF',
                                     fg='white', font=('Arial', 12), relief='solid', width=15)
        self.next_button.grid(row=0, column=1, padx=10)

        self.previous_button.grid_remove()
        self.next_button.grid_remove()

        # Status Label
        self.status_label = tk.Label(right_frame, text='Moves: 0\nExpanded Nodes: 0\nSolution Steps: 0',
                                     font=('Arial', 14), fg='#333333', bg='#FFFFFF')
        self.status_label.pack(pady=20)

        # Create puzzle tiles
        self.create_tiles()

    def on_algorithm_change(self, value):
        if value == 'A*':
            self.heuristic_label.grid()
            self.heuristic_menu.grid()
        else:
            self.heuristic_label.grid_remove()
            self.heuristic_menu.grid_remove()

    def on_size_change(self, value):
        self.puzzle_size = value
        self.puzzle = PuzzleShuffleService.shuffle_puzzle(self.puzzle_size)
        self.create_tiles()
        self.update_tiles()

    def create_tile_button(self, i, j):
        return tk.Button(self.puzzle_frame, text=str(self.puzzle.position[i][j]), font=('Helvetica', 18), width=4,
                         height=2, bg='#007BFF', fg='white', command=lambda: self.move_tile(i, j))

    def create_tiles(self):
        for widget in self.puzzle_frame.winfo_children():
            widget.destroy()
        self.tiles = []
        for i in range(self.puzzle_size):
            row = []
            for j in range(self.puzzle_size):
                tile = self.create_tile_button(i, j)
                tile.grid(row=i, column=j, padx=5, pady=5)
                row.append(tile)
            self.tiles.append(row)

    def update_tiles(self):
        for i in range(self.puzzle_size):
            for j in range(self.puzzle_size):
                text = str(self.puzzle.position[i][j])
                if text == '0':
                    text = ''
                self.tiles[i][j].config(text=text)

    def update_status_label(self):
        text = (f'Moves: {self.current_step}\n'
                f'Expanded Nodes: {self.num_expanded_nodes}\n'
                f'Solution Steps: {len(self.solution_steps)}')
        self.status_label.config(text=text)

    def move_tile(self, i, j):
        empty_i, empty_j = self.puzzle.find_empty_tile()
        if (abs(empty_i - i) == 1 and empty_j == j) or (abs(empty_j - j) == 1 and empty_i == i):
            self.puzzle.position = self.puzzle.swap_tiles(i, j, empty_i, empty_j)
            self.update_tiles()
            self.current_step += 1
            self.update_status_label()

    def shuffle_puzzle(self):
        self.puzzle = PuzzleShuffleService.shuffle_puzzle(self.puzzle_size)
        self.solution_steps = []
        self.current_step = 0
        self.num_expanded_nodes = 0
        self.update_tiles()
        self.update_status_label()
        self.previous_button.grid_remove()
        self.next_button.grid_remove()
        self.solve_button.grid()  # Show the solve button again

    def start_solve_puzzle(self):
        self.solve_button.grid_remove()  # Hide the solve button
        self.stop_button.grid()  # Show the stop button
        self.solve_button.config(text='Đang tìm giải pháp....', state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text='Đang tìm giải pháp....')
        threading.Thread(target=self.solve_puzzle).start()

    def stop_solve_puzzle(self):
        if self.solver:
            self.solver.stop()
            self.solve_button.config(text='Solve', state=tk.NORMAL)
            self.stop_button.grid_remove()  # Hide the stop button
            self.solve_button.grid()  # Show the solve button
            self.status_label.config(text='Đã dừng')

    def solve_puzzle(self):
        selected_algorithm = self.selected_algorithm.get()
        if selected_algorithm == 'A*':
            selected_heuristic = self.selected_heuristic.get() or HEURISTIC_TOTAL
            self.solver = PuzzleSolver(AStar(self.puzzle, heuristic=selected_heuristic))


        self.solver.run()
        self.solution_steps = self.solver.get_solution()
        self.num_expanded_nodes = self.solver.get_num_expanded_nodes()
        self.current_step = 0
        self.master.after(0, self.on_solve_complete)

    def on_solve_complete(self):
        self.update_tiles()
        self.update_status_label()
        self.solve_button.grid()  # Show the solve button
        self.solve_button.config(text='Solve', state=tk.NORMAL)
        self.stop_button.grid_remove()  # Hide the stop button
        self.previous_button.grid()
        self.next_button.grid()

    def previous_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.puzzle = self.solution_steps[self.current_step]
            self.update_tiles()
            self.update_status_label()

    def next_step(self):
        if self.current_step < len(self.solution_steps) - 1:
            self.current_step += 1
            self.puzzle = self.solution_steps[self.current_step]
            self.update_tiles()
            self.update_status_label()

    def auto_run(self):
        if self.current_step < len(self.solution_steps) - 1:
            # Gọi hàm thực hiện bước tự động
            self.run_auto_step()

    def run_auto_step(self):
        if self.current_step < len(self.solution_steps) - 1:
            # Thực hiện bước tiếp theo
            self.next_step()
            # Đặt lại thời gian trễ 1 giây trước khi gọi lại hàm này
            self.master.after(500, self.run_auto_step)  # Tự động gọi lại sau 1 giây

