import pygame
import components
from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE
)

# PYGAME INIT
pygame.init()
screen = pygame.display.set_mode((800, 600))
screen.fill((255, 255, 255))


center = screen.get_rect().center
graph = components.Graph(screen, ((100, 80), (125, 90), (110, 75)), (0, 0, 300, 300))
graph.center = center
graph.draw()

# MAINLOOP
running = True
while running:
    for event in pygame.event.get((QUIT, KEYDOWN)):
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
    # refresh display
    pygame.display.update()
pygame.quit()
