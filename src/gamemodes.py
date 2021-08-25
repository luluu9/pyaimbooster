import pygame
from components import Button
from appearance import (lobby_bg_color, lobby_color, lobby_fontsize, default_font,
                       summary_bg_color, summary_color, summary_fontsize,
                       background_color,)

# BLUEPRINT:
# class GameMode():
#     def __init__(self, screen):
#         self.screen = screen

#     def load():
#         pass

#     def frame():
#         pass

class StaticButtons():
    def frame(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.check_click(pygame.mouse.get_pos())


class Lobby(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.buttons = []

    def load(self):
        self.screen.fill(lobby_bg_color)
        gamemodes = ["Arcade", "Speedy fingers", "XXX"]
        # prepare variables for text
        font = pygame.freetype.Font(default_font, lobby_fontsize)
        gap = lobby_fontsize * 1.3
        center = self.screen.get_rect().center
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
            button = Button(self.screen, font, gamemode, lobby_color, text_rect, outline_color=lobby_color, outline_radius=5, custom_outline_rect=background_rect)
        
            # set callbacks to change game mode
            if gamemode == "Arcade":
                button.set_callback(self.game.change_game_mode, "Arcade")
            elif gamemode == "Speedy fingers":
                button.set_callback(self.game.change_game_mode, "Speedy fingers")
            else: 
                button.set_callback(self.game.change_game_mode, "Lobby") # placeholder
            self.buttons.append(button)


class Summary(StaticButtons):
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.scoreCounter = game.scoreCounter
        self.previous_game_mode = game.game_mode
        self.buttons = []

    def load(self):
        def show_variable(text, var, pos):
            var_text = f"{text}: {var}"
            text_rect = font.get_rect(var_text, size=summary_fontsize) 
            text_rect.topleft = pos.topleft
            font.render_to(self.screen, text_rect, var_text, summary_color)

        # prepare
        self.screen.fill(summary_bg_color)
        font = pygame.freetype.Font(default_font, summary_fontsize)
        gap = summary_fontsize * 1.5
        hits_ratio = f"{self.scoreCounter.get_hits()}/{self.scoreCounter.get_all_targets()}"
        response_time = f"{int(self.scoreCounter.get_median_reaction_time()*1000)} msec"

        # create buttons
        midbottom = self.screen.get_rect().midbottom 
        button_padding = 15
        play_rect = font.get_rect("Play again", size=summary_fontsize) 
        play_rect.midright = midbottom
        play_rect.move_ip(-button_padding, -summary_fontsize) # to give some space between buttons
        play_button = Button(self.screen, font, "Play again", summary_color, play_rect, button_padding, summary_color, 5)
        
        return_rect = font.get_rect("Return", size=summary_fontsize) 
        return_rect.midleft = midbottom
        return_rect.move_ip(button_padding, -summary_fontsize)
        return_button = Button(self.screen, font, "Return", summary_color, return_rect, button_padding, summary_color, 5)

        # show stats
        start = pygame.Rect(play_rect.x, 150, 1, 1)
        show_variable("Hits", hits_ratio, start.move(0, gap))
        show_variable("Accuracy", f"{self.scoreCounter.get_accuracy()}%", start)
        show_variable("Time", f"{self.scoreCounter.get_time()} s", start.move(0, gap*2))
        show_variable("M. response", response_time, start.move(0, gap*3))

        # set up callbacks
        play_button.set_callback(self.game.change_game_mode, self.previous_game_mode)
        return_button.set_callback(self.game.change_game_mode, "Lobby")
        self.buttons = (play_button, return_button)



