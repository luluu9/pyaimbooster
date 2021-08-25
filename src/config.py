class AWPSettings():
    def __init__(self):
        self.target_settings = {"start_max": True, "max_radius": 10}

class AllSettings():
    def __init__(self):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.AWP = AWPSettings()

SETTINGS = AllSettings()