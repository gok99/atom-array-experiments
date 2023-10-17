import basic_sim_framework.scaffolding as core

from heapq import heappop, heappush

# a star algorithm
# goal_test: (grid, coord) -> bool
# heuristic: (grid, curr_coord, adj_coord) -> int
def a_star(grid, start_coord, heuristic, goal_test, ignore_adj=lambda grid, coord: False):
    def get_path(parent, curr_coord):
        path = []
        while parent[curr_coord] is not None:
            parent_coord = parent[curr_coord]
            path.append((curr_coord, parent_coord))
            curr_coord = parent_coord
        return path[::-1]
    visited = set()
    parent = {}
    heap = []
    parent[start_coord] = None
    heappush(heap, (0, 0, start_coord, None))
    while len(heap) > 0:
        f_curr, g_curr, curr_coord, prev_coord = heappop(heap)

        if curr_coord in visited:
            continue

        visited.add(curr_coord)
        parent[curr_coord] = prev_coord

        if goal_test(grid, curr_coord):
            return (True, get_path(parent, curr_coord))
        
        g_adj = g_curr + 1
        for adj_coord in core.get_adjacent_slots(grid, curr_coord):
            if (adj_coord not in visited) and (not ignore_adj(grid, adj_coord)):
                f_adj = g_adj + heuristic(grid, curr_coord, adj_coord)
                heappush(heap, (f_adj, g_adj, adj_coord, curr_coord))
    return (False, [])

def extract_layers(grid):
    layers = []
    curr_layer = 0
    
    # get targets
    targets = []
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if core.is_target(grid, (x, y)):
                targets.append((x, y))
    
    while len(targets) > 0:
        layer_slots = []
        for target in targets:
            not_blocked = False
            for adj in core.get_adjacent_slots(grid, target):
                if adj not in targets:
                    not_blocked = True
                    break
            if not_blocked:
                layer_slots.append(target)

        for slot in layer_slots:
            targets.remove(slot)
        
        layers.append((curr_layer, layer_slots))
        curr_layer += 1
    
    return layers
