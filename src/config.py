class AWPSettings():
    def __init__(self):
        self.target_settings = {"max_radius": 10, "grow": False, "outline_margin": 2}

class ArcadeSettings():
    def __init__(self):
        self.target_settings = {"max_radius": 50, "grow": True, "outline_margin": 4}

class SpeedyFingersSettings():
    def __init__(self):
        self.target_settings = {"max_radius": 50, "grow": False, "outline_margin": 4}
        self.targets_amount = 5

class Appearance():
    def __init__(self):
        self.default_font = "src/fonts/no_continue.ttf"
        self.background_color = (222, 222, 222)
        self.outline_color = (0, 0, 0) 
        self.filling_color = (255, 255, 255)
        self.score_color = (74, 74, 74)
        self.lobby_bg_color = self.background_color
        self.lobby_color = self.score_color
        self.lobby_fontsize = 40
        self.summary_bg_color = self.background_color
        self.summary_color = self.score_color
        self.summary_fontsize = 30
        self.summary_padding = 40
        self.switch_filling_color = (195, 195, 195)
        self.switch_toggle_outline = (125, 125, 125)
        self.graph_fontsize = 10
        self.tab_view_bg_color = (195, 195, 195) 
        self.tab_selected_color = (165, 165, 165)
        self.tab_font_color = self.score_color
        self.tab_fontsize = 25

class AllSettings():
    def __init__(self):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.CHALLENGE_TIME = 30*1000 # 30 seconds
        self.AWP = AWPSettings()
        self.Arcade = ArcadeSettings()
        self.SpeedyFingers = SpeedyFingersSettings()
        self.Appearance = Appearance()


SETTINGS = AllSettings()