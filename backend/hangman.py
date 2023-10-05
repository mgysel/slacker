'''
Hangman game implemented in Python
'''

import time
from random_word import RandomWords

HANGMAN = [
"""
   _________
    |/        
    |              
    |                
    |                 
    |               
    |                   
    |___                 
    """,

"""
   _________
    |/   |      
    |              
    |                
    |                 
    |               
    |                   
    |___                 
    H""",

"""
   _________       
    |/   |              
    |   (_)
    |                         
    |                       
    |                         
    |                          
    |___                       
    HA""",

"""
   ________               
    |/   |                   
    |   (_)                  
    |    |                     
    |    |                    
    |                           
    |                            
    |___                    
    HAN""",

"""
   _________             
    |/   |               
    |   (_)                   
    |   /|                     
    |    |                    
    |                        
    |                          
    |___                          
    HANG""",

"""
   _________              
    |/   |                     
    |   (_)                     
    |   /|\                    
    |    |                       
    |                             
    |                            
    |___                          
    HANGM""",

"""
   ________                   
    |/   |                         
    |   (_)                      
    |   /|\                             
    |    |                          
    |   /                            
    |                                  
    |___                              
    HANGMA""",

"""
   ________
    |/   |     
    |   (_)    
    |   /|\           
    |    |        
    |   / \        
    |               
    |___           
    HANGMAN"""]

# Random Word generator
r = RandomWords()
WORD = r.get_random_word(hasDictionaryDef="true", minLength=6)
WORD = WORD.upper()

# Setting up variables
WRONG = 0
MAX_WRONG = 7
GUESSES = []
GUESSED_CHARS = "_" * len(WORD)

print("\n++++++++++ WELCOME TO HANGMAN! YOU HAVE 7 GUESSES AT THE MYSTERY WORD ++++++++++")

while WRONG < MAX_WRONG and GUESSED_CHARS != WORD: 
    print("\n++++++++++ START OF ROUND ++++++++++")
    print(HANGMAN[WRONG])
    print("WORD IS: {} \n".format(" ".join(GUESSED_CHARS)))
    print("YOU HAVE USED {}/7 GUESSES: {}\n".format(WRONG, "X " * WRONG))
    print("YOU HAVE GUESSED THESE LETTERS/ WORDS: {}\n".format(GUESSES))

    GUESS = input("ENTER YOUR LETTER OR WORD GUESS -----> ").upper()
    # Check if something has already been guessed
    while GUESS in GUESSES: 
        print("YOU HAVE ALREADY GUESSED {}, TRY AGAIN...\n".format(GUESS))
        GUESS = input("ENTER YOUR LETTER OR WORD GUESS -----> ").upper()
    GUESSES.append(GUESS)

    # Checking correctness
    correct = 0
    if GUESS in WORD:
        correct = 1
        HOLDER = ""
        for i in range(len(WORD)):
            if WORD[i] == GUESS:
                HOLDER += GUESS
            else:
                HOLDER += GUESSED_CHARS[i]
        GUESSED_CHARS = HOLDER

    # Increment wrong counter if team does not guess correctly
    if correct == 0: 
        WRONG += 1

    # check if the team has won
    if GUESSED_CHARS == WORD: 
        print("\n++++++++++ CONGRATULATIONS YOU WIN!!! THE WORD WAS {} ++++++++++\n".format(WORD))
        exit()

if WRONG == MAX_WRONG:
    print("\n++++++++++ END OF GAME ++++++++++\n")
    print("YOU HAVE USED {}/7 GUESSES: {}".format(WRONG, "X " * WRONG)) 
    print(HANGMAN[WRONG])
    print("\n++++++++++ YOU WERE HANGED! THE WORD WAS {} ++++++++++\n".format(WORD))
