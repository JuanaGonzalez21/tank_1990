import pygame
import time
import random
import pygame.freetype

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank 1990")

BG = pygame.transform.scale(pygame.image.load("bg.jpg"), (  WIDTH, HEIGHT))
WHITE = (255 ,255 ,255)

#Montamos el background
def draw():
    WIN.blit(BG, (0,0))
    pygame.display.update()

def text_bottom(text, font_size, text_rgb, bg_rgb):
    font = pygame.freetype.Sysfont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


def main():
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        draw()

    pygame.quit()

if __name__ == "__main__":
    main()

