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

class AllSettings():
    def __init__(self):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 60
        self.AWP = AWPSettings()
        self.Arcade = ArcadeSettings()
        self.SpeedyFingers = SpeedyFingersSettings()

SETTINGS = AllSettings()