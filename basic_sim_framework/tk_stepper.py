import tkinter as tk
import numpy as np
import basic_sim_framework.scaffolding as sim

# Global variables
grid_size = 10
grid = np.array([[0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1],
                [0, 0, 0, 0, 1],
                [2, 2, 2, 2, 3]])
ll_moves = []
current_move = 0
current_path = 1
canvas = None
last_moved_particle = None
current_move_var = None

# Create a Tkinter window
window = tk.Tk()
window.title("Array Visualizer")

# Function to draw grid backgrounds and circles on the canvas based on the array
def draw_grid():
    if canvas == None:
        print("canvas is uninitialized! call set_grid() first")
        return

    canvas.delete("all")  # Clear the canvas
    cell_width = 40  # Adjust the cell width to your desired size

    for i in range(grid_size):
        for j in range(grid_size):
            x0 = j * cell_width
            y0 = i * cell_width
            x1 = x0 + cell_width
            y1 = y0 + cell_width

            if grid[i][j] == 0 or grid[i][j] == 1:
                canvas.create_rectangle(x0, y0, x1, y1, fill="white")  # White grid background

            if grid[i][j] == 2 or grid[i][j] == 3:
                canvas.create_rectangle(x0, y0, x1, y1, fill="green")  # Green grid background

            if grid[i][j] == 1 or grid[i][j] == 3:
                canvas.create_oval(x0, y0, x1, y1, fill="blue")
    
    move_label.config(text="Current Distance: " + str(current_move))
    total_label.config(text="Total Distance: " + str(len(ll_moves)))
    path_label.config(text="Current Move (Path): " + str(current_path))

####################

def set_grid(new_grid):
    global grid_size
    global grid
    global canvas

    temp_grid_size = len(new_grid)
    assert temp_grid_size == len(new_grid[0]), "Grid must be square"
    # set grid
    grid_size = temp_grid_size
    grid = new_grid
    # set canvas
    canvas = tk.Canvas(window, width=grid_size * 40, height=grid_size * 40)
    canvas.pack()

def set_ll_moves(new_ll_moves):
    global current_move_var
    global ll_moves
    ll_moves = new_ll_moves
    # Create a Tkinter IntVar to store the current move position
    current_move_var = tk.IntVar()
    current_move_var.set(0)  # Initialize the slider position to 0

    # Create a Scale widget (slider) for controlling the current move
    move_slider = tk.Scale(window, from_=0, to=len(ll_moves), orient=tk.HORIZONTAL, variable=current_move_var)
    move_slider.pack()
    # Bind the slider's value change to the update_grid_from_slider function
    current_move_var.trace_add("write", update_grid_from_slider)

####################

def forward_fn(current_move):
    global last_moved_particle
    global current_path

    if current_move < len(ll_moves):
        sim.execute_do_ll_move(grid, ll_moves[current_move][0], ll_moves[current_move][1])
        if last_moved_particle != None and last_moved_particle != ll_moves[current_move][0]:
            current_path += 1
        last_moved_particle = ll_moves[current_move][1]
        return current_move + 1
    else:
        return current_move

def backward_fn(current_move):
    global last_moved_particle
    global current_path

    if current_move > 0:
        sim.execute_undo_ll_move(grid, ll_moves[current_move - 1][0], ll_moves[current_move - 1][1])
        if last_moved_particle != None and last_moved_particle != ll_moves[current_move - 1][1]:
            current_path -= 1
        last_moved_particle = ll_moves[current_move - 1][0]
        return current_move - 1
    else:
        return current_move

# Function to update the grid based on the slider's value
def update_grid_from_slider(*args):
    global current_move
    target_move = current_move_var.get()
    if target_move > current_move:
        while target_move > current_move:
            current_move = forward_fn(current_move)
    elif target_move < current_move:
        while target_move < current_move:
            current_move = backward_fn(current_move)
    draw_grid()

# Function to move forward through the list of moves
def move_forward():
    global current_move
    current_move = forward_fn(current_move)
    current_move_var.set(current_move)
    draw_grid()

# Function to move backward through the list of moves
def move_backward():
    global current_move
    current_move = backward_fn(current_move)
    current_move_var.set(current_move)
    draw_grid()

# Label to display the current move
path_label = tk.Label(window, text="Current Move: 0")
path_label.pack()

move_label = tk.Label(window, text="Current Distance: 0")
move_label.pack()

total_label = tk.Label(window, text="Current Distance: 0")
total_label.pack()

# Buttons to move forward and backward through the list of moves
forward_button = tk.Button(window, text="Forward", command=move_forward)
forward_button.pack()

backward_button = tk.Button(window, text="Backward", command=move_backward)
backward_button.pack()

def start_viz():
    # Initial drawing
    draw_grid()
    # Run the Tkinter main loop
    window.mainloop()
