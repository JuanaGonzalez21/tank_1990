# main.py
import sys
import pygame
import pygame.freetype

from agent import RandomExplorer, a_star_camino, RouteFollower  # modos del agente
import word                                                     # mundo (grid/dibujo)

# ===================== INICIALIZACIÓN =====================
pygame.init()
pygame.freetype.init()

# --- Ventana y colores (NO cambiar dimensiones) ---
WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank 1990 — Demo")

BLACK = (0, 0, 0)
WHITE = (230, 230, 230)
ORANGE = (255, 120, 0)
DARK = (22, 22, 22)

# =================== TABLERO Y CÓDIGOS ====================
# (NO tocar: controlan tamaño lógico del mundo)
TILE   = 64       # px por celda
GRID_W = 22       # ancho en celdas
GRID_H = 12       # alto  en celdas

EMPTY  = 0
GRASS  = 1
BRICK  = 2
TANK_C = 3
WIN_C  = 4

# ===================== CARGA DE ASSETS ====================
def load_scaled(path, w, h):
    """Carga un PNG con alpha y lo reescala a (w,h)."""
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (w, h))

SPR_TANK  = load_scaled("tank.png",  TILE, TILE)
SPR_BRICK = load_scaled("brick.png", TILE, TILE)
SPR_GRASS = load_scaled("grass.png", TILE, TILE)
SPR_WIN   = load_scaled("win.png",   TILE, TILE)
try:
    BG_IMG = pygame.image.load("bg.jpg").convert()
    BG_IMG = pygame.transform.smoothscale(BG_IMG, (WIDTH, HEIGHT))
except Exception:
    BG_IMG = None  # fondo opcional

# ======================== UI: BOTÓN =======================
class Button:
   
    def __init__(self, x, y, width, height, text, font_size=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.freetype.SysFont("Courier", font_size, bold=True)
        self.color = ORANGE
        self.hover = False

    def draw(self, surface):
        color = (255, 180, 50) if self.hover else self.color
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, color, self.rect, 3, border_radius=15)
        txt, r = self.font.render(self.text, WHITE)
        r.center = self.rect.center
        surface.blit(txt, r)

    def check_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# =============== SUBMENÚ: MODE AGENT (nuevo) ===============
def submenu_agente():
    """
    Pantalla intermedia al hacer clic en 'Mode Agent'.
    - 'No informado' -> explora aleatoriamente hasta llegar al WIN
    - 'Informado'    -> A* (ruta óptima)
    ESC -> volver al menú principal.
    """
    clock = pygame.time.Clock()
    title_font = pygame.freetype.SysFont("Courier", 64, bold=True)
    info_font  = pygame.freetype.SysFont("Courier", 22)

    w, h = 420, 78
    spacing = 22
    cx = WIDTH // 2 - w // 2
    cy = HEIGHT // 2 - (h*2 + spacing) // 2

    btn_noinf = Button(cx, cy + 0*(h+spacing), w, h, "No informado")
    btn_inf   = Button(cx, cy + 1*(h+spacing), w, h, "Informado")

    while True:
        clock.tick(60)
        mouse = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return "back"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_noinf.is_clicked(mouse): return "uninformed"
                if btn_inf.is_clicked(mouse):   return "informed"

        # fondo
        if BG_IMG: WIN.blit(BG_IMG, (0,0))
        else: WIN.fill(BLACK)

        for b in (btn_noinf, btn_inf):
            b.check_hover(mouse)
            b.draw(WIN)


        pygame.display.update()

