import pygame
import random
import history
from config import SETTINGS
from components import Button, Switch, Graph, TabView
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
    def __init__(self, screen, grow=False, max_radius=50, outline_margin=4, forbidden_rects=[]):
        self.radius = 0
        self.screen = screen
        self.forbidden_rects = forbidden_rects
        self.max_radius = max_radius
        self.grow = grow
        self.outline_margin = outline_margin
        self.pos = self.get_allowed_pos()
        self.reached_max = False
        if not grow:
            self.radius = self.max_radius
    
    def update(self):
        if self.grow:
            if self.radius < self.max_radius and not self.reached_max:
                self.radius += 1
            else:
                self.reached_max = True
                self.radius -= 1
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
                    button.check_click(pygame.mouse.get_pos())


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
        history.add_results(type(self).__name__, results)


class Lobby(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.buttons = []

    def load(self):
        self.screen.fill(SETTINGS.Appearance.lobby_bg_color)
        gamemodes = ["Arcade", "Speedy fingers", "AWP"]
        # prepare variables for text
        font = pygame.freetype.Font(SETTINGS.Appearance.default_font, SETTINGS.Appearance.lobby_fontsize)
        gap = SETTINGS.Appearance.lobby_fontsize * 1.3
        center = self.screen.get_rect().center
        start = (center[0], center[1] - (len(gamemodes) * gap)/2)
        # find biggest rect to function as background rect
        biggest_rect = font.get_rect(max(gamemodes, key=len), size=SETTINGS.Appearance.lobby_fontsize)
        for i, gamemode in enumerate(gamemodes):
            # fit text rect
            text_rect = font.get_rect(gamemode, size=SETTINGS.Appearance.lobby_fontsize) 
            text_rect.center = (start[0], start[1] + gap * i)
        
            # prepare background for text
            background_rect = pygame.Rect(start[0] - biggest_rect.w/2, text_rect.y, biggest_rect.w, biggest_rect.h)
            background_rect = background_rect.inflate(15, 15) # make some space around
            
            # create and render button  
            button = Button(self.screen, font, gamemode, SETTINGS.Appearance.lobby_color, text_rect, outline_color=SETTINGS.Appearance.lobby_color, outline_radius=5, custom_outline_rect=background_rect)
        
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
        self.previous_game_mode = game.game_mode
        self.buttons = []

    def load(self):
        # prepare
        self.screen.fill(SETTINGS.Appearance.summary_bg_color)
        font = pygame.freetype.Font(SETTINGS.Appearance.default_font, SETTINGS.Appearance.summary_fontsize)

        # create TabView
        tabView = TabView(self.screen,
                             SETTINGS.Appearance.tab_view_bg_color, 
                             SETTINGS.Appearance.tab_selected_color,
                             SETTINGS.Appearance.tab_font_color, 
                             SETTINGS.Appearance.tab_fontsize, 
                             ["Results", "Graphs"], [self.show_results, self.add_graph], 10, (0, 0, 600, 500))
        tabView.center = self.screen.get_rect().center
        tabView.draw()
        self.buttons.extend(tabView.tab_buttons)

        # create buttons
        midbottom = self.screen.get_rect().midbottom 
        button_padding = 15
        play_rect = font.get_rect("Play again", size=SETTINGS.Appearance.summary_fontsize) 
        play_rect.midright = midbottom
        play_rect.move_ip(-button_padding, -SETTINGS.Appearance.summary_fontsize) # to give some space between buttons
        play_button = Button(self.screen, font, "Play again", SETTINGS.Appearance.summary_color, play_rect, button_padding, SETTINGS.Appearance.summary_color, 5)
        
        return_rect = font.get_rect("Return", size=SETTINGS.Appearance.summary_fontsize) 
        return_rect.midleft = midbottom
        return_rect.move_ip(button_padding, -SETTINGS.Appearance.summary_fontsize)
        return_button = Button(self.screen, font, "Return", SETTINGS.Appearance.summary_color, return_rect, button_padding, SETTINGS.Appearance.summary_color, 5)

        # show stats
        self.show_results()

        # set up callbacks
        play_button.set_callback(self.game.change_game_mode, self.previous_game_mode)
        return_button.set_callback(self.game.change_game_mode, "Lobby")
        self.buttons.extend([play_button, return_button])

    def show_results(self):
        def show_variable(text, var, pos):
            var_text = f"{text}: {var}"
            text_rect = font.get_rect(var_text, size=SETTINGS.Appearance.summary_fontsize) 
            text_rect.topleft = pos.topleft
            font.render_to(self.screen, text_rect, var_text, SETTINGS.Appearance.summary_color)

        font = pygame.freetype.Font(SETTINGS.Appearance.default_font, SETTINGS.Appearance.summary_fontsize)
        gap = SETTINGS.Appearance.summary_fontsize * 1.5
        hits_ratio = f"{self.scoreCounter.get_hits()}/{self.scoreCounter.get_all_targets()}"
        response_time = f"{int(self.scoreCounter.get_median_reaction_time()*1000)} msec"
        start = pygame.Rect(200, 150, 1, 1)
        show_variable("Hits", hits_ratio, start.move(0, gap))
        show_variable("Accuracy", f"{self.scoreCounter.get_accuracy()}%", start)
        show_variable("Time", f"{self.scoreCounter.get_time()} s", start.move(0, gap*2))
        show_variable("M. response", response_time, start.move(0, gap*3))

    def add_graph(self, result_type="Hits"): # DELETE HITS
        results_to_graph = history.get_selected_results(self.previous_game_mode, result_type)
        graph = Graph(self.screen, SETTINGS.Appearance.summary_color, SETTINGS.Appearance.graph_fontsize, results_to_graph, (0, 0, 300, 300))
        graph.center = self.screen.get_rect().center
        graph.draw() 


class Arcade(ShootingMode):
    def __init__(self, screen, game):
        super().__init__(screen, game)

    def load(self):
        pygame.time.set_timer(self.game.events["ADD_TARGET"], 0)
        pygame.time.set_timer(self.game.events["ADD_TARGET"], int(1000/self.game.TARGET_SPAWNRATE))
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
            if target.update() == False:
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
        new_target = Target(self.screen, **SETTINGS.Arcade.target_settings, forbidden_rects=self.get_occupied_rects())
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
        new_target = Target(self.screen, **SETTINGS.SpeedyFingers.target_settings, forbidden_rects=self.get_occupied_rects())
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
        new_target = Target(self.screen, **SETTINGS.AWP.target_settings)
        self.targets.append(new_target)