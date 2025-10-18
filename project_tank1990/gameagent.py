import pygame
import sys

pygame.init()
def pantalla_agente():
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and boton_volver.clickeado():
                return True
        
        WIN.fill(NEGRO)
        texto = font.render("PANTALLA AGENTE", True, BLANCO)
        WIN.blit(texto, (400, 300))
        boton_volver.dibujar(WIN)
        pygame.display.update()

boton_volver = Boton(0, 0, 100, 40, "VOLVER")