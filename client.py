#Sean Reed
#7033251
#COSC2p13 Assignment 2

#client.py

import socket

socky=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #use IPV4, and stream (think TCP)
socky.connect(("localhost",2048))
#socky.settimeout(10) #10 sec

#1st thing client recieves from server is game number
game_id=socky.recv(100).decode().strip()
print("Game ID: " + game_id)

#2nd thing client will recieve from server is their player number
player_id=socky.recv(100).decode().strip()
print("A game has started, You are: Player " + player_id)

def recieve_game_state():
    #recieve initial empty game state line by line and print
    for x in range(0,6):
        try:
            row_data = socky.recv(100)
            #print("Recieved:", row_data) #debug
            if not row_data:
                print("Connection closed by server.")
                break
            print(row_data.decode().strip() ) #print recieved row
        except socket.timeout:
            print("Timeout occured, server didn't send data.")
            break
        except Exception as e:
            print("Error occured:", e)
            break

#recieve initial game state
recieve_game_state()

#method to validate user input (only allow for numbers 1 -> 6)
def is_valid_input():
    while True:
        user_input = input("> Input the column to drop (1 to 6): ")
        if user_input.isdigit() and 1 <= int(user_input) <= 6:
            return user_input
        else:
            print("Invalid input. Please input a number between 1 and 6.")

while True:
    try:
        #receive whose turn it is from server
        current_turn = socky.recv(100).decode().strip()
        print("Current turn is:", current_turn)
        print("Player id is:", player_id)
        
        if player_id == current_turn:
            s=is_valid_input()
            socky.sendall((s+"\n").encode()) #send user input to server
        else:
            #recieve new board state
            recieve_game_state()
            
            #recieve message if there has been a connect four, if so, then break
            game_resolved = socky.recv(100).decode().strip()
            if (game_resolved == "True"):
                print("Player " + current_turn + " wins")
                break
        
    except Exception as e:
        print("Error:", e)
        break