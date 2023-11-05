import basic_sim_framework.scaffolding as sim
import basic_sim_framework.tk_stepper as viz
import basic_sim_framework.algo_helpers as algo

import numpy as np
import math
from scipy.optimize import linear_sum_assignment

particles = sim.generate_particle_coords(size=20, num_particles=49)
# target coords n slots in the center of the grid

# dense center
target_coords = [(x, y) for x in range(7, 14) for y in range(7, 14)]

# sparse
# target_coords = list(sim.generate_particle_coords(size=20, num_particles=49).values())

grid = sim.initialize_grid(target_coords, size=20)
sim.place_particles(grid, particles)

clone_grid = np.copy(grid)

# manhattan
def man_dist(from_pos, to_pos):
    return abs(from_pos[0] - to_pos[0]) + abs(from_pos[1] - to_pos[1])

# euclidean
def sq_dist(from_pos, to_pos):
    return (from_pos[0] - to_pos[0])**2 + (from_pos[1] - to_pos[1])**2

# squared manhattan
def sqman_dist(from_pos, to_pos):
    return man_dist(from_pos, to_pos)**2

assert len(particles) == len(target_coords), "need this for now"
def run_lsap(distance_fn):
    lsap_matrix = np.zeros((len(particles), len(target_coords)))
    for i, particle in particles.items():
        for j, target in enumerate(target_coords):
            lsap_matrix[i][j] = distance_fn(particle, target)
    return linear_sum_assignment(lsap_matrix)

particle_ids, slot_ids = run_lsap(sqman_dist)
hl_moves = [(particle, target_coords[slot]) for particle, slot in zip(particle_ids, slot_ids)]
print("hl_moves: ", hl_moves)

# map hl moves to ml moves

# a high level move to mid level move with manhattan path (pick the one with less particles in the way)
def get_manhattan_ll_path(hl_move):
    particle, target = hl_move
    x0, y0 = particles[particle]
    x1, y1 = target

    path_l = []
    num_obstacles_l = 0
    path_t = []
    num_obstacles_t = 0

    curr = (x0, y0)
    while curr != target:
        if x0 <= x1 and curr[0] < x1:
            path_t.append((curr, (curr[0] + 1, curr[1])))
            curr = (curr[0] + 1, curr[1])
        elif x0 > x1 and curr[0] > x1:
            path_t.append((curr, (curr[0] - 1, curr[1])))
            curr = (curr[0] - 1, curr[1])
        elif y0 <= y1 and curr[1] < y1:
            path_t.append((curr, (curr[0], curr[1] + 1)))
            curr = (curr[0], curr[1] + 1)
        elif y0 > y1 and curr[1] > y1:
            path_t.append((curr, (curr[0], curr[1] - 1)))
            curr = (curr[0], curr[1] - 1)

        if sim.is_filled(grid, curr):
            num_obstacles_t += 1

    curr = (x0, y0)
    while curr != target:
        if y0 <= y1 and curr[1] < y1:
            path_l.append((curr, (curr[0], curr[1] + 1)))
            curr = (curr[0], curr[1] + 1)
        elif y0 > y1 and curr[1] > y1:
            path_l.append((curr, (curr[0], curr[1] - 1)))
            curr = (curr[0], curr[1] - 1)
        elif x0 <= x1 and curr[0] < x1:
            path_l.append((curr, (curr[0] + 1, curr[1])))
            curr = (curr[0] + 1, curr[1])
        elif x0 > x1 and curr[0] > x1:
            path_l.append((curr, (curr[0] - 1, curr[1])))
            curr = (curr[0] - 1, curr[1])

        if sim.is_filled(grid, curr):
            num_obstacles_l += 1
    
    if num_obstacles_l < num_obstacles_t:
        return (num_obstacles_l, path_l)
    else:
        return (num_obstacles_t, path_t)

# ll_moves = [get_manhattan_ll_path(hl_move) for hl_move in hl_moves]
# ll_moves.sort(key=lambda x: x[0])

layers = algo.extract_layers(grid)
layers.reverse()
flattened_layers = []
for layer in layers:
    flattened_layers += layer[1]
sorted_hl = [[move for move in hl_moves if move[1] == target][0] for target in flattened_layers]
print("sorted_hl: ", sorted_hl)
ll_moves = [get_manhattan_ll_path(hl_move) for hl_move in sorted_hl]

zero_obs_ll_moves = []
# in case destination is currently filled by another particle
# that will be moved out of the way by a later move
deferred_moves = []
# print(len(ll_moves))
for _, path in ll_moves:
    if len(path) > 0 and sim.is_filled(grid, path[-1][1]):
        deferred_moves.append(path)
    else:
        # print("len of path:", len(path))
        zero_obs_ll_moves += sim.breakup_blocking_moves(grid, path)

while len(deferred_moves) > 0:
    # print("deferred_moves: ", deferred_moves)
    path = deferred_moves.pop(0)
    if len(path) > 0 and sim.is_filled(grid, path[-1][1]):
        deferred_moves.append(path)
    zero_obs_ll_moves += sim.breakup_blocking_moves(grid, path)

# print(len(zero_obs_ll_moves))

# Start Visualizer
viz.set_ll_moves(zero_obs_ll_moves)
viz.set_grid(clone_grid)
viz.start_viz()
