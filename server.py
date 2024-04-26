#Sean Reed
#7033251
#COSC2p13 Assignment 2

#server.py

import socket
import threading

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #use IPV4, and stream (think TCP)
server.bind(("localhost", 2048)) #Normally we'd use use the proper host name
server.listen(5) #Allow up to 5 queued connections

#increments everytime a new game is started
#eg. first 2 clients that start a game will be game 0, and the next 2 clients start a game will be game 1...etc
game_ids=0

#used to determine if there's a connect four in the game_state and returns boolean
def check_connectfour(game_state, player_marker):
    #dict for checking each direction (left/right, up/down, diagonals)
    directions = [(1,0), (0,1), (1,1), (1,-1)]

    #see if there is connect four by traversing each space in game state
    for a in range(5):
        for b in range(5):
            if game_state[a][b] in player_marker:
                for dx, dy in directions: #check each direction
                    count = 1
                    x,y=a,b
                    #increment count for each successive piece we find in a direction
                    while (0 <= x + dx < 5 and 0 <= y + dy < 5) and game_state[x+dx][y+dy] == game_state[a][b]:
                        count = count + 1
                        if count == 3:
                            #found connect four
                            return True
                        x,y = x+dx, y+dy #increment direction offset
    
    #there isn't a connect four
    return False
    

#called after each players turn and sends updated game state to other player
def update_game_state(game_id, updated_client, other_client, current_turn, game_state, pos):
    player_marker = '[1]' #chars used to represent player pieces on game state
    if current_turn == 2:
        player_marker = '[2]'
    
    #perform checks if a piece is in the way
    row_pos = 5
    #start from bottom row of game_state and check for available spots
    for x in range(5, -1, -1): 
        if game_state[x][pos] == "[ ]":
            row_pos = x #our piece fits in this spot
            break
    
    #update game state with player input
    game_state[row_pos][pos] = player_marker

    #send player the updated game state
    for row in game_state:
        print(str(row)+'\n')
        row_s = ' '.join(row) #compile row into a string
        updated_client.sendall((row_s+'\n').encode()) #send game state row by row

    #check for a connect four
    game_resolved = check_connectfour(game_state, player_marker)
    print("Connect four: " + str(game_resolved) )
    
    #send client info if there is a connect four
    updated_client.sendall((str(game_resolved)+'\n').encode())

    #if game is over, print server message indicating who won and then close both clients
    if game_resolved:
        print("State of Game ID " + str(game_id) + ", there is a connect four for player " + str(current_turn) )
        updated_client.close()
    else:
        print("State of Game ID " + str(game_id) )


def connectfour_game(client_one, client_two, game_id):
 
    #send game id to players
    client_one.sendall((str(game_id)+'\n').encode())
    client_two.sendall((str(game_id)+'\n').encode())
    
    #once a game has started, inform players their player number
    client_one.sendall(('1'+'\n').encode())
    client_two.sendall(('2'+'\n').encode())

    #initalize the game state
    game_state = [["[ ]" for y in range(6)] for x in range(6)]
    
    #send the empty game state to each player
    for row in game_state:
        print(str(row)+'\n')
        row_s = ' '.join(row) #compile row into a string
        client_one.sendall((row_s+'\n').encode()) #send game state row by row
        client_two.sendall((row_s+'\n').encode()) #send game state row by row
    
    current_turn = "2" #players current turn

    #main game loop
    while True:
        
        #send each player whose turn it is
        current_turn = "2" if current_turn == "1" else "1"
        client_one.sendall((current_turn+'\n').encode())
        client_two.sendall((current_turn+'\n').encode())

        #recieve player 1 input
        one_to_two=client_one.recv(100)
        if len(one_to_two)==0: #if client 1 disconnected
            break

        #update game state based on player 1 input and send to player 2
        update_game_state(game_id, client_two, client_one, int(current_turn), game_state, int(one_to_two)-1) 

        #break loop if there is a game that was resolved
        if check_connectfour(game_state, '[1]'):
            break

        #alternate turns and send current turn to clients
        current_turn = "2" if current_turn == "1" else "1"
        client_one.sendall((current_turn+'\n').encode())
        client_two.sendall((current_turn+'\n').encode())

        #recieve player 2 input
        two_to_one=client_two.recv(100)
        if len(two_to_one)==0: #if client 2 disconnected
            break

        #update game state based on player 2 input and send back to player 1
        update_game_state(game_id, client_one, client_two, int(current_turn), game_state, int(two_to_one)-1)

        #break loop if there is a game that was resolved
        if check_connectfour(game_state, '[2]'):
            break


#keep accepting pairs of connections here:
while True:
    
    #accept 2 clients
    (client_one, add_one) = server.accept()
    print("Accepted client A:"+str(add_one))
    (client_two, add_two) = server.accept()
    print("Accepted client B:"+str(add_two))
    print("Started Game ID "+str(game_ids))
     
    #once 2 clients have been paired, start a game
    threading.Thread(target=connectfour_game,args=(client_one,client_two,game_ids)).start()
    
    #increment game ids
    game_ids = game_ids + 1