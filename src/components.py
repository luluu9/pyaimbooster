import pygame
from config import SETTINGS


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
        self.screen.fill(SETTINGS.Appearance.lobby_bg_color, self.switch_outline)
        self.screen.fill(SETTINGS.Appearance.lobby_bg_color, self.text_rect)
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
        self.filling_rect = pygame.draw.rect(self.screen, SETTINGS.Appearance.switch_filling_color, self.switch_rect)
        # create outline for switch
        self.switch_outline = pygame.draw.rect(self.screen, self.text_color, self.switch_rect, outline)
        # prepare size and position for toggle
        self.toggle_size = (self.switch_rect.width/2, self.switch_rect.height-outline*2)
        if self.current_text == self.on_text:
            self.toggle_position = (self.switch_rect.right-outline/2-self.toggle_size[0], self.switch_rect.y+outline)
        else:
            self.toggle_position = (self.switch_rect.x+outline/1.5, self.switch_rect.y+outline)
        # create toggle rect
        self.toggle_rect = pygame.draw.rect(self.screen, SETTINGS.Appearance.switch_toggle_outline, pygame.Rect(self.toggle_position, self.toggle_size), outline)

    def set_callback(self, callback):
        self.callback = callback

    def check_click(self, mouse_pos):
        if self.switch_rect:
            if self.switch_rect.collidepoint(mouse_pos):
                self.toggle()
                self.callback(self.is_on())


# Graph data ((time_1, value_1), (time_2, value_2)...) in Rect
# Indices are beyond rect
class Graph(pygame.Rect):
    def __init__(self, screen, color, font_size, data, *args) -> None:
        super().__init__(*args)
        self.screen = screen
        self.data = sorted(data, key=lambda x: x[0])
        self.color = color
        self.font_size = font_size
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
    
    def draw(self):
        if len(self.data) < 2:
            print("Not enough data to draw!")
            return
        
        axes_width = 5
        lines_width = 3
        index_width = 2
        indice_gap = 30
        indice_margin = 20

        # draw axes
        pygame.draw.line(self.screen, self.color, self.topleft, self.bottomleft, axes_width)
        pygame.draw.line(self.screen, self.color, self.bottomleft, self.bottomright, axes_width)

        # draw indices
        x_delta, y_delta = self.get_deltas()
        for y_pos in range(0, self.height+1, indice_gap): # +1 to show most-upper (self.height) value
            y_value = int(y_pos/y_delta)
            y_screen_pos = self.y+self.height-y_pos
            # draw index line
            if y_pos != 0 and y_pos != self.height: # don't draw lines on edges
                pygame.draw.line(self.screen, self.color, (self.x-axes_width, y_screen_pos), (self.x+axes_width, y_screen_pos), index_width)
            # draw text value
            text_rect = self.font.get_rect(str(y_value), size=self.font_size) 
            text_rect.midright = (self.x-indice_margin, y_screen_pos)
            self.font.render_to(self.screen, text_rect, str(y_value), self.color)
        
        for i, x_pos in enumerate(range(0, self.width+1, int(x_delta))):
            x_value = self.data[i][0]
            x_screen_pos = self.x+self.width-x_pos
            # draw index line
            if x_pos != 0 and x_pos != self.height: # don't draw lines on edges
                pygame.draw.line(self.screen, self.color, (x_screen_pos, self.y+self.width-axes_width), (x_screen_pos, self.y+self.width+axes_width), index_width)
            # draw text value
            text_rect = self.font.get_rect(str(x_value), size=self.font_size) 
            text_rect.midtop = (x_screen_pos, self.y+self.height+indice_margin)
            self.font.render_to(self.screen, text_rect, str(x_value), self.color)

        # get data to draw
        prepared_data = self.get_normalized_data()
        # draw data
        pygame.draw.lines(self.screen, self.color, False, prepared_data, lines_width)

    # one graph unit (currently only y-axis) equals delta pixels
    def get_deltas(self):
        min_y_value = 0
        max_y_value = max(self.data, key=lambda y: y[1])[1]
        x_delta = self.width/(len(self.data)-1)
        y_delta = self.height/(max_y_value - min_y_value)
        return x_delta, y_delta

    # returns data according to rect size
    def get_normalized_data(self):
        x_delta, y_delta = self.get_deltas()
        normalized_data = []
        for i, (x, y) in enumerate(self.data):
            normalized_data.append((self.x+i*x_delta, self.bottom-y*y_delta))
        return normalized_data