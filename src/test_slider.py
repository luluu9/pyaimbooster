import pygame
import pygame.freetype
import components
from config import SETTINGS
from pygame.locals import (
    QUIT,
)


pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

screen.fill(SETTINGS.Appearance.summary_bg_color, pygame.Rect(0, 0, 800, 600))
font = pygame.freetype.Font(SETTINGS.Appearance.default_font, 20)
slider = components.Slider(screen, font, (0, 0, 0), 15, (0, 0, 0), 0, 100, 50, 5, 5, SETTINGS.Appearance.background_color, screen.get_rect().center, (150, 20))
slider.center = screen.get_rect().center

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            slider.is_clicked(pygame.mouse.get_pos())
    screen.fill(SETTINGS.Appearance.background_color)
    slider.draw()
    pygame.display.update()
    clock.tick(SETTINGS.FPS)
pygame.quit()