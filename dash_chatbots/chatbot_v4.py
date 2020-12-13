# =========================
'''
v2
Bugs fixed:
1. Add more states, making sure when user greets, the state will go back
2. Lower the fuzzy match ratio to allow more results. Make sure that the function returns the complete movie name
3. Create new regex pattern so we don't trim the title by accident
Features added:
1. Let user decide what movies to choose if there are more than two options in the query result

v3
Other:
1. break down the fuzzy match to two functions for dash implementation

v4
Other:
1. Add new states: confirm_movie, bye
2. Add more small chats 
'''
# =========================

# Import the required libraries 
import re 
import random
import pandas as pd
from fuzzywuzzy import fuzz
from pathlib import Path
import os
base_path = Path(__file__).parent
os.chdir(base_path)

# Load and preprocess movie data 
movies = pd.read_csv('data/movies.csv')
links = pd.read_csv('data/links.csv', converters={'imdbId': lambda x: str(x)})
movies['clean_title'] = [re.sub(r',\sThe\s\(\d+\)', '', t) for t in movies.title]
movies['clean_title'] = [re.sub(r'\s\(\d+\)', '', t) for t in movies.clean_title]
movies['clean_title'] = [re.sub(r'[*]', '', t) for t in movies.clean_title]
movies['clean_genres'] = [g.split('|') for g in movies.genres]
movie_explode = movies.explode('clean_genres')
genres_list = [i.lower() for i in movie_explode['clean_genres'].unique()]
movies_links = movies.merge(links, on='movieId')
movies_links.to_csv('data/movies_links_clean.csv', index=False)

# Set inital variables

user_name = '__USER__'
name = 'Movie Recommendation Assistant'


# Define defualt response
defualt_responses = {
    "what's your name?": [
        "my name is {0}".format(name),
        "they call me {0}".format(name),
        "I go by {0}".format(name)
        ],
    "what's your name": [
        "my name is {0}".format(name),
        "they call me {0}".format(name),
        "I go by {0}".format(name)
    ],
    "who are you?": [
        "my name is {0}".format(name),
        "they call me {0}".format(name),
        "I go by {0}".format(name)
        ],
    "who are you": [
        "my name is {0}".format(name),
        "they call me {0}".format(name),
        "I go by {0}".format(name)
        ],
    "how are you": [
        "Great!", 
        "Doing well!",
        "Stuck at home mostly..Thanks Covid..",
        "Rough week.."],
    "why":[
        "There's no why. Let's talk about movies! What's your favorite movie?",
        "You ask too much. Let's talk about movies! What's your favorite movie?",
        "Hard to tell..Let's talk about movies! What's your favorite movie?",
    ],
    "default": ["default message"],
    "question": [
        "That's a great question!", 
        'you tell me!',
        "Nice question! Unfortunately, I don't know the answer.:("
        ],
    "statement": [
        'tell me more!',
        'why do you think that?',
        'how long have you felt this way?',
        'I find that extremely interesting',
        'can you back that up?',
        'oh wow!',
        ':)'
        ]
}

# Define intents
greetings = ['hey', 'hello', 'hi', 'hello there', 'hi robot', 'good morning', 'good evening', 'moin', 'hey there', "let's go", 'hey dude', 'goodmorning', 'goodevening', 'good afternoon', 'yo']
affirm = ['yes', 'y', 'indeed', 'of course', 'sounds good', 'correct']
deny = ['no', 'n', 'never', "I don't think so"," don't like that", 'no way', 'not really']
goodbye = ['see u', 'cu',' good by', 'see you later', 'good night', 'bye', 'goodbye', 'have a nice day', 'see you around', 'bye bye', 'see you later', '88']

# Define the INIT state
INIT = 0

# Define the GREETING state
GREETING = 1

# Define the CHOOSE_MOVIE state
CHOOSE_GENRE = 2

# Define the PROVIDE_GENRE state
PROVIDE_GENRE = 3

