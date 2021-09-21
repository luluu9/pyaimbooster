import pygame
import random
import history
from config import SETTINGS
from components import Button, Switch, Graph, TabView, Slider
from sounds import (hit_sound, miss_sound)


# BLUEPRINT:
# class GameMode():
#     def __init__(self, screen):
#         self.screen = screen

#     def load(self):
#         pass

#     def frame(self):
#         pass


class Target():
    def __init__(self, screen, grow=0, max_radius=50, duration=1.0, outline_margin=4, forbidden_rects=[]):
        self.radius = 0
        self.screen = screen
        self.forbidden_rects = forbidden_rects
        self.max_radius = max_radius
        self.duration = duration
        self.grow = grow
        self.grow_step = max_radius/(duration*1000/2) # radius increase per milisecond
        self.outline_margin = outline_margin
        self.pos = self.get_allowed_pos()
        self.reached_max = False
        if not grow:
            self.radius = self.max_radius
    
    def update(self, delta_time=0):
        if self.grow:
            if self.radius < self.max_radius and not self.reached_max:
                self.radius += self.grow_step * delta_time
            else:
                self.reached_max = True
                self.radius -= self.grow_step * delta_time
                # destroy this object if smaller than 1px
                if self.radius <= 0:
                    return False 
        self.draw()

    def draw(self):
        # draw outline
        pygame.draw.circle(self.screen, SETTINGS.Appearance.outline_color, self.pos, self.radius, self.outline_margin)
        # draw filling
        pygame.draw.circle(self.screen, SETTINGS.Appearance.filling_color, self.pos, self.radius-self.outline_margin)

    def mouse_collides(self, mouse_pos):
        if pow((mouse_pos[0] - self.pos[0]), 2) + pow((mouse_pos[1] - self.pos[1]), 2) <= pow(self.radius, 2):
            return True
    
    def get_random_pos(self, margin=0):
        x = random.randint(margin, SETTINGS.SCREEN_WIDTH-margin)
        y = random.randint(margin, SETTINGS.SCREEN_HEIGHT-margin)
        return (x, y)
    
    # get free space for spawn
    def get_allowed_pos(self):
        for i in range(200): # to prevent freezing if there is no more space for targets
            pos = self.get_random_pos(self.max_radius)
            if not self.rect_in_forbidden_area(pos):
                return pos
        return (100, 100)

    # check if targets would overlap
    def rect_in_forbidden_area(self, pos):
        rect_to_check = self.get_final_rect(pos)
        for rect in self.forbidden_rects:
            if rect.colliderect(rect_to_check):
                return True
        return False
    
    # get max occupied space as rect
    def get_final_rect(self, center=None):
        rect = pygame.Rect((0, 0), (self.max_radius*2, self.max_radius*2))
        if center == None:
            rect.center = self.pos
        else:
            rect.center = center
        return rect


