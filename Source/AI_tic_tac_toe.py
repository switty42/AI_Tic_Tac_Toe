# ChatGPT tic tac toe
# Author Stephen Witty
# 8-26-23
# Example code from rollbar.com - GPT example
#
# V1 8-26-23 - Initial release / dev
# V2 9-12-23 - Add timeout to GPT
#
# Notes - Add your OpenAI key below
# Change Linux constant below for correct clear screen command for your OS

import openai
import time
import sys
import os

# Put OpenAI API key here
openai.api_key = "XXXXXXXXXXXXXXXXXXXXX"

# Uncomment GPT model desired here
#gpt_model='gpt-3.5-turbo'
gpt_model = "gpt-4"

###################### Constants ##########################################################
NUMBER_OF_GAMES_TO_PLAY = 10      # Number of games the program will play before exiting
GPT_RETRY_LIMIT = 25              # Number of times to retry GPT if errors occur
SLEEP_ON_DISPLAY = 3              # Seconds to sleep incase of an error
LINUX = True                      # Running on Linux machine - for screen clear
CLEAR_SCREEN = True               # Clear the screen during updates


########## This function creates the AI prompt based on inputed player (X or O) #######
def create_gpt_prompt(player):

   prompt_message = "A game of tic tac toe is in progress and you are asked to help decide the next move. \
The board spaces are numbered from 1 to 9.  The first row are spaces 1, 2 and 3.  The second row are spaces 4, 5 and 6.  \
The third row are spaces 7, 8 and 9.  The board is currently populated like this: "

   cnt = 1
   for entry in board:
      if (cnt > 1):
         prompt_message = prompt_message + ", "
      prompt_message = prompt_message + "Space " + str(cnt) + " is "
      if (entry == " "):
         prompt_message = prompt_message + "None"
      else:
         prompt_message = prompt_message + entry
      cnt = cnt + 1

   prompt_message = prompt_message + ".  It is the player with the token " + player + " turn to play.  \
What space should player with token " + player + " place their token to give the player the best chance to win the game on this move or a future move? \
Provide the answer as a number in between {}.  For example if the answer is space 7, your output should include {7}.  \
If the board is completely empty pick the most advantageous starting space.  You cannot pick a space that is not currently None."

   return prompt_message

########### This function formats an output string ####################
def print_string(string):
   cnt = 0
   for char in string:
      if not (char == " " and cnt == 0):
         print(char, end="")
         cnt = cnt + 1
      if (cnt > 115 and char == " "):
         print()
         cnt = 0
   print()
   sys.stdout.flush()

############### Function - Call ChatGPT #########################################
def call_gpt(prompt_message):
   global error_text
   try:
      response = openai.ChatCompletion.create(model=gpt_model, messages=[ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt_message}],request_timeout=25)
   except Exception as e:
      error_text = "WARNING: System Error during ChatGPT call: " + str(e)
      return ""

   return response.choices[0]["message"]["content"]

##################### Function - parse the space answer from GPT reply ############################
# Going to some lengths to verify the answer from GPT is a number since replies are often unpredictable
# A zero return code means something went wrong - answer should be between 1 and 9
def parse_answer(message):
   global error_text
   cnt = 0
   cnt2 = 0
   pos = 0
   for char in message:
      if (char == "{"):
         cnt = cnt + 1
         start = pos
      if (char == "}"):
         cnt2 = cnt2 + 1
         end = pos
      pos = pos + 1

   if (cnt == 0 or cnt2 == 0):
      error_text = "WARNING:  No brackets or incomplete"
      return 0

   if (cnt > 1 or cnt2 > 1):
      error_text = "WARNING:  Too many brackets in output from GPT"
      return 0

   if (end < start):
      error_text = "WARNING: Brackets are reversed in output from GPT"
      return 0

   if ( (end - start) != 2):
      error_text = "WARNING: No single digit number in between brackets"
      return 0

   move_char = message[start + 1]
   if not (move_char.isdigit()):
      error_text = "WARNING: Answer is not a digit"
      return 0

   answer = int(move_char)
   if (answer < 1 or answer > 9):
      error_text = "WARNING:  Answer is out of range"
      return 0

   return answer

