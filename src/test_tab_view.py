import pygame
import pygame.freetype
import components
from config import SETTINGS
from pygame.locals import (
    QUIT,
)

def test_print():
    print("xd")

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

screen.fill(SETTINGS.Appearance.summary_bg_color, pygame.Rect(0, 0, 800, 600))
tabView = components.TabView(screen, 
                             SETTINGS.Appearance.tab_view_bg_color, 
                             SETTINGS.Appearance.tab_selected_color,
                             SETTINGS.Appearance.tab_font_color, 
                             SETTINGS.Appearance.tab_fontsize, 
                             ["Results", "Graphs"], [1, test_print], 10, (0, 0, 600, 500))

tabView.center = screen.get_rect().center
graph = components.Graph(screen, (0, 0, 0), 10, ((100, 80), (125, 50), (110, 75), (131, 84), (134, 40), (130, 60)), (0, 0, 300, 300))
graph.center = tabView.get_empty_rect().center

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in tabView.buttons:
                button.check_click(pygame.mouse.get_pos())
    tabView.draw()
    graph.draw()
    pygame.display.update()
    clock.tick(SETTINGS.FPS)
pygame.quit()