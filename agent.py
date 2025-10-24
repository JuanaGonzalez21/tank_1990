# agent.py
# Lógica del agente para:
# - Modo NO INFORMADO: exploración aleatoria con backtracking (DFS random).
# - Modo INFORMADO: A* (heurística Manhattan) + animación de ruta (RouteFollower).

import random
from collections import deque  # reservado por si quieres añadir BFS clásico

# -------------------- Vecinos cardinales --------------------
def _vecinos_cardinales(x, y, grid_w, grid_h):
    if x + 1 < grid_w: yield (x + 1, y)
    if x - 1 >= 0:     yield (x - 1, y)
    if y + 1 < grid_h: yield (x, y + 1)
    if y - 1 >= 0:     yield (x, y - 1)

# --------------- Exploración aleatoria (DFS random) ----------
class RandomExplorer:
    """
    Recorre el grid con DFS aleatorio paso a paso hasta alcanzar 'goal'.
    - Evita BRICK u otras celdas no caminables (definidas en 'walkable').
    - Marca visitados y hace backtracking cuando no hay vecinos nuevos.
    - Se mueve cada 'step_ms' para animación visible.
    """
    def __init__(self, grid, start, goal, grid_w, grid_h, walkable: set, step_ms=160):
        self.grid = grid
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.walkable = walkable

        self.cell = start
        self.goal = goal
        self.visited = {start}
        self.stack = []            # para backtracking
        self._accum = 0
        self.step_ms = step_ms
        self.finished = False      # True cuando llega a goal o no hay más camino

    def _candidatos(self, x, y):
        """Vecinos caminables no visitados en orden aleatorio."""
        vecs = [(nx, ny) for (nx, ny) in _vecinos_cardinales(x, y, self.grid_w, self.grid_h)
                if self.grid[ny][nx] in self.walkable and (nx, ny) not in self.visited]
        random.shuffle(vecs)
        return vecs

    def _siguiente_celda(self):
        if self.cell == self.goal:
            self.finished = True
            return self.cell

        x, y = self.cell
        cand = self._candidatos(x, y)
        if cand:
            # avanzar a un vecino aleatorio y guardar backtracking
            self.stack.append(self.cell)
            nxt = cand[0]
            self.visited.add(nxt)
            return nxt
        else:
            # sin vecinos nuevos: retroceder
            if self.stack:
                return self.stack.pop()
            else:
                # sin a dónde ir (raro porque el generador asegura camino)
                self.finished = True
                return self.cell

    def update(self, dt_ms):
        if self.finished:
            return
        self._accum += dt_ms
        if self._accum >= self.step_ms:
            self._accum = 0
            self.cell = self._siguiente_celda()
            if self.cell == self.goal:
                self.finished = True

    def draw(self, surface, spr_tank, off_x, off_y, tile):
        x, y = self.cell
        surface.blit(spr_tank, (off_x + x*tile, off_y + y*tile))

# ========================== A* (INFORMADO) ==========================
def _h_manhattan(a, b):
    ax, ay = a
    bx, by = b
    return abs(ax - bx) + abs(ay - by)

def a_star_camino(grid, start, goal, grid_w, grid_h, walkable: set):
    """
    Devuelve la ruta óptima (lista de celdas) usando A* con heurística Manhattan.
    Si no existe camino, retorna lista vacía.
    """
    from heapq import heappush, heappop

    sx, sy = start; gx, gy = goal
    open_heap = []
    heappush(open_heap, (0, start))  # (f_score, nodo)

    g = {start: 0}
    parent = {start: None}

    def vecinos(x, y):
        if x + 1 < grid_w: yield (x + 1, y)
        if x - 1 >= 0:     yield (x - 1, y)
        if y + 1 < grid_h: yield (x, y + 1)
        if y - 1 >= 0:     yield (x, y - 1)

    f_seen = {start: _h_manhattan(start, goal)}

    while open_heap:
        _, current = heappop(open_heap)
        if current == goal:
            # reconstruir ruta
            ruta = []
            cur = goal
            while cur is not None:
                ruta.append(cur)
                cur = parent[cur]
            ruta.reverse()
            return ruta

        cx, cy = current
        for nx, ny in vecinos(cx, cy):
            if grid[ny][nx] not in walkable:
                continue
            tentative = g[current] + 1  # costo uniforme por paso
            if (nx, ny) not in g or tentative < g[(nx, ny)]:
                g[(nx, ny)] = tentative
                parent[(nx, ny)] = current
                f = tentative + _h_manhattan((nx, ny), goal)
                # solo empujar si mejora el f observado
                if (nx, ny) not in f_seen or f < f_seen[(nx, ny)]:
                    f_seen[(nx, ny)] = f
                    heappush(open_heap, (f, (nx, ny)))

    return []  # sin ruta

# ===================== SEGUIDOR DE RUTA (ANIMACIÓN) =================
class RouteFollower:
    """
    Anima al tanque siguiendo una ruta (lista de celdas) calculada (p. ej., A*).
    """
    def __init__(self, ruta, step_ms=160):
        self.ruta = ruta or []
        self.i = 0
        self.cell = self.ruta[0] if self.ruta else None
        self._accum = 0
        self.step_ms = step_ms
        self.finished = False if self.ruta else True

    def reset(self, ruta):
        self.ruta = ruta or []
        self.i = 0
        self.cell = self.ruta[0] if self.ruta else None
        self._accum = 0
        self.finished = False if self.ruta else True

    def update(self, dt_ms):
        if self.finished or not self.ruta:
            return
        self._accum += dt_ms
        if self._accum >= self.step_ms:
            self._accum = 0
            if self.i < len(self.ruta) - 1:
                self.i += 1
                self.cell = self.ruta[self.i]
            if self.i >= len(self.ruta) - 1:
                self.finished = True

    def draw(self, surface, spr_tank, off_x, off_y, tile):
        if self.cell is None:
            return
        x, y = self.cell
        surface.blit(spr_tank, (off_x + x*tile, off_y + y*tile))
