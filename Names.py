import random
import msvcrt
import json
import os
VOTES_FILE = "votes.json"
WINS_FILE = "wins.json"
try:
    with open(VOTES_FILE, "r") as f:
        try:
            overallVotes = json.load(f)
            nameVotes = overallVotes["votes"]
        except json.JSONDecodeError:
            nameVotes = [0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0]
            overallVotes = {"votes": nameVotes}
except FileNotFoundError:
    nameVotes = [0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0]
    overallVotes = {"votes": nameVotes}

try:
    with open(WINS_FILE, "r") as f:
        record = json.load(f)

    # Fallbacks if keys are missing
    winCount = record.get("wins", [0] * 30)
    lossCount = record.get("losses", [0] * 30)
    tieCount = record.get("ties", [0] * 30)

    # Rebuild record with all keys, so it's consistent
    record = {
        "wins": winCount,
        "losses": lossCount,
        "ties": tieCount
    }
except (json.JSONDecodeError, FileNotFoundError):
    winCount = [0] * 30
    lossCount = [0] * 30
    tieCount = [0] * 30
    record = {
        "wins": winCount,
        "losses": lossCount,
        "ties": tieCount
    }

names = ["Moe", "Larry", "Gary", "Finn", "Copper", "Steverino",
         "Rizzo", "Ozzy", "Pickle Rick", "Caesar", "Loki", "Luigi",
         "Timber", "Cocoa Bear", "Beretta", "Winchester", "Decoy", "Nemo",
         "Rio", "Bucky", "Dust", "Perch", "Chopper", "Freddie",
         "Fudge", "Noodle", "Rico", "Butter", "Pappy", "Korn"]
names_ordered= []
roundOne = []

def nameSelector(y, z):
    x = random.randint(0, len(y)-1)
    a = y.pop(x)
    z.append(a)

    return z

def randomizer(i = 0):
    while i < 30:
        nameSelector(names, names_ordered)
        i += 1

def selector(j = 0, k = 0):
    while j < 30:
        nameSelector(names_ordered, roundOne)
        j += 1
    while k < 15:
        print(f"1.{k+1}: {roundOne[k]} vs {roundOne[k+15]}")
        k += 1

def add_votes(name, names_ordered):
    try:
        index = names_ordered.index(name)
        nameVotes[index] += 1

        with open(VOTES_FILE, "w") as f:
            json.dump({"votes": nameVotes}, f, indent=4)
    except ValueError:
        print(f"Name {name} not found in names_ordered list.")

def add_win(name, names_ordered):
    global winCount, lossCount, tieCount
    try:
        index = names_ordered.index(name)
        winCount[index] += 1

        with open(WINS_FILE, "w") as f:
            json.dump({"wins": winCount,
                       "losses": lossCount,
                       "ties": tieCount}, f, indent=4)
    except ValueError:
        print(f"Name {name} not found in names_ordered list.")

def add_loss(name, names_ordered):
    global winCount, lossCount, tieCount
    try:
        index = names_ordered.index(name)
        lossCount[index] += 1

        with open(WINS_FILE, "w") as f:
            json.dump({"wins": winCount,
                "losses": lossCount,
                "ties": tieCount}, f, indent=4)
    except ValueError:
        print(f"Name {name} not found in names_ordered list.")

def reset_all_stats():
    #"""Resets all wins, losses, ties, and total votes to zero and updates files."""
    global nameVotes, winCount, lossCount, tieCount
    num_names = len(names)

    # 1. Reset Votes and CLOSE THE FILE
    nameVotes = [0] * num_names
    # Use 'with open' for proper file management
    with open(VOTES_FILE, "w") as f: 
        json.dump({"votes": nameVotes}, f, indent=4) # File closes automatically here

    # 2. Reset Wins/Losses/Ties and CLOSE THE FILE
    winCount = [0] * num_names
    lossCount = [0] * num_names
    tieCount = [0] * num_names
    record = {
        "wins": winCount,
        "losses": lossCount,
        "ties": tieCount
    }
    # Use 'with open' for proper file management
    with open(WINS_FILE, "w") as f:
        json.dump(record, f, indent=4) # File closes automatically here
    
    print("All tournament stats (Wins, Losses, Votes) have been reset and files closed.")