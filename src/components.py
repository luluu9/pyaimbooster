import pygame
from pygame import draw
from appearance import lobby_bg_color, switch_filling_color, switch_toggle_outline

# Button with an outline and a callback
class Button(): 
    def __init__(self, screen, font, text, text_color, text_rect, padding=0, outline_color=(0,0,0), outline_radius=0, custom_outline_rect=None):
        if custom_outline_rect:
            self.button_rect = pygame.draw.rect(screen, outline_color, custom_outline_rect, outline_radius)
        else:
            self.button_rect = pygame.draw.rect(screen, outline_color, text_rect.inflate(padding, padding), outline_radius)
        self.text_rect = font.render_to(screen, text_rect, text, text_color)

    def set_callback(self, callback, *args, **kwargs):
        self.callback = callback
        self.callback_args = args
        self.callback_kwargs = kwargs

    def check_click(self, mouse_pos):
        if self.button_rect:
            if self.button_rect.collidepoint(mouse_pos):
                self.callback(*self.callback_args, **self.callback_kwargs)


# Switch button with text change on toggle
class Switch(): 
    def __init__(self, screen, font, off_text, on_text, text_color, text_rect):
        self.screen = screen
        self.font = font
        self.text_color = text_color
        self.text_rect = text_rect
        self.current_text = off_text
        self.off_text = off_text
        self.on_text = on_text
        self.draw()

    def toggle(self):
        if self.is_on():
            self.current_text = self.off_text
        else:
            self.current_text = self.on_text
        # clear screen and draw
        self.screen.fill(lobby_bg_color, self.switch_outline)
        self.screen.fill(lobby_bg_color, self.text_rect)
        self.draw()

    def is_on(self):
        if self.current_text == self.on_text:
            return True
        else:
            return False

    def draw(self):
        outline = 5
        # draw text
        self.text_rect = self.font.render_to(self.screen, self.text_rect, self.current_text, self.text_color)
        # prepare rect for switch, move down and size down
        self.switch_rect = self.text_rect.move(0, self.text_rect.height*1.3).inflate(-self.text_rect.width/2, 0) 
        # fill switch with color
        self.filling_rect = pygame.draw.rect(self.screen, switch_filling_color, self.switch_rect)
        # create outline for switch
        self.switch_outline = pygame.draw.rect(self.screen, self.text_color, self.switch_rect, outline)
        # prepare size and position for toggle
        self.toggle_size = (self.switch_rect.width/2, self.switch_rect.height-outline*2)
        if self.current_text == self.on_text:
            self.toggle_position = (self.switch_rect.right-outline/2-self.toggle_size[0], self.switch_rect.y+outline)
        else:
            self.toggle_position = (self.switch_rect.x+outline/1.5, self.switch_rect.y+outline)
        # create toggle rect
        self.toggle_rect = pygame.draw.rect(self.screen, switch_toggle_outline, pygame.Rect(self.toggle_position, self.toggle_size), outline)

    def set_callback(self, callback):
        self.callback = callback

    def check_click(self, mouse_pos):
        if self.switch_rect:
            if self.switch_rect.collidepoint(mouse_pos):
                self.toggle()
                self.callback(self.is_on())

