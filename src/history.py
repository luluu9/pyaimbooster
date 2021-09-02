import pathlib
import json
import time

# RESULTS STRUCTURE
# {
#   GAMEMODE:
#   {
#       DATE:
#       {
#           RESULTS...      
#       }
#   }
#   ...
# }

results = {
}

def read_history():
    file_path = pathlib.Path.home() / "pyaimbooster.stats"
    file_path.touch(exist_ok=True)
    with file_path.open("r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except: # invalid file
            return {}
    return history

def write_history():
    file_path = pathlib.Path.home() / "pyaimbooster.stats"
    file_path.touch(exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

def add_results(gamemode, new_stats):
    if not gamemode in results:
        results[gamemode] = {}
    results[gamemode][str(int(time.time()))] = new_stats
    write_history()

# returns list of tuples which containts time and particular result values
# e.g. for ("AWP", "Hits") returns (("12312425", "40"), ("12315425", "35"))
def get_selected_results(gamemode, type):
    selected_results = []
    if gamemode in results:
        for time, gamemode_results in results[gamemode].items():
            if type in gamemode_results:
                selected_results.append((time, gamemode_results[type]))
    return selected_results


results = read_history()
