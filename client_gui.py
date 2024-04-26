#Sean Reed
#7033251
#COSC2p13 Assignment 2

#client_gui.py

import tkinter as tk
from tkinter import messagebox
import socket
import threading

class ConnectFourGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect Four GUI")
        
        #set GUI to a small window
        self.root.geometry("400x300")
        
        #GUI variables
        self.game_id_label = tk.Label(self.root, text="Game ID: ")
        self.game_id_label.pack()
        
        self.player_id_label = tk.Label(self.root, text="Player ID: ")
        self.player_id_label.pack()
        
        self.game_state_label = tk.Label(self.root, text="Game State:")
        self.game_state_label.pack()
        
        self.game_state_text = tk.Text(self.root, height=6, width=25)
        self.game_state_text.pack()
        
        self.input_label = tk.Label(self.root, text="Input the column to drop (1 to 6): ")
        self.input_label.pack()
        
        self.input_entry = tk.Entry(self.root)
        self.input_entry.pack()
        
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.submit_button.pack()
        
        self.socky = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socky.connect(("localhost", 2048))
        
        #obtain game id from server
        self.game_id = self.socky.recv(100).decode().strip()
        print("Game ID: " + self.game_id)
        
        #obtain player id from server
        self.player_id = self.socky.recv(100).decode().strip()
        print("A game has started, You are: Player " + self.player_id)
        
        self.game_id_label.config(text="Game ID: " + self.game_id)
        self.player_id_label.config(text="Player ID: " + self.player_id)
        
        #recieve initial game state
        self.recieve_game_state()
        
        self.listen_game_state_thread = threading.Thread(target=self.listen_game_state)
        self.listen_game_state_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    #recieve game state from server and parse it and then display onto GUI
    def recieve_game_state(self):
        game_state_text = ""
        #recieve initial empty game state line by line and print
        for x in range(0,6):
            try:
                row_data = self.socky.recv(100)
                #print("Recieved:", row_data) #debug
                if not row_data:
                    print("Connection closed by server.")
                    break
                row_string = row_data.decode().strip()
                print( row_string ) #print recieved row
                game_state_text += row_string + "\n" #append rows to game text
                
            except socket.timeout:
                print("Timeout occured, server didn't send data.")
                break
            except Exception as e:
                print("Error occured:", e)
                break
        
        # display game state on GUI
        self.game_state_text.config(state=tk.NORMAL)
        self.game_state_text.delete(1.0, tk.END)  # clear previous game state
        self.game_state_text.insert(tk.END, game_state_text)  # update game state
        self.game_state_text.config(state=tk.DISABLED)

    #main client loop, handles the game state
    def listen_game_state(self):
        while True:
            try:
                #receive whose turn it is from server
                current_turn = self.socky.recv(100).decode().strip()
                print("Current turn is:", current_turn)
                print("Player id is:", self.player_id)

                #disable button if and let user know if it is their turn
                if self.player_id == current_turn:
                    self.submit_button["state"] = "normal"
                    self.input_label.config(text="Your turn. Input the column to drop (1 to 6):")
                else:
                    self.submit_button["state"] = "disabled"
                    self.input_label.config(text="Opponent's turn. Waiting for their move...")

                    # receive new board state
                    self.recieve_game_state()

                    # receive message if there has been a connect four, if so, then break
                    game_resolved = self.socky.recv(100).decode().strip()
                    if game_resolved == "True":
                        print("Player " + current_turn + " wins")
                        self.root.destroy()
                        break
            except:
                self.root.destroy()
                break

    #button handling input submission, also checks for valid input
    def submit_input(self):
        input_value = self.input_entry.get().strip() #parse input
        if input_value.isdigit() and 1 <= int(input_value) <= 6: #validate input
            self.socky.sendall((input_value + "\n").encode())
            self.input_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid input. Please enter a number between 1 and 6.")
    
    #function for when user quits, closes socket and destroys gui
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.socky.close()
            self.root.destroy()

if __name__ == "__main__":
    gui = ConnectFourGUI()
    gui.root.mainloop()
