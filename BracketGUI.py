#Python GUI How 2: https://www.pythonguis.com/tutorials/create-gui-tkinter/
#Pages Idea: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter

#Blastoise image from: https://www.pokemon.com/us/pokedex/blastoise
#Wartortle image from: https://marriland.com/pokedex/wartortle/
#Squirtle  image from: https://www.pokemon.com/us/pokedex/squirtle

import tkinter as tk
from tkinter import *
from tkinter import font as tkfont
import random
import time
import Names

def setup_names_data(num_names=len(Names.names)):
    names = [f"Name {i+1}" for i in range(num_names)]
    random.shuffle(names)
    data = {name: {'wins': 0, 'losses': 0, 'total_votes': 0} for name in names}

    return names, data

def generate_round_robin_schedule(names):
    if len(names) % 2 != 0:
        raise ValueError("Number of names bust be even for standard round-robin")
    
    n = len(names)
    rounds = []
    fixed_name = names[0]
    rotating_names = names[1:]

    for r in range(n-1):
        current_round_matches = []

        current_round_matches.append((fixed_name, rotating_names[0]))

        for i in range (1, n // 2):
            p1 = rotating_names[i]
            p2 = rotating_names[n - 1 - i]
            current_round_matches.append((p1, p2))

        rounds.append(current_round_matches)

        rotating_names = rotating_names[-1:] + rotating_names[:-1]

    return rounds

class BracketApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.names = Names.names
        self.schedule = generate_round_robin_schedule(self.names)
        self.total_rounds = len(self.schedule)
        self.matches_per_round = len(self.schedule[0])

        self.round_scores = {}

        self.round_progress_file = "round_progress.txt"
        self.current_round = self._load_current_round()

        #GUI Setup
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.match_font = tkfont.Font(family='Helvetica', size=10)
        self.title("Bracket Voting App")
        self.geometry("600x800")
        self.minsize(500,700)
        self.maxsize(700,900)

        #Container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, VotingPage, IntermissionPage, ResultsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
    
    def _load_current_round(self):
        #Loads current round index from file
        try:
            with open(self.round_progress_file, "r") as f:
                round_index = int(f.read().strip())
                return min(round_index, self.total_rounds) #Ensures it doesn't exceed max rounds
        except (FileNotFoundError, ValueError):
            return 0

    def _save_current_round(self):
        #Saves current round index to file
        with open(self.round_progress_file, "w") as f:
            f.write(str(self.current_round))

    def get_current_match_set(self):
        #Returns the list of matches for the current round
        if 0 <= self.current_round < self.total_rounds:
            return self.schedule[self.current_round]
        return []

    def get_match_score(self, name1, name2):
        #Gets or initializes the current score for a specific match. Key is tuple(sorted names)
        key = tuple(sorted((name1, name2)))
        #Score is [votes for key[0], votes for key[1]]
        if key not in self.round_scores:
            self.round_scores[key] = [0, 0]

        #Return scores in the requested order (name1, name2)
        if name1 == key[0]:
            return self.round_scores[key]
        else:
            return [self.round_scores[key][1], self.round_scores[key][0]]

    def vote(self, match_index, vote_for_name_index):
        current_matches = self.get_current_match_set()
        name1, name2 = current_matches[match_index]

        voted_name = name1 if vote_for_name_index == 0 else name2

        #1. Update the match score cache (self.round_scores)
        key = tuple(sorted((name1, name2)))
        key_index = 0 if voted_name == key[0] else 1
        self.round_scores[key][key_index] += 1

        #2. Update the persistent global vote count in Names.py
        Names.add_votes(voted_name, Names.names)

        #3. Check for winner and update W/L if match finished
        self.check_winner(match_index)

        #4. Refresh the GUI
        self.frames["VotingPage"].update_display()

    def check_winner(self, match_index):
        current_matches = self.get_current_match_set()
        name1, name2 = current_matches[match_index]

        votes1, votes2 = self.get_match_score(name1, name2)

        winner = loser = None
        if votes1 + votes2 >= 1:
            if votes1 > votes2:
                winner, loser = name1, name2
            elif votes2 > votes1:
                winner, loser = name2, name1
            else:
                return

        if (votes1 >= 1 or votes2 >= 1) and winner is not None:
            key = tuple(sorted((name1, name2)))
            if len(self.round_scores[key]) == 2:
                Names.add_win(winner, Names.names)
                Names.add_loss(loser, Names.names)

        self.check_round_end()

    def check_round_end(self):
        #Checks if all matches in the current round have been recorded.
        current_matches = self.get_current_match_set()
        finished_matches = 0

        for name1, name2 in current_matches:
            key = tuple(sorted((name1, name2)))
            # Check if the match was marked as finished/recorded in the cache
            if key in self.round_scores and (self.round_scores[key][0] + self.round_scores[key][1]) >= 1:
                finished_matches += 1

        if finished_matches == self.matches_per_round:
            # Round is over, move to next round
            self.current_round += 1
            self._save_current_round() # Persist the new round index
            self.round_scores = {} # Reset match scores for the new round

            if self.current_round < self.total_rounds:
                print(f"*** ROUND {self.current_round + 1} STARTING! ***")
                self.frames["VotingPage"].update_display()
            else:
                print("*** TOURNAMENT FINISHED! ***")
                self.show_frame("ResultsPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        if page_name == "StartPage":
            frame.update_display()
        elif page_name == "VotingPage":
            frame.update_display()
        elif page_name == "ResultsPage":
            frame.update_display()
        elif page_name == "IntermissionPage":
            if hasattr(frame, 'start_timer'):
                frame.start_timer()
                
        frame.tkraise()

    def reset_data(self):
        Names.reset_all_stats()
        self.current_round = 0
        self._save_current_round()
        self.round_scores = {}
        self.show_frame("StartPage")
        print("Application state reset complete. All data zeroed")

# --- START PAGE ---
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        tk.Label(self, text="Hanline Dog Name Bracket 2025", 
                 font=controller.title_font).pack(side="top", fill="x", pady=10)

        # Labels for static info
        tk.Label(self, text=f"Total Participants: {len(controller.names)}").pack()
        tk.Label(self, text=f"Total Rounds: {controller.total_rounds}").pack()
        tk.Label(self, text=f"Matches per Round: {controller.matches_per_round}").pack()

        # Label for dynamic info (Current Round)
        self.round_status_label = tk.Label(self, text="", pady=10)
        self.round_status_label.pack()

        tk.Button(self, text="Start/Continue Voting",
                  command=lambda: controller.show_frame("VotingPage")).pack(pady=5)
        tk.Button(self, text="View Results",
                  command=lambda: controller.show_frame("ResultsPage")).pack(pady=5)
        tk.Button(self, text="Intermission",
                  command=lambda: controller.show_frame("IntermissionPage")).pack(pady=5)
                  
        tk.Button(self, text="⚠️ RESET ALL DATA TO ZERO",
                  command=lambda: controller.reset_data(),
                  fg="red").pack(pady=20)
        
    def update_display(self):
        """Refreshes the dynamic Current Round text."""
        # Update the text to reflect the current_round value from the controller
        self.round_status_label.config(text=f"Current Round: {self.controller.current_round + 1}")

# --- VOTING PAGE (Replaces RoundOne) ---
class VotingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # --- GUI Elements Setup ---
        self.round_label = tk.Label(self, text="", font=controller.title_font)
        self.round_label.pack(side="top", fill="x", pady=10)
        
        tk.Label(self, text="First to 5 votes wins!").pack()
        
        # Scrollable area for matches
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.matches_frame = tk.Frame(self.canvas)

        self.matches_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.matches_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Lists to hold references to the labels and buttons for dynamic update
        self.match_widgets = []

        # Create 15 sets of labels and buttons (for 15 matches)
        for i in range(controller.matches_per_round):
            match_row = tk.Frame(self.matches_frame)
            match_row.pack(fill="x", pady=5)
            
            match_label = tk.Label(match_row, text="", font=controller.match_font, width=35, anchor='w')
            match_label.pack(side=tk.LEFT, padx=5)
            
            # Use a lambda function to pass the match index 'i' to the controller's vote method
            btn1 = tk.Button(match_row, text="Vote 1", width=8, command=lambda i=i: self.controller.vote(i, 0))
            btn1.pack(side=tk.LEFT, padx=2)
            
            btn2 = tk.Button(match_row, text="Vote 2", width=8, command=lambda i=i: self.controller.vote(i, 1))
            btn2.pack(side=tk.LEFT, padx=2)
            
            self.match_widgets.append({
                'label': match_label,
                'btn1': btn1,
                'btn2': btn2
            })
            
        tk.Button(self, text="Go to Start Page",
                  command=lambda: controller.show_frame("StartPage")).pack(pady=20)

    def update_display(self):
        """Dynamically updates the labels and buttons for the current round's matches."""
        current_matches = self.controller.get_current_match_set()
        
        if not current_matches:
            self.round_label.config(text="TOURNAMENT COMPLETE! Go to Results Page.")
            for widgets in self.match_widgets:
                widgets['label'].config(text="---")
                widgets['btn1'].config(text="DONE", state=tk.DISABLED)
                widgets['btn2'].config(text="DONE", state=tk.DISABLED)
            return

        self.round_label.config(text=f"Round {self.controller.current_round + 1} of {self.controller.total_rounds}")
        
        for i, (name1, name2) in enumerate(current_matches):
            widgets = self.match_widgets[i]
            
            votes1, votes2 = self.controller.get_match_score(name1, name2)
            
            # Check if match is finished (by checking the internal cache status)
            key = tuple(sorted((name1, name2)))
            finished = len(self.controller.round_scores.get(key, [])) == 3
            
            score_text = f"({votes1}-{votes2})"
            
            if finished:
                winner = name1 if votes1 > votes2 else name2
                status_text = f"WINNER: {winner}"
                widgets['btn1'].config(text="VOTE 1", state=tk.DISABLED)
                widgets['btn2'].config(text="VOTE 2", state=tk.DISABLED)
            else:
                status_text = ""
                widgets['btn1'].config(text=f"{name1}", state=tk.NORMAL)
                widgets['btn2'].config(text=f"{name2}", state=tk.NORMAL)
            
            widgets['label'].config(text=f"Match {i+1}: {name1} vs {name2} {score_text} | {status_text}")
            
        # Update canvas scroll region
        self.matches_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

# --- INTERMISSION PAGE ---
class IntermissionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # 1. Variables for the Timer
        self.time_start = 300  #Keep above 1 minute (60s) so there's no issues implementing the code.
        self.time_left_s = self.time_start
        self.timer_id = None    # To hold the reference for the scheduled 'after' call
        
        # Dictionary to map time thresholds to image files
        self.image_map = {
            # Time > time_start / 2 (e.g., > 150 seconds)
            'Squirtle': {"threshold": self.time_start / 2, "file": "Squirtle.png"},
            # Time >= 30 and <= time_start / 2 (e.g., 30 <= time <= 150 seconds)
            'Wartortle': {"threshold": 30, "file": "Wartortle.png"},
            # Time < 30 seconds
            'Blastoise': {"threshold": 0, "file": "Blastoise.png"}, # We use 0 as the lowest boundary
        }
        # A persistent reference for the current PhotoImage
        self.current_image_ref = None 

        # 2. Page Layout
        tk.Label(self, text="Intermission", font=controller.title_font).pack(side="top", fill="x", pady=10)

        # Timer Label (Initialize with the starting time)
        self.timer_label = tk.Label(self, text=self._format_time(), font=controller.title_font, fg="red")
        self.timer_label.pack(pady=10)

        # Display Image Label
        self.image_label = tk.Label(self)
        self.image_label.pack()

        # Navigation Button
        tk.Button(self, text="Go to Start Page",
                  command=lambda: self._stop_timer_and_navigate("StartPage")).pack(pady=20)
                  
    # --- Timer Logic ---
    
    def start_timer(self):
        """Starts or resets the 5-minute timer."""
        # Stop any existing timer before starting a new one
        if self.timer_id:
            self.after_cancel(self.timer_id)
            
        self.time_left_s = 300  # Reset to 5 minutes
        self.update_timer()

    def _update_image(self):
        """Loads and updates the image based on the current time remaining."""
        # The logic is applied in descending order of time remaining to handle overlapping ranges
        
        image_file = None
        
        # 1. Blastoise: Time < 30 seconds
        if self.time_left_s < 30:
            image_file = self.image_map['Blastoise']['file']
        # 2. Wartortle: 30 <= Time <= time_start / 2 (e.g., 30 <= Time <= 150)
        elif self.time_left_s <= self.time_start / 2:
            image_file = self.image_map['Wartortle']['file']
        # 3. Squirtle: Time > time_start / 2 (e.g., > 150)
        else:
            image_file = self.image_map['Squirtle']['file']

        try:
            # Load the new image and store a reference to prevent garbage collection
            new_image_ref = tk.PhotoImage(file=image_file)
            self.image_label.config(image=new_image_ref)
            self.current_image_ref = new_image_ref
        except tk.TclError:
            self.image_label.config(image='', text=f"Error: {image_file} not found")
            self.current_image_ref = None

    def update_timer(self):
        """Decrements the timer and schedules the next update."""
        if self.time_left_s > 0:
            self.time_left_s -= 1
            self.timer_label.config(text=self._format_time())
            
            # --- The crucial fix: Update the image dynamically ---
            self._update_image()
            
            # Schedule this function to run again after 1000ms (1 second)
            self.timer_id = self.after(1000, self.update_timer)
        else:
            # Timer is done!
            self.timer_label.config(text="Time's Up!", fg="blue")
            self._update_image() # Final image update
            
    def _format_time(self):
        """Converts seconds into MM:SS format."""
        minutes = self.time_left_s // 60
        seconds = self.time_left_s % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _stop_timer_and_navigate(self, page_name):
        """Stops the timer when navigating away."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.controller.show_frame(page_name)

# --- RESULTS PAGE (Final Alignment Optimization) ---
class ResultsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Use a monospaced font for perfect column alignment
        self.mono_font = tkfont.Font(family='Courier New', size=10)
        
        tk.Label(self, text="Tournament Standings", font=controller.title_font).pack(side="top", fill="x", pady=10)
        
        # Scrollable area for results
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.results_labels = []

        tk.Button(self, text="Go to Start Page",
                  command=lambda: controller.show_frame("StartPage")).pack(pady=20)

    def update_display(self):
        """Calculates and displays the sorted standings with fixed-width alignment."""
        # Clear previous results
        for label in self.results_labels:
            label.destroy()
        self.results_labels = []

        # Import Names here to ensure latest data is read before calculating
        import Names 
        data = []
        for i, name in enumerate(Names.names):
            data.append({
                'name': name,
                'wins': Names.winCount[i],
                'losses': Names.lossCount[i],
                'total_votes': Names.nameVotes[i]
            })
        
        standings = data
        
        # Sort by: 1) Wins (desc), 2) Losses (asc), 3) Total Votes (desc)
        standings.sort(key=lambda item: (-item['wins'], item['losses'], -item['total_votes']))
        
        # 1. Display the Header: Use < for left-aligned text, > for right-aligned numbers
        header_text = (
            f"{'Rank':<5}"
            f"{'Name':<20}"
            f"{'Wins':>8}"      # Right-aligned header
            f"{'Losses':>8}"    # Right-aligned header
            f"{'Votes':>5}"     # Right-aligned header
        )
        header = tk.Label(self.scrollable_frame, 
                          text=header_text, 
                          font=self.mono_font, 
                          anchor='w', bg="#e0e0e0")
        header.pack(fill='x', padx=5, pady=5)
        self.results_labels.append(header)
        
        # 2. Display the sorted results
        for rank, stats in enumerate(standings):
            # Use fixed-width formatting for perfect alignment
            text = (
                f"{rank+1:<5}"                     # Rank (Left-aligned)
                f"{stats['name'][:19]:<20}"        # Name (Left-aligned)
                f"{stats['wins']:>8}"              # Wins (Right-aligned)
                f"{stats['losses']:>8}"            # Losses (Right-aligned)
                f"{stats['total_votes']:>5}"       # Votes (Right-aligned)
            )
            label = tk.Label(self.scrollable_frame, text=text, anchor='w', font=self.mono_font)
            label.pack(fill='x', padx=5)
            self.results_labels.append(label)
        
        # Update canvas scroll region after adding all widgets
        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":    
    app = BracketApp()
    app.mainloop()
