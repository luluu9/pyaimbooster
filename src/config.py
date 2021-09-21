TargetLimits = {
               "max_radius": [1, 100],
               "grow": [0, 1],
               "outline_margin": [0, 10],
               "targets_amount": [1, 25],
               "spawn_rate": [1, 10],
               "duration": [1, 5]
               } 

class TargetSettings():
    def get_target_setting(self, attr_name):
        try:
            return getattr(self, attr_name)
        except AttributeError:
            return None

    def get_target_settings(self):
        target_settings_names = ["max_radius", "grow", "outline_margin"]
        target_settings = {name:self.get_target_setting(name) for name in target_settings_names if self.get_target_setting(name) != None}
        return target_settings

    def load_saved_settings(self):
        import pathlib, json
        settings_name_to_load = self.__class__.__name__
        file_path = pathlib.Path.home() / "pyaimbooster.settings"
        settings_to_load = {}
        with file_path.open("r", encoding="utf-8") as settings:
            for line in settings:
                if line.startswith(settings_name_to_load):
                    settings_to_load_str = line.split(maxsplit=1)[1]
                    settings_to_load = json.loads(settings_to_load_str)
                    break
        for name, setting in settings_to_load.items():
            if hasattr(self, name):
                setattr(self, name, setting)

    def save_settings(self):
        import pathlib, json
        settings_to_write = (json.dumps(self.__dict__))
        settings_name_to_write = self.__class__.__name__
        file_path = pathlib.Path.home() / "pyaimbooster.settings"
        file_path.touch(exist_ok=True)
        all_settings = {}
        with file_path.open("r", encoding="utf-8") as old_settings:
            for line in old_settings:
                settings_name, settings = line.strip().split(maxsplit=1)
                all_settings[settings_name] = settings
        all_settings[settings_name_to_write] = settings_to_write
        with file_path.open("w", encoding="utf-8") as new_settings:
            for settings_name, settings in all_settings.items():
                new_settings.write(settings_name + " " + settings_to_write + "\n")

class AWPSettings(TargetSettings):
    def __init__(self):
        self.max_radius = 10
        self.grow = 0
        self.outline_margin = 2
        self.load_saved_settings()

class ArcadeSettings(TargetSettings):
    def __init__(self):
        self.max_radius = 50
        self.grow = 1 # 1 == True
        self.outline_margin = 4
        self.spawn_rate = 3 # targets per second 
        self.duration = 2
        self.load_saved_settings()

class SpeedyFingersSettings(TargetSettings):
    def __init__(self):
        self.max_radius = 50
        self.grow = 0
        self.outline_margin = 4
        self.targets_amount = 5
        self.load_saved_settings()

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
        self.graph_fontsize = 15
        self.tab_view_bg_color = (195, 195, 195) 
        self.tab_selected_color = (165, 165, 165)
        self.tab_font_color = self.score_color
        self.tab_fontsize = 25
        self.buttons_padding = [15, 15]
        self.settings_fontsize = 20
        self.settings_buttons_fontsize = self.summary_fontsize
        self.slider_fontsize = 15

class AllSettings():
    def __init__(self):
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FPS = 144
        self.CHALLENGE_TIME = 30*1000 # 30 seconds
        self.AWP = AWPSettings()
        self.Arcade = ArcadeSettings()
        self.SpeedyFingers = SpeedyFingersSettings()
        self.Appearance = Appearance()
        self.TargetLimits = TargetLimits


SETTINGS = AllSettings()