class StaticButtons():
    def frame(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.is_clicked(pygame.mouse.get_pos()):
                        break


class ShootingMode():
    def __init__(self, screen, game):
        game.reset() # reset events and scoreboard
        if game.challenge == True:
            pygame.time.set_timer(game.events["END_CHALLENGE"], SETTINGS.CHALLENGE_TIME, True)
        self.screen = screen
        self.game = game
        self.scoreCounter = game.scoreCounter
        self.targets_to_delete = []
        self.targets = []

    def get_occupied_rects(self):
        occupied = []
        for target in self.targets:
            occupied.append(target.get_final_rect())
        return occupied
    
    def save_results(self):
        results = {
            "Hits": self.scoreCounter.get_hits(),
            "Accuracy": self.scoreCounter.get_accuracy(),
            "Median response": self.scoreCounter.get_median_reaction_time()
        }
        history.add_results(self.game.game_mode, results)


class Lobby(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.buttons = []

    def load(self):
        self.screen.fill(SETTINGS.Appearance.lobby_bg_color)
        gamemodes = ["Arcade", "Speedy fingers", "AWP", "Settings"]
        
        # prepare variables for buttons
        font = pygame.freetype.Font(SETTINGS.Appearance.default_font, SETTINGS.Appearance.lobby_fontsize)
        gap_betweens_buttons = SETTINGS.Appearance.lobby_fontsize * 1.3
        buttons_padding = SETTINGS.Appearance.buttons_padding
        screen_center = self.screen.get_rect().center
        start_x = screen_center[0]
        start_y = screen_center[1] - (len(gamemodes)/2)*gap_betweens_buttons

        # find biggest rect to function as background rect
        biggest_rect = font.get_rect(max(gamemodes, key=len), size=SETTINGS.Appearance.lobby_fontsize)

        for i, gamemode in enumerate(gamemodes):
            # fit text rect
            text_rect = biggest_rect 
            text_rect.center = (start_x, start_y + gap_betweens_buttons * i)
            
            # create and render button  
            button = Button(self.screen, font, gamemode, SETTINGS.Appearance.lobby_color, buttons_padding, SETTINGS.Appearance.lobby_color, 5, text_rect)
            button.draw()

            # set callbacks to change game mode
            button.set_callback(self.game.change_game_mode, gamemode)
            self.buttons.append(button)
        
        # Create switch for challenge/training mode
        text_rect = font.get_rect("Training", size=SETTINGS.Appearance.lobby_fontsize)
        text_rect.topright = self.screen.get_rect().inflate(-20, -20).topright
        switch = Switch(self.screen, font, "Training", "Challng", SETTINGS.Appearance.lobby_color, text_rect)
        switch.set_callback(self.game.set_challenge)
        self.buttons.append(switch)

        # Check if switch was toggled earlier
        if self.game.challenge == True:
            switch.toggle() 


class Summary(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.scoreCounter = game.scoreCounter
        self.previous_game_mode = game.game_mode # change this name to more precise
        self.buttons = []
        self.result_types = history.get_result_types(self.previous_game_mode)
        self.current_graph_type = self.result_types[0] if self.result_types else ""
        self.font_size = SETTINGS.Appearance.summary_fontsize
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
        self.buttons_padding = SETTINGS.Appearance.buttons_padding
        self.next_button = None
        self.previous_button = None
        self.play_again_button = None
        self.return_button = None

    def load(self):
        # prepare
        self.screen.fill(SETTINGS.Appearance.summary_bg_color)
        
        # create TabView
        self.tab_view = TabView(self.screen,
                             SETTINGS.Appearance.tab_view_bg_color, 
                             SETTINGS.Appearance.tab_selected_color,
                             SETTINGS.Appearance.tab_font_color, 
                             SETTINGS.Appearance.tab_fontsize, 
                             ["Results", "Graphs"], [self.show_results, self.show_graph], 10, (0, 0, 600, 500))
        self.tab_view.center = self.screen.get_rect().center
        self.tab_view.draw()
        self.buttons.extend(self.tab_view.tab_buttons)

        # show stats
        self.show_results()

    def show_main_buttons(self):
        midbottom = self.tab_view.midbottom 
        if not self.play_again_button:
            play_rect = self.font.get_rect("Play again", size=self.font_size) 
            play_rect.midright = midbottom
            play_rect.move_ip(-self.buttons_padding[0], -self.font_size) # to give some space between buttons
            self.play_again_button = Button(self.screen, self.font, "Play again", SETTINGS.Appearance.summary_color, self.buttons_padding, SETTINGS.Appearance.summary_color, 5, play_rect)
            self.play_again_button.set_callback(self.game.change_game_mode, self.previous_game_mode)
            self.buttons.append(self.play_again_button)
        if not self.return_button:
            return_rect = self.font.get_rect("Return", size=self.font_size) 
            return_rect.midleft = midbottom
            return_rect.move_ip(self.buttons_padding[0], -self.font_size)
            self.return_button = Button(self.screen, self.font, "Return", SETTINGS.Appearance.summary_color, self.buttons_padding, SETTINGS.Appearance.summary_color, 5, return_rect)
            self.return_button.set_callback(self.game.change_game_mode, "Lobby")
            self.buttons.append(self.return_button)
        self.play_again_button.draw()
        self.return_button.draw()

    def show_results(self):
        def show_variable(text, var, pos):
            var_text = f"{text}: {var}"
            text_rect = self.font.get_rect(var_text, size=self.font_size) 
            text_rect.topleft = pos.topleft
            self.font.render_to(self.screen, text_rect, var_text, SETTINGS.Appearance.summary_color)

        gap = self.font_size * 1.5
        hits_ratio = f"{self.scoreCounter.get_hits()}/{self.scoreCounter.get_all_targets()}"
        response_time = f"{int(self.scoreCounter.get_median_reaction_time()*1000)} msec"
        start = self.tab_view.get_empty_rect().move(SETTINGS.Appearance.summary_padding, SETTINGS.Appearance.summary_padding)
        show_variable("Hits", hits_ratio, start.move(0, gap))
        show_variable("Accuracy", f"{self.scoreCounter.get_accuracy()}%", start)
        show_variable("Time", f"{self.scoreCounter.get_time()} s", start.move(0, gap*2))
        show_variable("M. response", response_time, start.move(0, gap*3))
        self.show_main_buttons()

    def show_graph(self):
        self.tab_view.draw()
        results_to_graph = history.get_selected_results(self.previous_game_mode, self.current_graph_type)
        if len(results_to_graph) > 1:
            if not self.previous_button:
                previous_button_pos = self.tab_view.get_empty_rect().move(SETTINGS.Appearance.summary_padding, SETTINGS.Appearance.summary_padding)
                previous_button_rect = self.font.get_rect("<", size=self.font_size) 
                previous_button_rect.topleft = previous_button_pos.topleft
                self.previous_button = Button(self.screen, self.font, "<", SETTINGS.Appearance.summary_color, self.buttons_padding, SETTINGS.Appearance.summary_color, 5, previous_button_rect)
                self.previous_button.set_callback(self.previous_graph)
                self.buttons.append(self.previous_button)

            if not self.next_button:
                next_button_pos = self.tab_view.get_empty_rect().move(self.tab_view.get_empty_rect().width-SETTINGS.Appearance.summary_padding, SETTINGS.Appearance.summary_padding)
                next_button_rect = self.font.get_rect(">", size=self.font_size) 
                next_button_rect.topright = next_button_pos.topleft
                self.next_button = Button(self.screen, self.font, ">", SETTINGS.Appearance.summary_color, self.buttons_padding, SETTINGS.Appearance.summary_color, 5, next_button_rect)
                self.next_button.set_callback(self.next_graph)
                self.buttons.append(self.next_button)
            
            # draw buttons
            self.next_button.draw()
            self.previous_button.draw()

            # draw graph
            graph = Graph(self.screen, SETTINGS.Appearance.summary_color, SETTINGS.Appearance.graph_fontsize, results_to_graph, (0, 0, 300, 300), draw_text_on_y_axis=True)
            graph.center = self.tab_view.get_empty_rect().center
            graph.draw()

            # draw graph title
            title_rect = self.font.get_rect(self.current_graph_type, size=self.font_size)
            title_rect.center = self.tab_view.get_empty_rect().center
            title_rect.y = self.next_button.text_rect.y # align graph title height to buttons text
            self.font.render_to(self.screen, title_rect, self.current_graph_type, SETTINGS.Appearance.summary_color)
        else:
            text = f"Not enough data for graph"
            text_rect = self.font.get_rect(text, size=self.font_size)
            text_rect.center = self.tab_view.get_empty_rect().center
            self.font.render_to(self.screen, text_rect, text, SETTINGS.Appearance.summary_color)
        self.show_main_buttons()
    
    def next_graph(self):
        next_graph_type_index = (self.result_types.index(self.current_graph_type) + 1) % len(self.result_types)
        self.current_graph_type = self.result_types[next_graph_type_index]
        self.show_graph()

    def previous_graph(self):
        next_graph_type_index = (self.result_types.index(self.current_graph_type) - 1) % len(self.result_types)
        self.current_graph_type = self.result_types[next_graph_type_index]
        self.show_graph()


class Settings(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.buttons = []
        self.font_size = SETTINGS.Appearance.settings_fontsize
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
        self.slider_font_size = SETTINGS.Appearance.slider_fontsize
        self.buttons_font_size = SETTINGS.Appearance.settings_buttons_fontsize
        self.buttons_padding = SETTINGS.Appearance.buttons_padding
        self.return_button = None
        self.sliders = []

    def load(self):
        # prepare
        self.screen.fill(SETTINGS.Appearance.summary_bg_color)
        
        # create TabView
        self.tab_view = TabView(self.screen,
                             SETTINGS.Appearance.tab_view_bg_color, 
                             SETTINGS.Appearance.tab_selected_color,
                             SETTINGS.Appearance.tab_font_color, 
                             SETTINGS.Appearance.tab_fontsize, 
                             ["Arcade", "SpeedyFingers", "AWP"], [self.show_settings]*3, 10, (0, 0, 600, 500))
        self.tab_view.center = self.screen.get_rect().center
        self.tab_view.draw()
        self.buttons.extend(self.tab_view.tab_buttons)

        # show stats
        self.show_settings()

    def show_main_buttons(self):
        midbottom = self.tab_view.midbottom 
        button_font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.buttons_font_size)
        if not self.return_button:
            return_rect = self.font.get_rect("Return", size=self.buttons_font_size) 
            return_rect.center = midbottom
            return_rect.move_ip(0, -self.buttons_font_size)
            self.return_button = Button(self.screen, button_font, "Return", SETTINGS.Appearance.summary_color, self.buttons_padding, SETTINGS.Appearance.summary_color, 5, return_rect)
            self.return_button.set_callback(self.game.change_game_mode, "Lobby")
            self.buttons.append(self.return_button)
        self.return_button.draw()

    def show_settings(self):
        def show_variable(text, current_value, min_value, max_value, pos):
            var_text = f"{text}: {current_value}"
            text_rect = self.font.get_rect(var_text, size=self.font_size) 
            text_rect.center = pos
            self.font.render_to(self.screen, text_rect, var_text, SETTINGS.Appearance.summary_color)
            slider_font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.slider_font_size)
            slider = Slider(self.screen, SETTINGS.Appearance.tab_view_bg_color, 
                            slider_font, SETTINGS.Appearance.summary_color, 
                            self.slider_font_size, SETTINGS.Appearance.summary_color, 
                            min_value, max_value, current_value, 5, 5, 
                            SETTINGS.Appearance.background_color, 
                            (0, 0), (150, 20))
            slider.center = (pos[0], pos[1]+self.font_size*1.5)
            slider.set_call_on_change(self.change_setting, setting_name)
            slider.draw()
            self.sliders.append(slider)

        gap = self.font_size * 4
        current_pos = self.tab_view.get_empty_rect().midtop
        current_pos = (current_pos[0], current_pos[1]-gap//2)
        selected_game_mode = self.tab_view.selected_tab
        for setting_name, value in vars(getattr(SETTINGS, selected_game_mode)).items():
            min_value = SETTINGS.TargetLimits[setting_name][0]
            max_value = SETTINGS.TargetLimits[setting_name][1]
            current_pos = (current_pos[0], current_pos[1]+gap)
            show_variable(setting_name, value, min_value, max_value, current_pos)
        
        self.show_main_buttons()
    
    def change_setting(self, value, setting_name):
        game_mode_settings = getattr(SETTINGS, self.tab_view.selected_tab)
        setattr(game_mode_settings, setting_name, value) # how to show updated value?
        game_mode_settings.save_settings()

    def frame(self):
        super().frame()
        for slider in self.sliders:
            slider.check_slider()


class Arcade(ShootingMode):
    def __init__(self, screen, game):
        super().__init__(screen, game)

    def load(self):
        pygame.time.set_timer(self.game.events["ADD_TARGET"], 0)
        pygame.time.set_timer(self.game.events["ADD_TARGET"], int(1000/SETTINGS.Arcade.spawn_rate))
        self.add_target()

    def frame(self):
        self.screen.fill(SETTINGS.Appearance.background_color)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for target in self.targets:
                    if target.mouse_collides(pygame.mouse.get_pos()):
                        hit_sound.play()
                        self.scoreCounter.add_hit()
                        self.targets_to_delete.append(target)
                        break
                else:
                    miss_sound.play()
                self.scoreCounter.add_shoot()
            elif event.type == self.game.events["ADD_TARGET"]:
                self.add_target()
                
        # update targets size and draw
        for target in self.targets:
            if target.update(self.game.clock.get_time()) == False:
                self.targets_to_delete.append(target)

        # delete unused targets
        while len(self.targets_to_delete) > 0:
            try:
                self.targets.remove(self.targets_to_delete.pop())
                self.scoreCounter.add_target()
            except ValueError: # probably double clicked faster than delta time
                pass
        
        # update counter
        self.scoreCounter.update()
    
    def add_target(self):
        new_target = Target(self.screen, **SETTINGS.Arcade.get_target_settings(), forbidden_rects=self.get_occupied_rects())
        self.targets.append(new_target)


class SpeedyFingers(ShootingMode):
    def __init__(self, screen, game):
        super().__init__(screen, game)

    def load(self):
        for i in range(SETTINGS.SpeedyFingers.targets_amount):
            self.add_target()

    def frame(self):
        self.screen.fill(SETTINGS.Appearance.background_color)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scoreCounter.add_shoot()
                for target in self.targets:
                    if target.mouse_collides(pygame.mouse.get_pos()):
                        hit_sound.play()
                        self.scoreCounter.add_hit()
                        self.scoreCounter.add_target()
                        self.targets_to_delete.append(target)
                        pygame.event.post(pygame.event.Event(self.game.events["ADD_TARGET"]))
                        break
                else:
                    miss_sound.play()
            elif event.type == self.game.events["ADD_TARGET"]:
                self.add_target()

        # draw targets
        for target in self.targets:
            target.draw()
        
        # delete unused targets
        while len(self.targets_to_delete) > 0:
            try:
                self.targets.remove(self.targets_to_delete.pop())
            except ValueError: # probably double clicked faster than delta time
                pass 
        
        # update counter
        self.scoreCounter.update()

    def add_target(self):
        new_target = Target(self.screen, **SETTINGS.SpeedyFingers.get_target_settings(), forbidden_rects=self.get_occupied_rects())
        self.targets.append(new_target)


class AWP(ShootingMode):
    def __init__(self, screen, game):
        super().__init__(screen, game)

    def load(self):
        self.add_target()

    def frame(self):
        self.screen.fill(SETTINGS.Appearance.background_color)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.scoreCounter.add_shoot()
                for target in self.targets:
                    if target.mouse_collides(pygame.mouse.get_pos()):
                        hit_sound.play()
                        self.scoreCounter.add_hit()
                        self.scoreCounter.add_target()
                        self.targets_to_delete.append(target)
                        pygame.event.post(pygame.event.Event(self.game.events["ADD_TARGET"]))
                        break
                else:
                    miss_sound.play()
            elif event.type == self.game.events["ADD_TARGET"]:
                self.add_target()

        # draw targets
        for target in self.targets:
            target.draw()
        
        # delete unused targets
        while len(self.targets_to_delete) > 0:
            try:
                self.targets.remove(self.targets_to_delete.pop())
            except ValueError: # probably double clicked faster than delta time
                pass 
        
        # update counter
        self.scoreCounter.update()

    def add_target(self):
        new_target = Target(self.screen, **SETTINGS.AWP.get_target_settings())
        self.targets.append(new_target) 


# TO INSPECT:
# - still something is bad about respawn in arcade mode
# - sometimes challenge mode time is bad (ends too fast) probably due to exiting from challenge mode earlier
# - target spawn rate can be accidentally set when entering Settings tab (mouse click is passed to newly created sliders)