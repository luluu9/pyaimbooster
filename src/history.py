import pathlib
import json
import time

# STATS STRUCTURE
# {
#   GAMEMODE:
#   {
#       DATE:
#       {
#           STATS...      
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

results = read_history()