# Define the CONFIRM_MOVIE state
CONFIRM_MOVIE = 4

# Define the INITIAL_MOVIE state
INITIAL_MOVIE = 5

# Define the MOVIE_RECOMMENDATION state
MOVIE_RECOMMENDATION = 6

# Define the DONE state
BYE = 7


# Define policy
policy = {
    (INIT, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (INIT, "goodbye"): (BYE, f"Bye {user_name}! Have a good day and enjoy your movie!"),
    (INIT, "none"): (INIT, f"Sorry {user_name}, I don't quite understand...Would you tell me what specific movie you are interested in again?"),
    (INIT, "specify_movie"): (CONFIRM_MOVIE, f"Hey! we found some possible matches in the database."),
    (GREETING, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (GREETING, "specify_movie"): (CONFIRM_MOVIE, f"Hey! we found some possible matches in the database."),
    (GREETING, "goodbye"): (BYE, f"Bye {user_name}! Have a good day and enjoy your movie!"),
    (GREETING, "none"): (CHOOSE_GENRE, "Sorry we can't find that movie in our database. Would you tell me what types of movie you usually watch?"),
    (CHOOSE_GENRE, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (CHOOSE_GENRE, "specify_genre"): (PROVIDE_GENRE, "Here I find some movies you may like!"),
    (CHOOSE_GENRE, "specify_movie"): (CONFIRM_MOVIE, f"Hey! we found some possible matches in the database.Please choose one by specifying the order in the provided list: (Note: the order starts from 1)"),
    (CHOOSE_GENRE, "goodbye"): (BYE, f"Bye {user_name}! Have a good day and enjoy your movie!"),
    (CHOOSE_GENRE, "none"): (CHOOSE_GENRE, "Sorry, I can't find any movie in this type. Would you try again?"),
    (CONFIRM_MOVIE, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (CONFIRM_MOVIE, "comfirm_movie"): (INITIAL_MOVIE, f"Perfect! Would you want some recommendations?"),
    (CONFIRM_MOVIE, "none"): (CONFIRM_MOVIE, f"Looks like the order you provide is not right. Please try again!"),
    (INITIAL_MOVIE, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (INITIAL_MOVIE, "affirm"): (MOVIE_RECOMMENDATION, "Here are the recommendations!"),
    (INITIAL_MOVIE, "deny"): (MOVIE_RECOMMENDATION, "Bye! See you next time."),
    (INITIAL_MOVIE, "goodbye"): (BYE, f"Bye {user_name}! Have a good day and enjoy your movie!"),
    (INITIAL_MOVIE, "none"): (MOVIE_RECOMMENDATION, "Sorry, I don't understand!"),
    (MOVIE_RECOMMENDATION, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (MOVIE_RECOMMENDATION, "goodbye"): (BYE, f"Bye {user_name}! Have a good day and enjoy your movie!"),
    (BYE, "greetings"): (GREETING, f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?"),
    (BYE, "specify_movie"): (CONFIRM_MOVIE, f"Hey! we found some possible matches in the database."),
}

# Create the list of testing messages
messages = [
    "Hi",
    "lion pasdasdajs hdjsakhdjkas",
    "Animation",
    "what's your name", 
    "who?", 
    "hi",
    "Lian kin",
    '1',
    'yes',
    'Hi',
    'bye',
    'Hey',
    "Beast",
    '11',
    'No',
    'Hi',
    "Beauty",
    'Documentary',
    'bye',
    'how are you'
]

def send_message(state, message):
  #  print("USER : {}".format(message))
    new_state, response = respond(state, message)
   # print("BOT : {}".format(response))
    return new_state, response

def respond(state, message):
    message = message.lower()
    for question in [q.lower() for q in defualt_responses.keys()]:
        if re.search(fr'^{message}[?]?$', question):
            response = random.choice(defualt_responses[message])
            new_state = INIT
            return new_state, response
        elif message.endswith("?"):
            response = random.choice(defualt_responses['question'])
            new_state = INIT
            return new_state, response
    try:
        (new_state, response) = policy[(state, interpret_intent(message))]
    except:
        (new_state, response) = policy[(INIT, 'none')]

    return new_state, response

def fuzzy_match(movie_in_search, verbose=True):
    match_tuple = []
    # get match
    for t in range(len(movies['clean_title'])):
        ratio = fuzz.ratio(movies['clean_title'][t].lower(), movie_in_search.lower())
        if ratio >= 70:
            match_tuple.append((movies['title'][t], ratio))
    # sort
    match_tuple = sorted(match_tuple, key=lambda x: x[1])[::-1]
    if not match_tuple:
        return
    if verbose:
        all_options = [(i+1, x[0]) for i, x in enumerate(match_tuple)]
    try: 
        return all_options
    except:
        return 

# choice = 0
def select_movie(choice, all_options):
    try:
        return all_options[choice-1][1]
    except:
        return


def interpret_intent(message):
    message = str(message).lower()
    for greet in greetings:
        if re.search(fr'\b{greet}\b', message):
            return 'greetings'
    for bye in goodbye:
        if re.search(fr'\b{bye}\b', message):
            return 'goodbye'
    for pos in affirm:
        if re.search(fr'\b{pos}\b', message):
            return 'affirm'
    for neg in deny:
        if re.search(fr'\b{neg}\b', message):
            return 'deny'
    for genre in genres_list:
        if re.search(fr'^{genre}$', message):
            return 'specify_genre'
    if re.search(fr'^\d$', message):
        return 'comfirm_movie'
    if fuzzy_match(message):
        return 'specify_movie'
    return 'none'


# Call send_message() for each message
if __name__ == '__main__':
    state = INIT
    for message in messages:    
        state, response = send_message(state, message)
        print('user ', message)
        print('bot ', response)











# ========= Spare code ============

# Define the policy rules
# policy = {
#     (INIT, "specify_movie"): (INITIAL_MOVIE, "Perfect! Would you want some recommendations?"),
#     (INIT, "none"): (CHOOSE_GENRE, "Sorry we can't find that movie in our database. Would you tell me what types of movie you usually watch?"),
#     (CHOOSE_GENRE, "specify_genre"): (PROVIDE_GENRE, "(provide movies with certain genre)"),
#     (CHOOSE_GENRE, "none"): (CHOOSE_GENRE, "Sorry, I can't find any movie in this type. Would you try again?"),
#     (INITIAL_MOVIE, "affirm"): (MOVIE_RECOMMENDATION, "Here are the recommendations!"),
#     (INITIAL_MOVIE, "deny"): (MOVIE_RECOMMENDATION, "Bye! See you next time."),
#     (INITIAL_MOVIE, "none"): (MOVIE_RECOMMENDATION, "Sorry, I don't understand!"),
# }

# # Define policy()
# def policy(intent):
#     # Return "do_pending" if the intent is "affirm"
#     if intent == "affirm":
#         return "do_pending", None
#     # Return "Ok" if the intent is "deny"
#     if intent == "deny":
#         return "Ok", None
#     if intent == "order":
#         return "Unfortunately, the Kenyan coffee is currently out of stock, would you like to order the Brazilian beans?", "Alright, I've ordered that for you!"

# # Define send_message()
# def send_message(pending, message):
#     print("USER : {}".format(message))
#     action, pending_action = policy(interpret(message))
#     if action == "do_pending" and pending is not None:
#         print("BOT : {}".format(pending))
#     else:
#         print("BOT : {}".format(action))
#     return pending_action
    
# # Define send_messages()
# def send_messages(messages):
#     pending = None
#     for msg in messages:
#         pending = send_message(pending, msg)

# # Send the messages
# send_messages([
#     "I'd like to order some coffee",
#     "ok yes please"
# ])

# ========= End ============