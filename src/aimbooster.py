import pygame
import pygame.freetype
import random
import time
from pygame.constants import USEREVENT

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_s,
    K_r
)


class ScoreCounter():
    def __init__(self):
        self.hits = 0
        self.all_targets = 0
        self.font_size = 30
        self.font = pygame.freetype.Font(default_font, self.font_size)
        self.shoots = 0
        self.start_time = time.time()
    
    def update(self):
        text = f"{self.hits}/{self.all_targets}"
        text_rect = self.font.get_rect(text, size=30) 
        text_rect.midtop = screen.get_rect().midtop
        self.font.render_to(screen, text_rect, text, score_color)

    def add_hit(self):
        self.hits += 1
    
    def add_target(self):
        self.all_targets += 1

    def add_shoot(self):
        self.shoots += 1
    
    # return how much time current round takes
    def get_time(self):
        return round(time.time() - self.start_time, 2)
    
    def get_accuracy(self):
        if self.shoots > 0:
            return round(self.hits*100/self.shoots, 2)
        else:
            return 0.0
    
    def get_hits(self):
        return self.hits
    
    def get_all_targets(self):
        return self.all_targets
    

class Target():
    def __init__(self):
        self.max_radius = 50
        self.reached_max = False
        self.pos = self.get_random_pos(self.max_radius)
        self.radius = 0
        self.outline_margin = 4

    def update(self):
        if self.radius < self.max_radius and not self.reached_max:
            self.radius += 1
        else:
            self.reached_max = True
            self.radius -= 1
            # destroy this object if smaller than 1px
            if self.radius <= 0:
                return False 
        # draw outline
        pygame.draw.circle(screen, outline_color, self.pos, self.radius, self.outline_margin)
        # draw filling
        pygame.draw.circle(screen, filling_color, self.pos, self.radius-self.outline_margin)

    def mouse_collides(self, mouse_pos):
        if pow((mouse_pos[0] - self.pos[0]), 2) + pow((mouse_pos[1] - self.pos[1]), 2) <= pow(self.radius, 2):
            return True
    
    def get_random_pos(self, margin=0):
        x = random.randint(margin, SCREEN_WIDTH-margin)
        y = random.randint(margin, SCREEN_HEIGHT-margin)
        return (x, y)


# Button with background
class ButtonWB(): 
    def __init__(self, font, text, text_color, text_rect, background_rect=None, background_color=(0,0,0), border_radius=0):
        if background_rect:
             self.background_rect = pygame.draw.rect(screen, background_color, background_rect, border_radius)
        self.text_rect = font.render_to(screen, text_rect, text, text_color)

    def set_callback(self, callback, *args, **kwargs):
        self.callback = callback
        self.callback_args = args
        self.callback_kwargs = kwargs

    def check_click(self, mouse_pos):
        if self.background_rect:
            if self.background_rect.collidepoint(mouse_pos):
                self.callback(*self.callback_args, **self.callback_kwargs)
        else:
            if self.text_rect.collidepoint(mouse_pos):
                self.callback(*self.callback_args, **self.callback_kwargs)