########## Function print the board #######################
def print_board():
   print()
   print("         |       |")
   print("     " + board[0] + "   |" + "   " + board[1] + "   |" + "   " + board[2])
   print("         |       |")
   print("  -----------------------")
   print("         |       |")
   print("     " + board[3] + "   |" + "   " + board[4] + "   |" + "   " + board[5])
   print("         |       |")
   print("  -----------------------")
   print("         |       |")
   print("     " + board[6] + "   |" + "   " + board[7] + "   |" + "   " + board[8])
   print("         |       |")
   print()

########### Function check for winner or tie #############
def check_for_winner():

   if (board[0] == board[1] and board[0] == board[2] and board[0] != " "):
      return(board[0])

   if (board[3] == board[4] and board[3] == board[5] and board[3] != " "):
      return(board[3])

   if (board[6] == board[7] and board[6] == board[8] and board[6] != " "):
      return(board[6])

   if (board[0] == board[3] and board[0] == board[6] and board[0] != " "):
      return(board[0])

   if (board[1] == board[4] and board[1] == board[7] and board[1] != " "):
      return(board[1])

   if (board[2] == board[5] and board[2] == board[8] and board[2] != " "):
      return(board[2])

   if (board[0] == board[4] and board[0] == board[8] and board[0] != " "):
      return(board[0])

   if (board[6] == board[4] and board[6] == board[2] and board[6] != " "):
      return(board[6])

   for space in board:
      if (space == " "):
         return "N"        # No winner yet

   return "Tie"  # Tie

############## Function to update the screen #######################################################
def update_screen():

   if (CLEAR_SCREEN):
      if (LINUX):
         os.system("clear") # Linux clear
      else:
         os.system("cls") # Windows clear

   print_board()

   print("\nMove history: ",end="")

   cnt = 0
   for m in move_history:
      if (cnt > 0 ):
         print(", ",end="")
      print(m,end="")
      cnt = cnt + 1

   print("\n\nCurrent winner: " + str(winner))

   print("\nX wins: " + str(total_x_wins) + "   O wins: " + str(total_o_wins) + "   Ties: " + str(total_ties))

   print("\n******* GPT prompt *************************")
   print_string(prompt)
   print("\n******* GPT reply **************************")
   print_string(gpt_reply)
   print("\n" + error_text)

###############  Start of main routine ##############################################################
number_of_games = 0

total_x_wins = 0
total_o_wins = 0
total_ties = 0

while(number_of_games < NUMBER_OF_GAMES_TO_PLAY): # Main loop to start games

   # Begin games with an empty board
   board = [" "," "," "," "," "," "," "," "," "]

   player = "X" # Start game as X
   winner = ""
   move_history = [] # Store the move history of each game


   while(check_for_winner() == "N"): # Loop for single game, check for winner here and break as needed, N = no winner or tie

      # Create GPT prompt
      prompt = create_gpt_prompt(player)

      # Call GPT and decode reply to a move
      gpt_reply = ""
      retry_count = 0

      while (gpt_reply == ""):

         error_text = "" # This is used inside functions to pass back error messages to display on screen updates

         if (retry_count == GPT_RETRY_LIMIT):
            print("\n\nERROR: Too many GPT errors, exiting\n")
            sys.exit()

         gpt_reply = call_gpt(prompt) # Call GPT
         if (gpt_reply == ""):
            update_screen()
            time.sleep(SLEEP_ON_DISPLAY)
            retry_count = retry_count + 1
            continue

         update_screen()

         answer = parse_answer(gpt_reply) # Decode GPT answer
         if (answer == 0):
            update_screen()
            time.sleep(SLEEP_ON_DISPLAY)
            retry_count = retry_count + 1
            gpt_reply = ""
            continue

         if not (board[answer - 1] == " "): # Verify that the space is free, retry if not
            error_text = "WARNING:  Space already in use"
            update_screen()
            time.sleep(SLEEP_ON_DISPLAY)
            retry_count = retry_count + 1
            gpt_reply = ""
            continue

         board[answer - 1] = player # Assign GPT move to board

         move_history.append(player + str(answer)) # Add move to game history

         update_screen()

         if (player == "X"):  # Toggle player for next move
            player = "O"
         else:
            player = "X"

   winner = check_for_winner()
   if (winner == "X"):
      total_x_wins = total_x_wins + 1
   if (winner == "O"):
      total_o_wins = total_o_wins + 1
   if (winner == "Tie"):
      total_ties = total_ties + 1

   update_screen()

   time.sleep(SLEEP_ON_DISPLAY)

   number_of_games = number_of_games + 1