# ===================== MODO: AGENTE (NO INF.) ==============
def mode_agente():
    """
    Modo NO INFORMADO: el tanque explora aleatoriamente (DFS random)
    hasta llegar a WIN. R: nuevo mapa | ESC: volver al menú.
    """
    clock = pygame.time.Clock()
    title_font = pygame.freetype.SysFont("Courier", 44, bold=True)
    info_font  = pygame.freetype.SysFont("Courier", 22)

    # 1) Generar nivel
    grid, start, goal = word.generar_nivel(
        GRID_W, GRID_H, EMPTY, GRASS, BRICK, TANK_C, WIN_C,
        densidad_brick=0.30, densidad_grass=0.15, max_intentos=200
    )

    # 2) Crear explorador aleatorio
    explorer = RandomExplorer(
        grid=grid, start=start, goal=goal,
        grid_w=GRID_W, grid_h=GRID_H,
        walkable={EMPTY, GRASS, WIN_C},
        step_ms=160
    )

    while True:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return True
                if e.key == pygame.K_r:
                    grid, start, goal = word.generar_nivel(
                        GRID_W, GRID_H, EMPTY, GRASS, BRICK, TANK_C, WIN_C,
                        densidad_brick=0.30, densidad_grass=0.15, max_intentos=200
                    )
                    explorer = RandomExplorer(
                        grid=grid, start=start, goal=goal,
                        grid_w=GRID_W, grid_h=GRID_H,
                        walkable={EMPTY, GRASS, WIN_C},
                        step_ms=160
                    )

        # avanzar una celda (cuando acumula step_ms)
        explorer.update(dt)

        # dibujar escena
        if BG_IMG: WIN.blit(BG_IMG, (0,0))
        else: WIN.fill(BLACK)

        title, tr = title_font.render("MODE AGENT — NO INFORMADO (Exploración aleatoria)", ORANGE)
        tr.midtop = (WIDTH // 2, 18); WIN.blit(title, tr)

        off_x, off_y = word.grid_screen_offset(WIDTH, HEIGHT, GRID_W, GRID_H, TILE)
        word.dibujar_grid(WIN, grid, GRID_W, GRID_H, TILE, DARK,
                          SPR_GRASS, SPR_BRICK, SPR_WIN, off_x, off_y)
        explorer.draw(WIN, SPR_TANK, off_x, off_y, TILE)

        # estado
        legend_y = off_y + GRID_H*TILE + 12
        tip, tipr = info_font.render("R: nuevo mapa | ESC: menú", WHITE)
        tipr.midtop = (WIDTH//2, legend_y); WIN.blit(tip, tipr)

        if explorer.finished and explorer.cell == goal:
            done, dr = info_font.render("¡Objetivo alcanzado!", ORANGE)
            dr.midtop = (WIDTH//2, legend_y + 26); WIN.blit(done, dr)

        pygame.display.update()

# ===================== MODO: AGENTE (INFORMADO) =============
def mode_agente_informado():
    """
    Modo INFORMADO: calcula ruta óptima con A* (heurística Manhattan)
    y anima al tanque siguiéndola. R: nuevo mapa | ESC: volver al menú.
    """
    clock = pygame.time.Clock()
    title_font = pygame.freetype.SysFont("Courier", 44, bold=True)
    info_font  = pygame.freetype.SysFont("Courier", 22)

    # 1) Generar nivel
    grid, start, goal = word.generar_nivel(
        GRID_W, GRID_H, EMPTY, GRASS, BRICK, TANK_C, WIN_C,
        densidad_brick=0.30, densidad_grass=0.15, max_intentos=200
    )

    # 2) Calcular ruta con A* y crear seguidor
    ruta = a_star_camino(grid, start, goal, GRID_W, GRID_H, {EMPTY, GRASS, WIN_C})
    follower = RouteFollower(ruta, step_ms=160)

    while True:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: return True
                if e.key == pygame.K_r:
                    grid, start, goal = word.generar_nivel(
                        GRID_W, GRID_H, EMPTY, GRASS, BRICK, TANK_C, WIN_C,
                        densidad_brick=0.30, densidad_grass=0.15, max_intentos=200
                    )
                    ruta = a_star_camino(grid, start, goal, GRID_W, GRID_H, {EMPTY, GRASS, WIN_C})
                    follower.reset(ruta)

        # avanzar por la ruta (si existe)
        follower.update(dt)

        # dibujar escena
        if BG_IMG: WIN.blit(BG_IMG, (0,0))
        else: WIN.fill(BLACK)

        title, tr = title_font.render("MODE AGENT — INFORMADO (A*)  |  R: nuevo mapa  |  ESC: menú", ORANGE)
        tr.midtop = (WIDTH // 2, 18); WIN.blit(title, tr)

        off_x, off_y = word.grid_screen_offset(WIDTH, HEIGHT, GRID_W, GRID_H, TILE)
        word.dibujar_grid(WIN, grid, GRID_W, GRID_H, TILE, DARK,
                          SPR_GRASS, SPR_BRICK, SPR_WIN, off_x, off_y)
        follower.draw(WIN, SPR_TANK, off_x, off_y, TILE)

        legend_y = off_y + GRID_H*TILE + 12
        if not follower.ruta:
            msg, mr = info_font.render("Sin ruta (A* no encontró camino). Pulsa R para regenerar.", WHITE)
            mr.midtop = (WIDTH//2, legend_y)
            WIN.blit(msg, mr)
        else:
            tip, tipr = info_font.render(f"Longitud ruta: {len(follower.ruta)} celdas", WHITE)
            tipr.midtop = (WIDTH//2, legend_y)
            WIN.blit(tip, tipr)
            if follower.finished and follower.cell == follower.ruta[-1] == goal:
                done, dr = info_font.render("¡Objetivo alcanzado por A*!", ORANGE)
                dr.midtop = (WIDTH//2, legend_y + 26); WIN.blit(done, dr)

        pygame.display.update()

# ========================= PLACEHOLDER ======================
def placeholder_mode(texto):
    """Pantalla temporal para modos sin implementar (ESC vuelve)."""
    clock = pygame.time.Clock()
    title_font = pygame.freetype.SysFont("Courier", 44, bold=True)
    info_font  = pygame.freetype.SysFont("Courier", 22)
    while True:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return True

        if BG_IMG: WIN.blit(BG_IMG,(0,0))
        else: WIN.fill(BLACK)

        t, r = title_font.render(texto, ORANGE); r.center = (WIDTH//2, HEIGHT//2)
        WIN.blit(t, r)
        tip, tr = info_font.render("ESC para volver al menú", WHITE)
        tr.midtop = (WIDTH//2, r.bottom + 18); WIN.blit(tip, tr)

        pygame.display.update()

# =========================== MENÚ ===========================
def menu():
    """
    Menú principal. Textos originales: 'Mode Agent', 'Mode User', 'COMPETITIVE'.
    """
    clock = pygame.time.Clock()
    title_font = pygame.freetype.SysFont("Courier", 72, bold=True)

    # Botones centrados
    w, h = 420, 78
    spacing = 30
    cx = WIDTH // 2 - w // 2
    cy = HEIGHT  // 2 - (h*2 + spacing*2) // 2

    btn_agent = Button(cx, cy + 0*(h+spacing), w, h, "Mode Agent")
    btn_user  = Button(cx, cy + 1*(h+spacing), w, h, "Mode User")
    btn_comp  = Button(cx, cy + 2*(h+spacing), w, h, "COMPETITIVE")

    while True:
        clock.tick(60)
        mouse = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if btn_agent.is_clicked(mouse): return "agent"
                if btn_user.is_clicked(mouse):  return "user"
                if btn_comp.is_clicked(mouse):  return "competitive"

        if BG_IMG: WIN.blit(BG_IMG,(0,0))
        else: WIN.fill(BLACK)

        for b in (btn_agent, btn_user, btn_comp):
            b.check_hover(mouse); b.draw(WIN)
        pygame.display.update()

# ============================ MAIN ==========================
def main():
    while True:
        opt = menu()
        if opt is None: break

        if opt == "agent":
            choice = submenu_agente()
            if choice is None: break
            if choice == "back": continue
            if choice == "uninformed":
                if mode_agente() is False: break
            elif choice == "informed":
                if mode_agente_informado() is False: break

        elif opt == "user":
            if placeholder_mode("MODE USER (en construcción)") is False: break
        elif opt == "competitive":
            if placeholder_mode("COMPETITIVE (en construcción)") is False: break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
