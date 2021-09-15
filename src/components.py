import pygame
from config import SETTINGS


# Rect with possibility to call callback function
class CallbackRect(pygame.Rect):
    def __init__(self, *args):
        super().__init__(*args)

    def set_callback(self, callback, *args, **kwargs):
        self.callback = callback
        self.callback_args = args
        self.callback_kwargs = kwargs

    def is_clicked(self, mouse_pos):
        if self.collidepoint(mouse_pos):
            self.callback(*self.callback_args, **self.callback_kwargs)
            return True
        return False


# Button with callback
class Button(CallbackRect): 
    def __init__(self, screen, font, text, text_color, padding=(0, 0), outline_color=(0,0,0), outline_radius=0, *args):
        super().__init__(*args)
        self.screen = screen
        self.font = font
        self.text = text
        self.text_color = text_color
        self.padding = padding
        self.outline_color = outline_color
        self.outline_radius = outline_radius
        self.inflate_ip(self.padding) # to detect click on padded area too

    def draw(self):
        self.button_rect = pygame.draw.rect(self.screen, self.outline_color, self, self.outline_radius)
        self.text_rect = self.font.render_to(self.screen, self.inflate([-p for p in self.padding]), self.text, self.text_color)


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

    def is_clicked(self, mouse_pos):
        if self.switch_rect:
            if self.switch_rect.collidepoint(mouse_pos):
                self.toggle()
                self.callback(self.is_on())
                return True
        return False


# Graph data ((time_1, value_1), (time_2, value_2)...) in Rect
# Indices are beyond rect
class Graph(pygame.Rect):
    def __init__(self, screen, color, font_size, data, *args, draw_text_on_x_axis=False, draw_text_on_y_axis=False) -> None:
        super().__init__(*args)
        self.screen = screen
        self.data = sorted(data, key=lambda x: x[0])
        self.color = color
        self.font_size = font_size
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
        self.draw_text_on_x_axis = draw_text_on_x_axis
        self.draw_text_on_y_axis = draw_text_on_y_axis
    
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
            if self.draw_text_on_y_axis:
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
            if self.draw_text_on_x_axis:
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


