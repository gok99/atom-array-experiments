import numpy as np
import random
import matplotlib.pyplot as plt

DEFAULT_GRID_SIZE = 10
# cell value legend
# 0: empty non-target
# 1: filled non-target
# 2: empty target
# 3: filled target
def is_empty(grid, coord):
    cell_value = grid[coord[0]][coord[1]]
    return cell_value == 0 or cell_value == 2

def is_filled(grid, coord):
    cell_value = grid[coord[0]][coord[1]]
    return cell_value == 1 or cell_value == 3

def is_target(grid, coord):
    cell_value = grid[coord[0]][coord[1]]
    return cell_value == 2 or cell_value == 3

def is_adjacent(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1

def is_within_bounds(coord, size=DEFAULT_GRID_SIZE):
    x, y = coord
    return x >= 0 and x < size and y >= 0 and y < size

def is_valid_move(grid, from_slot, to_slot):
    return is_filled(grid, from_slot) and \
           is_within_bounds(to_slot, size=grid.shape[0]) and \
           is_empty(grid, to_slot) and \
           is_adjacent(from_slot, to_slot)

# generate GRID_SIZE^2 / 2 unqiue (x, y) coordinates in the grid
def generate_particle_coords(size=DEFAULT_GRID_SIZE, num_particles=None):
    if num_particles == None:
        num_particles = size * size // 2
    particle_coords = set()
    while len(particle_coords) < num_particles:
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        particle_coords.add((x, y))

    # give them ids
    particles = {}
    for i, coord in enumerate(particle_coords):
        particles[i] = coord
    return particles

# set up the grid (side-effecting)
def initialize_grid(target_coords, size=DEFAULT_GRID_SIZE):
    grid = np.zeros((size, size))
    for coord in target_coords:
        grid[coord[0]][coord[1]] = 2
    return grid

# randomly place n particles in the grid (side-effecting)
def place_particles(grid, particles):
    for coord in particles.values():
        if grid[coord[0]][coord[1]] == 2:
            grid[coord[0]][coord[1]] = 3
        else:
            grid[coord[0]][coord[1]] = 1
    return grid

def pretty_print(grid):
    for row in grid:
        print(row)

# a high-level move defines a particle to be moved and a slot to be moved to
# an algorithm (e.g. A*Star) compiles a high level move to a sequence of mid
# level moves

# a mid-level move defines a particle (id) to be moved and a to_slot.
# for a given id <-> slot mapping, and a grid, a mid level move is valid if the
# particle id exists and the to_slot is adjacent and empty

# a low level move defines a from_slot and a to_slot. for a giving grid an ll
# move is valid if the from_slot is filled and the to_slot is empty and adjacent
# a low level move can be reversed by swapping the from_slot and to_slot

def get_adjacent_slots(grid, coord):
    x, y = coord
    slots = []
    for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        x1, y1 = x + dx, y + dy
        if is_within_bounds((x1, y1), size=grid.shape[0]):
            slots.append((x1, y1))
    return slots

def get_available_moves(grid, particles):
    moves = []
    for particle_id, coord in particles.items():
        # get all adjacent empty slots
        for (dx, dy) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                x, y = coord[0] + dx, coord[1] + dy
                if is_valid_move(grid, coord, (x, y)):
                    moves.append((particle_id, (x, y)))
    return moves

# only side effecting, returns nothing
def execute_do_ll_move(grid, from_slot, to_slot):
    assert is_valid_move(grid, from_slot, to_slot), "ll move is not valid"
    # update grid
    if is_target(grid, from_slot):
        grid[from_slot[0]][from_slot[1]] = 2
    else:
        grid[from_slot[0]][from_slot[1]] = 0
    
    if is_target(grid, to_slot):
        grid[to_slot[0]][to_slot[1]] = 3
    else:
        grid[to_slot[0]][to_slot[1]] = 1

def execute_undo_ll_move(grid, from_slot, to_slot):
    execute_do_ll_move(grid, to_slot, from_slot)

# compile ml_move to an ll_move
def ll_move_of_ml_move(grid, particles, ml_move):
    particle_id, to_slot = ml_move
    from_slot = particles[particle_id]
    
    assert is_valid_move(grid, from_slot, to_slot)
    return (from_slot, to_slot)

def breakup_blocking_moves(grid, ll_moves):
    # end slot must be empty and start slot must be filled
    assert len(ll_moves) == 0 or is_empty(grid, ll_moves[-1][1])
    assert len(ll_moves) == 0 or is_filled(grid, ll_moves[0][0])

    # execute ll moves
    unblocked_ll_moves = []
    stashed_moves = []
    for ll_move in ll_moves:
        if is_valid_move(grid, ll_move[0], ll_move[1]):
            execute_do_ll_move(grid, ll_move[0], ll_move[1])
            unblocked_ll_moves.append(ll_move)
            if len(stashed_moves) > 0:
                stashed_moves.reverse()
                for stashed_move in stashed_moves:
                    execute_do_ll_move(grid, stashed_move[0], stashed_move[1])
                    unblocked_ll_moves.append(stashed_move)
                stashed_moves = []
        else:
            stashed_moves.append(ll_move)
    
    assert len(stashed_moves) == 0, "stashed moves should be empty"
    return unblocked_ll_moves
