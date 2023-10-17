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

layers = algo.extract_layers(grid)

def astar_heuristic(grid, curr_coord, adj_coor):
    return 0
    particle_pos = []
    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if sim.is_filled(grid, (x, y)):
                particle_pos.append((x, y))
    
    min_dist = math.inf
    for particle in particle_pos:
        dist = abs(particle[0] - adj_coor[0]) + abs(particle[1] - adj_coor[1])
        if dist < min_dist:
            min_dist = dist
    return min_dist

nontarget_goal_pred = lambda p: lambda grid, pos: ((sim.is_filled(grid, pos) and not sim.is_target(grid, pos)) or sim.is_filled(grid, p))
all_goal_pred = lambda p: lambda grid, pos: sim.is_filled(grid, pos) or sim.is_filled(grid, p)

# print(algo.a_star(grid, (10, 10), astar_heuristic, as_goal_pred((10, 10))))

zero_obs_ll_moves = []
filled_slots = []
layers.reverse()

for layer in layers:
    layer_slots = layer[1] # get the slots in the layer
    for slot in layer_slots:
        success, path = algo.a_star(grid, slot, astar_heuristic, nontarget_goal_pred(slot), ignore_adj=lambda grid, pos: ((grid[pos[0]][pos[1]] == 3) or pos in filled_slots))

        if not success:
            print(filled_slots)
            success, path = algo.a_star(grid, slot, astar_heuristic, all_goal_pred(slot), ignore_adj=lambda grid, pos: pos in filled_slots)
            if success:
                filled_slots.append(slot)
                path.reverse()
                zero_obs_ll_moves += sim.breakup_blocking_moves(grid, path)
                continue
        
        filled_slots.append(slot)
        path.reverse()
        zero_obs_ll_moves += sim.breakup_blocking_moves(grid, path)

assert len(target_coords) == len(filled_slots), "not all slots are filled"

# Start Visualizer
viz.set_ll_moves(zero_obs_ll_moves)
viz.set_grid(clone_grid)
viz.start_viz()
