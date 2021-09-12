import pygame
import pygame.freetype
import time
import gamemodes
from pygame.constants import USEREVENT
from config import SETTINGS

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_s,
    K_r,
    K_ESCAPE
)


class ScoreCounter():
    def __init__(self):
        self.hits = 0
        self.all_targets = 0
        self.font_size = 30
        self.font = pygame.freetype.Font(SETTINGS.Appearance.default_font, self.font_size)
        self.shoots = 0
        self.start_time = time.time()
        self.end_time = None
        self.last_hit_time = None
        self.reaction_times = []
    
    def update(self):
        text = f"{self.hits}/{self.all_targets}"
        text_rect = self.font.get_rect(text, size=30) 
        text_rect.midtop = screen.get_rect().midtop
        self.font.render_to(screen, text_rect, text, SETTINGS.Appearance.score_color)

    def add_hit(self):
        self.hits += 1
        if self.last_hit_time:
            reaction = time.time()-self.last_hit_time
            self.reaction_times.append(reaction) 
        self.last_hit_time = time.time()
    
    def add_target(self):
        self.all_targets += 1

    def add_shoot(self):
        self.shoots += 1
    
    # return how much time current round takes
    def get_time(self):
        if not self.end_time:
            self.end_time = time.time()
        return round(self.end_time - self.start_time, 2)
    
    def get_accuracy(self):
        if self.shoots > 0:
            return round(self.hits*100/self.shoots, 2)
        else:
            return 0.0
    
    def get_hits(self):
        return self.hits
    
    def get_all_targets(self):
        return self.all_targets
    
    def get_median_reaction_time(self):
        def median(data):
            if len(data) == 0: return 0
            data.sort()
            mid = len(data) // 2
            return (data[mid] + data[~mid]) / 2

        return median(self.reaction_times)


class Game():
    def __init__(self):
        self.events = {}
        self.challenge = False
        self.change_game_mode("Lobby")

    def change_game_mode(self, game_mode):
        if game_mode == "Lobby":
            self.game_mode_obj = gamemodes.Lobby(screen, self)
        elif game_mode == "Settings":
            self.game_mode_obj = gamemodes.Settings(screen, self)
        elif game_mode == "Summary":
            self.game_mode_obj = gamemodes.Summary(screen, self)
        elif game_mode == "Arcade":
            self.game_mode_obj = gamemodes.Arcade(screen, self)
        elif game_mode == "Speedy fingers":
            self.game_mode_obj = gamemodes.SpeedyFingers(screen, self)
        elif game_mode == "AWP":
            self.game_mode_obj = gamemodes.AWP(screen, self)
        else:
            raise Exception("There is no provided game mode: " + str(game_mode))
        self.game_mode_obj.load()
        self.game_mode = game_mode
    
    def set_challenge(self, is_challenge):
        self.challenge = is_challenge
    
    def reset(self):
        for event in self.events.values():
            pygame.time.set_timer(event, 0)
        self.scoreCounter = ScoreCounter()
    
    def frame(self):
        self.game_mode_obj.frame()


# PYGAME INIT
pygame.init()
screen = pygame.display.set_mode((SETTINGS.SCREEN_WIDTH, SETTINGS.SCREEN_HEIGHT))
clock = pygame.time.Clock()

# LOAD GAME
game = Game()

# GAME EVENTS
game.events["ADD_TARGET"] = USEREVENT + 1
game.events["END_CHALLENGE"] = USEREVENT + 2

# GAME MECHANICS
game.TARGET_SPAWNRATE = 3 # targets per second 

# MAINLOOP
running = True
while running:
    pygame.display.set_caption("FPS: " + str(int(clock.get_fps())))
    for event in pygame.event.get((QUIT, KEYDOWN, game.events["END_CHALLENGE"])):
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            # Go to summary
            if event.key == K_s or event.key == K_ESCAPE and game.game_mode != "Lobby":
                # continue to prevent updating screen with targets after summary shows up
                if game.game_mode != "Summary": # to prevent looping in summary
                    game.change_game_mode("Summary")
                    continue
            # Restart
            elif event.key == K_r:
                game.change_game_mode(game.game_mode)
                continue
        elif event.type == game.events["END_CHALLENGE"]:
            if game.game_mode != "Summary": # to prevent reloading summary
                try:
                    game.game_mode_obj.save_results()
                except AttributeError:
                    pass # save results method not implemented
                game.change_game_mode("Summary")
    game.frame()
    # refresh display
    pygame.display.update()
    clock.tick(SETTINGS.FPS)
pygame.quit()


# todo:
# - add training modes