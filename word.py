# word.py
# Mundo: generación del mapa + utilidades de posicionamiento y dibujo.
import random
from collections import deque
import pygame

# ---------- offsets para centrar la grilla ----------
def grid_screen_offset(width: int, height: int, grid_w: int, grid_h: int, tile: int):
    bw = grid_w * tile
    bh = grid_h * tile
    off_x = (width - bw) // 2
    off_y = (height - bh) // 2
    return off_x, off_y

# ---------- dibujar grilla y celdas ----------
def dibujar_grid(surface, grid, grid_w: int, grid_h: int, tile: int,
                 dark_color, spr_grass, spr_brick, spr_win, off_x: int, off_y: int):
    """
    Dibuja el mapa (GRASS/BRICK/WIN) y la rejilla. El tanque se dibuja aparte.
    """
    for y in range(grid_h):
        for x in range(grid_w):
            rect = pygame.Rect(off_x + x*tile, off_y + y*tile, tile, tile)
            cell = grid[y][x]

            if cell == 1:      # GRASS
                surface.blit(spr_grass, rect.topleft)
            else:
                pygame.draw.rect(surface, dark_color, rect, 0)

            if cell == 2:      # BRICK
                surface.blit(spr_brick, rect.topleft)
            elif cell == 4:    # WIN
                surface.blit(spr_win, rect.topleft)

            pygame.draw.rect(surface, (40,40,40), rect, 1)  # rejilla sutil

# ---------- generación del nivel ----------
def _vecinos_cardinales(x, y, grid_w, grid_h):
    if x + 1 < grid_w: yield (x + 1, y)
    if x - 1 >= 0:     yield (x - 1, y)
    if y + 1 < grid_h: yield (x, y + 1)
    if y - 1 >= 0:     yield (x, y - 1)

def _hay_camino_bfs(grid, start, goal, grid_w, grid_h, walkable={0,1,4}):
    sx, sy = start
    gx, gy = goal
    q = deque([(sx, sy)])
    vis = {(sx, sy)}
    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy): return True
        for nx, ny in _vecinos_cardinales(x, y, grid_w, grid_h):
            if (nx, ny) not in vis and grid[ny][nx] in walkable:
                vis.add((nx, ny))
                q.append((nx, ny))
    return False

def generar_nivel(grid_w: int, grid_h: int,
                  empty: int, grass: int, brick: int, tank_c: int, win_c: int,
                  densidad_brick: float = 0.30, densidad_grass: float = 0.15,
                  max_intentos: int = 200):
    """
    Genera un grid aleatorio con BRICK/GRASS y coloca TANK_C (start) y WIN_C (goal).
    Repite hasta que exista camino válido entre TANK y WIN.
    """
    for _ in range(max_intentos):
        grid = [[empty for _ in range(grid_w)] for _ in range(grid_h)]

        for y in range(grid_h):
            for x in range(grid_w):
                r = random.random()
                if r < densidad_brick:
                    grid[y][x] = brick
                elif r < densidad_brick + densidad_grass:
                    grid[y][x] = grass

        sy = random.randint(0, grid_h-1)
        gy = random.randint(0, grid_h-1)
        start = (0, sy)
        goal  = (grid_w-1, gy)

        grid[sy][0] = tank_c
        grid[gy][grid_w-1] = win_c

        # despejar alrededor de start/goal
        for nx, ny in _vecinos_cardinales(*start, grid_w, grid_h):
            if grid[ny][nx] == brick: grid[ny][nx] = empty
        for nx, ny in _vecinos_cardinales(*goal, grid_w, grid_h):
            if grid[ny][nx] == brick: grid[ny][nx] = empty

        if _hay_camino_bfs(grid, start, goal, grid_w, grid_h, {empty, grass, win_c}):
            return grid, start, goal

    # Fallback (pasillo)
    grid = [[empty for _ in range(grid_w)] for _ in range(grid_h)]
    sy = random.randint(0, grid_h-1)
    gy = random.randint(0, grid_h-1)
    start = (0, sy)
    goal  = (grid_w-1, gy)
    grid[sy][0] = tank_c
    grid[gy][grid_w-1] = win_c
    return grid, start, goal