class Game():
    def __init__(self):
        self.change_game_mode("Lobby")

    def change_game_mode(self, game_mode):
        # reset events
        pygame.time.set_timer(ADD_TARGET, 0)
        if game_mode == "Lobby":
            self._load_lobby()
        elif game_mode == "Summary":
            self._load_summary(previous_game_mode=self.game_mode)
        elif game_mode == "Arcade":
            self._load_arcade()
        else:
            raise Exception("There is no provided game mode: " + str(game_mode))
        self.game_mode = game_mode
    
    def _load_lobby(self):
        screen.fill(lobby_color)
        gamemodes = ["Arcade", "XXX", "XXX"]
        self.lobby_buttons = []
        # prepare variables for text
        font = pygame.freetype.Font("src/fonts/no_continue.ttf", lobby_fontsize)
        gap = lobby_fontsize * 1.3
        center = screen.get_rect().center
        start = (center[0], center[1] - (len(gamemodes) * gap)/2)
        # find biggest rect to function as background rect
        biggest_rect = font.get_rect(max(gamemodes, key=len), size=lobby_fontsize)
        for i, gamemode in enumerate(gamemodes):
            # fit text rect
            text_rect = font.get_rect(gamemode, size=lobby_fontsize) 
            text_rect.center = (start[0], start[1] + gap * i)
        
            # prepare background for text
            background_rect = pygame.Rect(start[0] - biggest_rect.w/2, text_rect.y, biggest_rect.w, biggest_rect.h)
            background_rect = background_rect.inflate(15, 15) # make some space around
            
            # create and render button  
            button = ButtonWB(font, gamemode, score_color, text_rect, background_rect, background_color, 5)
           
            # set callbacks to change game mode
            if gamemode == "Arcade":
                button.set_callback(self.change_game_mode, "Arcade")
            else: 
                button.set_callback(self.change_game_mode, "Lobby") # placeholder
            self.lobby_buttons.append(button)
    
    def _load_summary(self, previous_game_mode):
        def show_variable(text, var, pos):
            var_text = f"{text}: {var}"
            text_rect = font.get_rect(var_text, size=summary_fontsize) 
            text_rect.topleft = pos.topleft
            font.render_to(screen, text_rect, var_text, summary_color)

        # prepare
        screen.fill(lobby_color)
        font = pygame.freetype.Font(default_font, summary_fontsize)
        gap = summary_fontsize * 1.5
        hits_ratio = f"{self.scoreCounter.get_hits()}/{self.scoreCounter.get_all_targets()}" 

        # create buttons
        midbottom = screen.get_rect().midbottom 
        button_padding = 15
        play_rect = font.get_rect("Play again", size=summary_fontsize) 
        play_rect.midright = midbottom
        play_rect.move_ip(-button_padding, -summary_fontsize) # to give some space between buttons
        play_button = ButtonWB(font, "Play again", summary_color, play_rect, play_rect.inflate(button_padding, button_padding), background_color, 5)
        
        return_rect = font.get_rect("Return", size=summary_fontsize) 
        return_rect.midleft = midbottom
        return_rect.move_ip(button_padding, -summary_fontsize)
        return_button = ButtonWB(font, "Return", summary_color, return_rect, return_rect.inflate(button_padding, button_padding), background_color, 5)

        # show stats
        start = pygame.Rect(play_rect.x, 150, 1, 1)
        show_variable("Hits", hits_ratio, start.move(0, gap))
        show_variable("Accuracy", f"{self.scoreCounter.get_accuracy()}%", start)
        show_variable("Time", f"{self.scoreCounter.get_time()}s", start.move(0, gap*2))

        # set up callbacks
        play_button.set_callback(self.change_game_mode, previous_game_mode)
        return_button.set_callback(self.change_game_mode, "Lobby")
        self.summary_buttons = (play_button, return_button)

    def _load_arcade(self):
        self.scoreCounter = ScoreCounter()
        self.targets = [Target()]
        self.targets_to_delete = []
        pygame.time.set_timer(ADD_TARGET, int(1000/TARGET_SPAWNRATE))

    def frame(self):
        if self.game_mode == "Lobby":
            self._lobby_frame()
        elif self.game_mode == "Summary":
            self._summary_frame()
        elif self.game_mode == "Arcade":
            self._arcade_frame()
    
    def _lobby_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.lobby_buttons:
                    button.check_click(pygame.mouse.get_pos())

    def _summary_frame(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.summary_buttons:
                    button.check_click(pygame.mouse.get_pos())

    def _arcade_frame(self):
        screen.fill(background_color)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for target in self.targets:
                    if target.mouse_collides(pygame.mouse.get_pos()):
                        self.scoreCounter.add_hit()
                        self.scoreCounter.add_target()
                        self.targets_to_delete.append(target)
                self.scoreCounter.add_shoot()
            elif event.type == ADD_TARGET:
                self.targets.append(Target())
                
        # update targets size
        for target in self.targets:
            if target.update() == False:
                self.targets_to_delete.append(target)
                self.scoreCounter.add_target()

        # delete unused targets
        while len(self.targets_to_delete) > 0:
            try:
                self.targets.remove(self.targets_to_delete.pop())
            except ValueError: # probably double clicked faster than delta time
                pass 
        
        # update counter
        self.scoreCounter.update()



# BASE SETTINGS
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# PYGAME INIT
pygame.init()
pygame.display.set_caption('aimbooster v.0.0.2')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# APPEARANCE 
default_font = "src/fonts/no_continue.ttf"
background_color = (222, 222, 222)
outline_color = (0, 0, 0) 
filling_color = (255, 255, 255)
score_color = (74, 74, 74)
lobby_color = (255, 255, 255)
lobby_fontsize = 40
summary_color = (155, 155, 155)
summary_fontsize = 30

# GAME MECHANICS
TARGET_SPAWNRATE = 3 # targets per second 

# GAME EVENTS
ADD_TARGET = USEREVENT + 1

# LOAD GAME
game = Game()

# MAINLOOP
running = True
while running:
    for event in pygame.event.get((QUIT, KEYDOWN)):
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_s:
                # return to prevent updating screen with targets after summary shows up
                game.change_game_mode("Summary")
                continue
            elif event.key == K_r:
                game.change_game_mode(game.game_mode)
                continue
    game.frame()
    # refresh display
    pygame.display.update()
    clock.tick(FPS)
pygame.quit()


# todo
# - add training modes
# - forbid to spawn new target onto other target
# - save stats
# - reset with keybutton (r?)