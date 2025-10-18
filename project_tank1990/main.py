import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Herencia Simple en Pygame")
clock = pygame.time.Clock()

# Clase base
class Entidad:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, self.rect)

# Clase derivada
class Jugador(Entidad):
    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

player = Jugador(100, 100, 50, 50)
color = (0, 128, 255)

# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.mover(-5, 0)
    if keys[pygame.K_RIGHT]:
        player.mover(5, 0)
    if keys[pygame.K_UP]:
        player.mover(0, -5)
    if keys[pygame.K_DOWN]:
        player.mover(0, 5)

    screen.fill((0, 0, 0))
    player.draw(screen, color)
    pygame.display.flip()
    clock.tick(30)