# Changeable tabs container 
# tab_callbacks are designed for draw functions in empty area (get_empty_rect)
class TabView(pygame.Rect):
    def __init__(self, screen, bg_color, selected_tab_color, text_color, font_size, tab_labels, tab_callbacks, padding, *args) -> None:
        super().__init__(*args)
        self.screen = screen
        self.bg_color = bg_color
        self.selected_tab_color = selected_tab_color
        self.text_color = text_color
        self.font_size = font_size
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
        self.tab_labels = tab_labels
        self.tab_callbacks = tab_callbacks
        self.tab_label_width = self.font.get_rect(max(self.tab_labels, key=len), size=self.font_size).width + padding*2
        self.tab_label_height = font_size*2
        self.selected_tab = tab_labels[0]
        self.tab_buttons = [] # needs to be manually checked by check_click method
    
    def draw(self):
        self.screen.fill(self.bg_color, self)
        self.draw_tab_panel()
    
    def draw_tab_panel(self):
        tab_start_pos = [self.x, self.y]
        for i, tab_label in enumerate(self.tab_labels):
            tab_center = [tab_start_pos[0]+self.tab_label_width//2, 
                          tab_start_pos[1]+self.tab_label_height//2+self.tab_label_height*i]
            tab_rect = CallbackRect(0, 0, self.tab_label_width, self.tab_label_height)
            tab_rect.center = tab_center
            tab_rect.set_callback(self.change_tab, tab_label)
            self.tab_buttons.append(tab_rect)
            if tab_label == self.selected_tab:
                self.screen.fill(self.selected_tab_color, tab_rect)
            # draw seperating lines
            if i != 0:
                separating_line_x = tab_start_pos[0]
                separating_line_y = tab_start_pos[1]+self.tab_label_height*i
                pygame.draw.line(self.screen, (0, 0, 0), 
                                (separating_line_x, separating_line_y), 
                                (separating_line_x+self.tab_label_width, separating_line_y))
            # draw text
            text_rect = self.font.get_rect(tab_label, size=self.font_size) 
            text_rect.center = tab_center
            self.font.render_to(self.screen, text_rect, tab_label, self.text_color)

    def change_tab(self, tab_label):
        if tab_label in self.tab_labels:
            if tab_label != self.selected_tab:
                self.selected_tab = tab_label
                self.draw()
                self.tab_callbacks[self.tab_labels.index(tab_label)]()

    # returns empty rect (without labels panel) inside TabView
    def get_empty_rect(self):
        empty_rect = pygame.Rect(self)
        empty_rect.width -= self.tab_label_width
        empty_rect.x += self.tab_label_width
        return empty_rect


class Slider(CallbackRect):
    def __init__(self, screen, bg_color, font, text_color, font_size, line_color, min_value, max_value, current_value, gaps, line_width, button_inner_color, *args):
        super().__init__(*args)
        self.screen = screen
        self.bg_color = bg_color
        self.font = font
        self.text_color = text_color
        self.font_size = font_size
        self.line_color = line_color
        self.current_value = current_value
        self.min_value = min_value
        self.max_value = max_value
        self.gaps = max(2, (max_value-min_value) if max_value-min_value < 5 else 5) 
        self.gap = self.width/self.gaps
        self.line_width = line_width
        self.button_inner_color = button_inner_color
        self.outline_color = line_color
        self.outline_radius = line_width
        self.set_callback(self.update_slider_position)

    def set_call_on_change(self, call_on_change, *args, **kwargs):
        self.call_on_change = call_on_change
        self.call_on_change_args = args
        self.call_on_change_kwargs = kwargs

    def get_slider_position(self):
        slider_position = self.x+self.width/(self.max_value-self.min_value)*(self.current_value-self.min_value)
        return slider_position

    def update_slider_position(self):
        mouse_pos_x = pygame.mouse.get_pos()[0]
        self.current_value = self.min_value + round((mouse_pos_x-self.x)*(self.max_value-self.min_value)/(self.width-1))
        self.call_on_change(self.current_value, *self.call_on_change_args, **self.call_on_change_kwargs)
        self.clear()
        self.draw()
    
    def clear(self):
        rect_to_clear = self.inflate(self.font_size+self.outline_radius, self.font_size)
        if self.min_text_rect:
            rect_to_clear.union_ip(self.min_text_rect)
        if self.max_text_rect:
            rect_to_clear.union_ip(self.max_text_rect)
        self.screen.fill(self.bg_color, rect_to_clear)
    
    def draw(self):
        pygame.draw.line(self.screen, self.line_color, self.midleft, self.midright, self.line_width)
        for i in range(1, self.gaps):
            pos_x = self.x + i*self.gap
            start_y = self.y
            stop_y = self.y + self.height
            pygame.draw.line(self.screen, self.line_color, (pos_x, start_y), (pos_x, stop_y), self.line_width)
        self.draw_slider_button()
        self.draw_text()

    def draw_slider_button(self):
        slider_position = self.get_slider_position()
        button_rect = pygame.Rect(slider_position, self.centery, 0, 0).inflate(self.font_size, self.font_size*2)
        pygame.draw.rect(self.screen, self.button_inner_color, button_rect)
        pygame.draw.rect(self.screen, self.outline_color, button_rect, self.outline_radius)
    
    def draw_text(self):
        min_text = str(self.min_value)
        max_text = str(self.max_value)
        text_y = self.centery+self.font_size*1.25
        min_value_rect = self.font.get_rect(min_text, size=self.font_size) 
        min_value_rect.topleft = (self.left, text_y)
        self.min_text_rect = self.font.render_to(self.screen, min_value_rect, min_text, self.text_color)
        max_value_rect = self.font.get_rect(max_text, size=self.font_size) 
        max_value_rect.topright = (self.right, text_y)
        self.max_text_rect = self.font.render_to(self.screen, max_value_rect, max_text, self.text_color)

    def check_slider(self):
        if pygame.mouse.get_pressed(num_buttons=3)[0] == True:
            self.is_clicked(pygame.mouse.get_pos())