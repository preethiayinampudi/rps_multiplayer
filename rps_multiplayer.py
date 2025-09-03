import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import pygame
import threading
import os
player_count_entry = None

# Initialize pygame mixer
pygame.mixer.init()

# Function to play sound
def play_sound(file_path):
    if os.path.exists(file_path):
        threading.Thread(target=lambda: pygame.mixer.Sound(file_path).play()).start()


# 🔊 Play background music
play_sound("sounds/landing_bg_music.mp3")

# Game assets and variables
choices = ["rock", "paper", "scissors"]
images = {}
players = []
player_choices = {}
scores = {}
current_player_index = 0
player_entries = []

# Load hand images
def load_images():
    for choice in choices:
        img = Image.open(f"{choice}.png").resize((150, 150), Image.Resampling.LANCZOS)
        images[choice] = ImageTk.PhotoImage(img)

# Set background image to a frame
def set_frame_background(frame, image_path=None):
    if not image_path:
        return
    try:
        bg_img = Image.open(image_path).resize((1024, 720), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(frame, image=bg_photo)
        bg_label.image = bg_photo  # Keep reference
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()
    except Exception as e:
        print(f"Background load error: {e}")

# Shake animation
def shake_hands(callback):
    shake_frame = tk.Frame(game_frame, bg="#DCEEF2")
    shake_frame.pack(pady=20)
    label = tk.Label(shake_frame, text="🤜 Shaking hands 🤛", font=("Comic Sans MS", 62, "bold"), bg="#DCEEF2")
    label.pack()
    motion_label = tk.Label(shake_frame, text="", font=("Segoe UI", 90), bg="#DCEEF2")
    motion_label.pack()

    motions = ["🤜 🤛", "🤛 🤜"] * 3
    def animate(i=0):
        if i < len(motions):
            motion_label.config(text=motions[i])
            game_frame.after(300, animate, i + 1)
        else:
            shake_frame.destroy()
            callback()

    animate()

# Determine winners
def determine_winners():
    unique_choices = list(set(player_choices.values()))
    if len(unique_choices) == 1:
        play_sound("sounds/tie.mp3")
        return "🤝 It's a tie!"

    win_map = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
    winning_choice = None
    for choice in unique_choices:
        if any(win_map[choice] == other for other in unique_choices if other != choice):
            winning_choice = choice
            break

    winners = [p for p, c in player_choices.items() if c == winning_choice]
    for winner in winners:
        scores[winner] += 1

    play_sound("sounds/win.mp3") if winners else play_sound("sounds/lose.mp3")
    return f"🎉 Winner(s): {', '.join(winners)} 🎉"

# Emoji reaction
def get_emoji_reaction(result_text):
    if "winner" in result_text.lower():
        return random.choice(["🎉", "😎", "🔥", "🎯", "🥳", "🤩"])
    return random.choice(["😢", "😅", "🙃", "🧷"])

# Reset round
def reset_round():
    global player_choices, current_player_index
    player_choices.clear()
    current_player_index = 0
    result_frame.pack_forget()
    play_round()

# Show mode selection
def show_mode_selection():
    play_sound("sounds/click.mp3")  # <== added here
    landing_frame.pack_forget()
    mode_frame_screen.pack(fill="both", expand=True)

# Select mode
def select_mode(is_single):
    single_player_mode.set(is_single)
    mode_frame_screen.pack_forget()
    show_start_page()

# Show start page
def show_start_page():
    toggle_mode()
    start_frame.pack(fill="both", expand=True)

# Toggle between single and multiplayer
def toggle_mode():
    for widget in multiplayer_frame.winfo_children():
        widget.destroy()
    player_entries.clear()

    if single_player_mode.get():
        multiplayer_frame.pack_forget()
        single_player_frame.pack(pady=20)
    else:
        single_player_frame.pack_forget()
        multiplayer_frame.pack(pady=20)
        tk.Label(multiplayer_frame, text="Enter number of players (2-6):", font=("Segoe UI", 16), bg="#FFFDE7").pack()
        global player_count_entry
        player_count_entry = tk.Entry(multiplayer_frame, font=("Segoe UI", 16), width=5)
        player_count_entry.pack(pady=10)

        def show_name_fields():
            for widget in multiplayer_frame.winfo_children():
                if isinstance(widget, tk.Entry) and widget != player_count_entry:
                    widget.destroy()
            player_entries.clear()
            try:
                count = int(player_count_entry.get())
                if 2 <= count <= 6:
                    for i in range(count):
                        entry = tk.Entry(multiplayer_frame, font=("Segoe UI", 16))
                        entry.insert(0, f"Player {i+1}")
                        entry.pack(pady=5)
                        player_entries.append(entry)
                else:
                    messagebox.showerror("Invalid Input", "Enter a number between 2 and 6")

            except ValueError:
                messagebox.showerror("Error", "Enter a valid number.")

        tk.Button(multiplayer_frame, text="Confirm", command=show_name_fields,
                  font=("Segoe UI", 14), bg="#FFD54F").pack(pady=10)

# Start the game
def start_game():
    global players, scores, current_player_index
    players.clear()
    scores.clear()
    current_player_index = 0

    if single_player_mode.get():
        name = single_player_name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Please enter your name.")
            return
        players.extend([name, "Computer"])
        scores[name] = 0
        scores["Computer"] = 0
    else:
        if not player_entries:
            messagebox.showerror("No Players", "Please enter player names.")
            return
        for entry in player_entries:
            name = entry.get().strip()
            if not name:
                messagebox.showerror("Missing Name", "All players must have names.")
                return
            players.append(name)
            scores[name] = 0

    start_frame.pack_forget()
    play_round()

# Play a round
def play_round():
    for widget in game_frame.winfo_children():
        widget.destroy()
    set_frame_background(game_frame, "img3.jpg")
    game_frame.configure(bg="#DCEEF2")

    player = players[current_player_index]
    status = tk.Label(game_frame, text=f"{player}, it's your turn!",
                      font=("Verdana", 30, "bold"), bg="#DCEEF2", fg="#004D40")
    status.pack(pady=20)

    def show_buttons():
        btn_frame = tk.Frame(game_frame, bg="#DCEEF2")
        btn_frame.pack(pady=20)
        for choice in choices:
            btn = tk.Button(btn_frame, image=images[choice],
                            command=lambda c=choice: choose_hand(c), bd=0,
                            bg="#DCEEF2", activebackground="#B2EBF2", cursor="hand2")
            btn.pack(side=tk.LEFT, padx=40)

    shake_hands(show_buttons)
    game_frame.pack(fill="both", expand=True)

# Choose hand
def choose_hand(choice):
    play_sound("sounds/button.mp3")
    global current_player_index
    player = players[current_player_index]
    if player == "Computer":
        choice = random.choice(choices)
    player_choices[player] = choice
    current_player_index += 1

    if current_player_index < len(players):
        play_round()
    else:
        result = determine_winners()
        game_frame.pack_forget()
        show_result_frame(result)

# Show result frame
def show_result_frame(result):
    for widget in result_frame.winfo_children():
        widget.destroy()
    set_frame_background(result_frame, "img5.jpg")

    tk.Label(result_frame, text=result, font=("Segoe UI", 30, "bold"),
             bg="#FFEBEE", fg="#C62828").pack(pady=30)
    tk.Label(result_frame, text=get_emoji_reaction(result),
             font=("Segoe UI", 60), bg="#FFEBEE").pack()
    show_scoreboard(result_frame)

    again_btn = tk.Button(result_frame, text="Play Again", font=("Segoe UI", 20, "bold"),
                          command=reset_round, bg="#43A047", fg="white", cursor="hand2", padx=30, pady=10)
    again_btn.pack(pady=30)
    result_frame.pack(fill="both", expand=True)

# Scoreboard
def show_scoreboard(frame):
    score_text = "\n".join([f"{p}: {s}" for p, s in scores.items()])
    tk.Label(frame, text=f"🏆 Scoreboard 🏆\n\n{score_text}",
             font=("Segoe UI Semibold", 22), bg=frame["bg"], fg="#6A1B9A").pack(pady=20)

# Initialize root window
root = tk.Tk()
root.title("🎮 Rock Paper Scissors")
root.geometry("1024x720")
root.resizable(False, False)

# Load hand images
load_images()

# Frames
landing_frame = tk.Frame(root)
mode_frame_screen = tk.Frame(root)
start_frame = tk.Frame(root)
single_player_frame = tk.Frame(start_frame, bg="#3C370F")
multiplayer_frame = tk.Frame(start_frame, bg="#8CB3F3")
game_frame = tk.Frame(root)
result_frame = tk.Frame(root)

# Backgrounds
set_frame_background(landing_frame, "background.jpg")
set_frame_background(mode_frame_screen, "img5.jpg")
set_frame_background(start_frame, "img3.jpg")

# Show landing page
landing_frame.pack(fill="both", expand=True)

# Landing page content
tk.Label(
    landing_frame,
    text="Rock Paper Scissors",
    font=("Impact", 44),
    bg="#FFDDEE", fg="#4C1D95"
).pack(side="top", pady=30)

# Start button
tk.Button(
    landing_frame,
    text="START",
    font=("Segoe UI", 20, "bold"),
    bg="#7C3AED", fg="white",
    width=16, height=1,
    activebackground="#6D28D9",
    cursor="hand2",
    command=show_mode_selection
).pack(side="bottom", pady=40)

# Mode Selection Page
single_player_mode = tk.BooleanVar(value=False)
tk.Label(mode_frame_screen, text="Choose Game Mode", font=("Segoe UI Black", 36), bg="#F1F8E9", fg="#33691E").pack(pady=60)
tk.Button(mode_frame_screen, text="You vs Computer", font=("Segoe UI", 20), bg="#AED581", fg="white", width=20, height=2, command=lambda: select_mode(True)).pack(pady=20)
tk.Button(mode_frame_screen, text="Multiplayer", font=("Segoe UI", 20), bg="#4DD0E1", fg="white", width=20, height=2, command=lambda: select_mode(False)).pack(pady=20)

# Single Player Setup
tk.Label(single_player_frame, text="Enter your name:", font=("Segoe UI", 18), bg="#FFFDE7").pack(pady=10)
single_player_name_entry = tk.Entry(single_player_frame, font=("Segoe UI", 16))
single_player_name_entry.pack(pady=10)

# Start Game Button
tk.Button(start_frame, text="Start Game", font=("Segoe UI", 20, "bold"), bg="#070E11", fg="white", width=16, height=2, cursor="hand2", command=start_game).pack(pady=30)

# Start GUI loop
root.mainloop()