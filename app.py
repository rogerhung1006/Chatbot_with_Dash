import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import time
import plotly.graph_objects as go
import dash_trich_components as dtc
import pandas as pd
import numpy as np
from copy import copy

import os
from dash_player.DashPlayer import DashPlayer
from dash_chatbots.chatbot_v4 import send_message, fuzzy_match, select_movie
from dash_chatbots.knn_recommender_v1 import *
from dash_chatbots.get_movie_info import *

# setup app with stylesheets
app = dash.Dash(external_stylesheets=[dbc.themes.SKETCHY])
#THEMES
## SKETCHY, DARKLY, LUMEN, MINTY



color_dict= {'adventure': 'danger', 
  'war':'primary',
  'fantasy':'warning', 
  'musical':'warning', 
  'horror':'dark', 
  'sci-fi':'success', 
  'imax':'info', 
  'mystery':'dark', 
  'crime':'danger',
  'thriller':'dark', 
  'comedy':'warning', 
  'drama':'info', 
  'action': 'danger', 
  'animation':'warning', 
  'documentary':'success',
  'western':'info', 
  '(no genres listed)':'info', 
  'children': 'warning', 
  'film-noir':'dark', 
  'romance':'danger'}

def textbox(text, box="bot"):
    style = {
        "max-width": "55%",
        "width": "max-content",
        "padding": "10px 15px",
        "border-radius": "25px",
        "margin-top": '10px',
        'border-width': 'thin'
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = '10px'

        color = "primary"
        inverse = True

    elif box == "bot":
        style["margin-left"] = '10px'
        style["margin-right"] = "auto"

        color = "light"
        inverse = False
        

    else:
        raise ValueError("Incorrect option for `box`.")
        

    return dbc.Card(text, style=style, body=True, color=color, inverse=inverse)



def review_box(review):
    
    style = {
    "max-width": "90%",
    "width": "max-content",
    "padding": "10px 15px",
    "border-radius": "25px",
    "margin-top": '15px',
    "margin-left": '10px',
    'margin-right': "auto",
    'border-width': 'thin'}
    
    return dbc.Card(review, style=style, body=True, color='info', outline=True)
    



def create_pie_chart(metric, ratio1, ratio2, empty_mode=False):


    fig = go.Figure(go.Pie(labels=['rating', 'grey'], 
                           values=[ratio1, ratio2],
                           textposition = 'outside',
                           textinfo='none',
                           hoverinfo='none',
                           sort=False,
                           insidetextorientation='radial', 
                           marker_colors=['#f5be41', 'lightgrey'], 
                           hole=.6))
  
    if metric == 'RottenTomatoesRating':
        ratio1 = '{}%'.format(ratio1)
          
    if empty_mode:
        ratio1 = 'N/A'
  
    fig.update_layout(margin={"r":2,"t":2,"l":2,"b":2},
                      annotations=[dict(text=str(ratio1), x=0.5, y=0.5, yanchor='middle', font_size=24, showarrow=False, font=dict(family='cursive'))],
                      showlegend=False, uniformtext_mode='hide',
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    
    return fig



def create_pie_chart_group(df):

    graph_list = []
    
    name_dict = {'imdbRating':'IMDB', 'Metascore':'Metascore', 'RottenTomatoesRating':'Rotten Tomatoes'}

        
    for col in ['imdbRating', 'Metascore', 'RottenTomatoesRating']:
        if (col in df.columns) &  (df.loc[0, col]!='N/A'):
            
            ratio1 = df.loc[0, col]
            
            if col == 'imdbRating':
                ratio1, ratio2 = float(ratio1), 10 - float(ratio1)
                
            elif col== 'Metascore':
                ratio1, ratio2 = int(ratio1), 100 - int(ratio1)    
                
            else:
                ratio1, ratio2 = int(ratio1[:-1]), 100 - int(ratio1[:-1])   

            pie_chart = create_pie_chart(col, ratio1, ratio2)
                                         
        else:
           # continue
            pie_chart = create_pie_chart(col, 0, 100, True)
            
        element = dbc.Col([html.H4(name_dict[col], 
                                   style={'text-align':'center', 'margin-bottom':'10px', 'margin-top':'10px'}),
                           dcc.Graph(figure=pie_chart, style={'height':'150px'})])
        
        graph_list.append(element)


    pie_chart_group = dbc.FormGroup(dbc.Row(graph_list, style={'margin-top': '15px'}, align='center', justify='center'))
    
    return pie_chart_group



def create_movie_info(user_input):
          
    df = get_movie_info(user_input, 'e4beb4c3')
        
    basic_info0 = html.P(df.loc[0,'Summary'])
       
    colors = ['primary', 'danger', 'success', 'warning', 'info', 'dark']
    
    genre_badges = html.H5(
        [
            dbc.Badge(genre, 
                      pill=True, 
                      color=colors[i % len(colors)], 
                      style={'margin-right':'5px'}
                      ) 
            for i, genre in enumerate(df.loc[0, 'Genre'].split(','))
            ]
        )

    basic_info2 = [
        dcc.Markdown(
            '**{}:** {}'.format(col, df.loc[0, col]), 
            style={'margin-top':'0px', 'margin-bottom':'0px'}
            ) 
        for col in ['Directors', 'Writers', 'Actors', 'Awards']
        ]
       
    
    rating_graphs = create_pie_chart_group(df)
    
    trailer = html.Div(
        DashPlayer(
            url=get_trailer(df.loc[0, 'Title'], df.loc[0, 'Year']),
            controls=True,
            playing=False,
            volume=1,
            width="100%",
            height="100%",
            ),
        style={'height':'250px'}
        )
    
    
    reviews = get_reviews(user_input) 
    
    reviews_info = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Row(dbc.CardImg(src='https://github.com/crystalwanyulee/plotly_dash_projects/blob/main/project%203/images/user.png?raw=true', 
                                                style={'height':'64px', 'width':'64px', 'margin-top':'30px'}), 
                                            justify='center', align='center'),
                                    dbc.Row(
                                        [
                                            html.P(rating, style={'color': '#F09304', 'font-size': '20px'}),
                                            html.P('/10', style={'font-size': '12px'})], 
                                        justify='center', align='center')
                                    ],
                                ),

                            ],
                        width=2,
                        align='center',
                        ),
                    dbc.Col(review_box('"{}"'.format(review)), align='center', width=9)
                    ], 
             #   style={'margin-top':'10px'}, 
                justify='center', align='center') 
            for rating, review in reviews
            ]
        )
    
    
    movie_info = dbc.FormGroup(
        [
         dbc.Row(html.H1(df.loc[0, 'Title'])),
         dbc.Row(
             [
                 genre_badges, 
                 html.P(' | {} | {} '.format(df.loc[0, 'Year'], df.loc[0, 'Runtime']), 
                        style={'font-size': '16px', 'margin-top':'5px'})
                 ],
             justify='begin',
             align='center',
             style={'margin-top':'5px', 'margin-bottom':'0px'}
             ),
         dbc.Row(
             [
                 dbc.Col(
                     [dbc.CardImg(src=df.loc[0,'Poster'], style={'align':'center', 'max-height':'250px'})], 
                     width=3),
                 dbc.Col(
                     [trailer], 
                     width=9)
                 ],
             justify='begin',
             align='center',
             style={'margin':'auto', 'height': '270px', 'margin-top':'5px'}
             ),

         dbc.Row(dbc.Col(dbc.Tabs(
             [
                 dbc.Tab(rating_graphs, label='Ratings'),
                 dbc.Tab(dbc.Row(dbc.Col([basic_info0]), 
                                 justify='begin', align='center', 
                                 style={'margin-top':'15px', 'margin-left':'15px'}), 
                         label='Summary'),
                 dbc.Tab(dbc.Row(dbc.Col(basic_info2), 
                                 justify='begin', align='center', 
                                 style={'margin-top':'15px', 'margin-left':'15px'}), 
                         label='Other Info'),
                 dbc.Tab(dbc.Row(dbc.Col(reviews_info), 
                                 justify='begin', align='center', 
                                 style={'margin-top':'15px'}), 
                         label='Reviews'),
                 ]
             )
             ), 
             style={'margin-top':'10px', 'height': '270px', "overflow-y": "auto", 'border-width': 'thin'}
             )
        ],
        style={"width": "90%",  "max-width": "1000px", "margin": "auto", 'margin-top':'5px'}
    )
    
    return movie_info


def carousel_card(title, image_link):
    
    image_card = dbc.FormGroup(
        [
            dbc.CardImg(src=image_link),
            html.P(title, style={'text-align':'center', 'margin-bottom':'5px', 'margin-top':'5px', 'max-width':'150px', 'height':'50px'})
            ],
        style={'height':'300px'}
        )
    
    return image_card
    


def create_carousel(titles, poster_links):

    carousel = dtc.Carousel([
               	carousel_card(title, poster_links[i])
                for i, title in enumerate(titles)
                ],
                slides_to_scroll=1,
                swipe_to_slide=True,
                autoplay=False,
                infinite=True,
                arrows=True,
                dots=True,
                variable_width=True,
                center_mode=True,
                responsive=[
                {
                    'breakpoint': 991
                    }
                ],
                style = {'margin-top':'15px', 'margin-bottom':'20px'}
    		)
    
    return carousel



loading =  dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        )

conversation = html.Div(
    children = [textbox('Please enter your name to start!'), loading],
    style={
        "width": "100%",
        "max-width": "1000px",
        "height": "75vh",
        "margin": "auto",
        "overflow-y": "auto",
    },
    id="display-conversation",
)



chat_input = dbc.InputGroup(
    [
        dbc.Input(id="user-input", 
                  placeholder="Enter your name...", 
                  type="text", 
                  style={'font-family':'cursive', 'font-weight': 'normal', 'border-width': 'thin'}),
        dbc.InputGroupAddon(
            dbc.Button("Submit", 
                       id="submit", 
                       color='info', 
                       style={'font-family':'cursive', 'border-width': 'thin'}), 
            addon_type="append"),
    ],
    style={"width": "100%",  "max-width": "1000px", "margin": "auto", 'margin-top': '5px', 'margin-bottom':'-10px'},
    size="mg"
)



chat_box = dbc.Card(
    [
     conversation,
     html.Hr(),
     chat_input,
     html.P(id='typing_status')
     ],
    body=True,
    outline=True,
    color='info',
    style={'border-top-right-radius': '0px',
           'border-top-left-radius': '0px',
           'border-bottom-right-radius': '15px',
           'border-bottom-left-radius': '15px',}
    )



app.layout = dbc.Container(
    [   dcc.Store(id="store-conversation", data={'text':[], 'role':[]}),
        dcc.Store(id='bot-store', data={'text':[], 'state':[]}),
        dcc.Store(id='user-store', data={'text':[]}),
        dcc.Store(id='state', data={'previous':-1, 'last_sent':'', 'movie':'', 'options':[], 'user_name':''}),


        dbc.Row(
            [

                
                dbc.Col(
                    [
                        dbc.Card(
                            [html.H3('Movie Recommendation Assistant', style={'margin':'auto', 'margin-top':'-5px'})],
                            color='info',
                            inverse=True,
                            style={'border-top-right-radius': '15px',
                                   'border-top-left-radius': '15px',
                                   'border-bottom-right-radius': '0px',
                                   'border-bottom-left-radius': '0px', 
                                   'height':'60px'},
                            body=True),
                        chat_box
                        ], 
                    width=6),
            ],
            align='center',
            justify='around',
            style={'margin-top':'30px'}
        ),
    ],
    id="main-container",
    style={"display": "flex", 
           "flex-direction": "column",
           'font-family':'cursive', 'font-weight': 'normal'},
    fluid=True
)

   
@app.callback(
    [Output("display-conversation", "children"),
     Output("user-input", "value"),
     Output('user-input', 'placeholder'),
     Output('state', 'data'),
     Output('loading-output-1', 'children')], 
    [Input("submit", "n_clicks"),
     Input("user-input", "n_submit")],
    [State("user-input", "value"),
     State("display-conversation", "children"),
     State('state', 'data'),
     State('user-input', 'placeholder')]
)
def update_bot_response(n_clicks, n_submit, user_input, chat_box, state, placeholder):
    
    user_name = state['user_name']
    previous_state = state['previous']
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    chat_box = chat_box[:-1]
        
    if 'submit' in changed_id:
        
        if (previous_state == -1):
            if user_input is None:
                user_input = 'User'

            user_box = textbox(user_input, 'user')  
            chat_box = chat_box + [user_box]
            user_name = user_input
            state['user_name'] = user_input
            user_input = 'Hi'
            

        user_box = textbox(user_input, 'user')  
        chat_box = chat_box + [user_box]
        
        new_state, response = send_message(previous_state, user_input)
        response = response.replace('__USER__', user_name)
        state['previous'] = new_state
        
        if (previous_state == -1):
            chat_box = chat_box[:-1]
            response_box1 = textbox(f"Hi {user_name}! Nice to meet you!", 'bot') 
            response_box2 = textbox('Would you like to tell me what specific movie you are interested in?', 'bot') 
            chat_box = chat_box + [response_box1, response_box2]
            placeholder = 'Please type a movie name...'

        
        elif response == "Hey! we found some possible matches in the database.":
            
            if  (state['last_sent'] == 'Type a movie name to get more information about the recommendations'):
                user_input_options = np.array(list(list(zip(*fuzzy_match(user_input)))[1]))
                rec_movies = np.array(state['recommend'])
                repeated = np.in1d(rec_movies, user_input_options)
                movies = rec_movies[repeated]
                
                if repeated.sum() > 1:
                    response = "Hey! Can you specify which movie you are looking for?"
                    response2 = 'Please choose one by specifying the order in the provided list: (Note: the order starts from 1)'
                    all_options = [(i+1, title) for i, title in enumerate(movies)]
                    all_options_text = [html.P('({0}) {1}'.format(i, title)) for i, title in all_options]
                    state['previous'] = 2
                    placeholder = 'Please type a number or enter "Hi" to restart......'
                    
                    response_box1 = textbox(response, 'bot') 
                    response_box2 = textbox(html.P([html.P(response2)] + all_options_text), 'bot') 
                    chat_box = chat_box + [response_box1, response_box2]
                    state['options'] = all_options
                    placeholder = 'Please type a number or enter "Hi" to restart......'
                    
                elif repeated.sum() == 1:
                    movie = movies[0]
                    response_box1 = textbox('Here you go!', 'bot')        
                    info_card = dbc.FormGroup([html.Hr(), create_movie_info(movie), html.Hr()]) 
                    response_box2 = textbox('Type a movie name to get more information about the recommendations', 'bot')
                    chat_box = chat_box + [response_box1, info_card, response_box2]
                    state['previous'] = previous_state
                    placeholder = 'Please type a movie name or enter "Hi" to restart...'
                    
                else:
                    response = 'Sorry! I cannot understand that. Please ensure you provide a correct movie name.'
                    response_box1 = textbox(response, 'bot') 
                    chat_box = chat_box + [response_box1]
                    state['previous'] = previous_state
                    placeholder = 'Please type a movie name or enter "Hi" to restart...'
                
            else:
                all_options = fuzzy_match(user_input)
                all_options_text = [html.P('({0}) {1}'.format(i, title)) for i, title in all_options]
                response2 = 'Please choose one by specifying the order in the provided list: (Note: the order starts from 1)'

                response_box1 = textbox(response, 'bot') 
                response_box2 = textbox(html.P([html.P(response2)] + all_options_text), 'bot') 
                chat_box = chat_box + [response_box1, response_box2]
                state['options'] = all_options
                placeholder = 'Please type a number or enter "Hi" to restart......'
                state['last_sent'] = ''
        
        
        elif response == 'Perfect! Would you want some recommendations?':     
            
            try:
                
                movie = select_movie(int(user_input), state['options'])
                response_box1 = textbox('Perfect! Here you go', 'bot')        
                info_card = dbc.FormGroup([html.Hr(), create_movie_info(movie), html.Hr()]) 
                response_box2 = textbox('Would you want some recommendations?', 'bot')
                chat_box = chat_box + [response_box1, info_card, response_box2]
                placeholder = 'Please type yes or no, or enter "Hi" to restart......'
                state['movie'] = movie
                state['last_sent'] = ''
                
                
            except:
                response='Sorry, we cannot find any information about this movie. Please enter other movies.'
                response_box1 = textbox(response, 'bot') 
                chat_box = chat_box + [response_box1]
                state['previous'] = 0
                placeholder = 'Please type a movie name or enter "Hi" to restart......'
                state['last_sent'] = ''
            

        elif (response == 'Here are the recommendations!') | (response == "Here I find some movies you may like!"):
            response_box1 = textbox(response, 'bot')     

            titles = ['Toy Story', 'Monster University', 'Finding Nemo', 'The Incredibles']
            poster_links = ['https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BMTUyODgwMDU3M15BMl5BanBnXkFtZTcwOTM4MjcxOQ@@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BZTAzNWZlNmUtZDEzYi00ZjA5LWIwYjEtZGM1NWE1MjE4YWRhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BMTY5OTU0OTc2NV5BMl5BanBnXkFtZTcwMzU4MDcyMQ@@._V1_UX182_CR0,0,182,268_AL_.jpg'
                            ]
            
            if (response == "Here I find some movies you may like!"):
                
                rec_movies = get_top_rating_movies(user_input)
                poster_links = get_movie_posters(rec_movies['imdbId'])
                titles = rec_movies.loc[rec_movies.imdbId.isin(poster_links.keys()), 'title']
                poster_links = list(poster_links.values())
                
            else:
                
                titles = make_recommendation(model_knn=model_knn,
                                             data=r_matrix_sparse,
                                             movie_in_search=state['movie'],
                                             mapper=movie_to_idx,
                                             n_recommendations=20)
                
                if len(titles) == 0:
                    genre = get_genre(state['movie'])
                    rec_movies = get_top_rating_movies(genre)
                    poster_links = get_movie_posters(rec_movies['imdbId'])
                    titles = rec_movies.loc[rec_movies.imdbId.isin(poster_links.keys()), 'title']
                    poster_links = list(poster_links.values())
                    
                else:
                    poster_links = get_movie_posters([get_imdbid(title) for title in titles])
                    titles = [get_title(imdbId) for imdbId in poster_links.keys()]
                    poster_links = list(poster_links.values())
  
            
      
            info_card = dbc.FormGroup([html.Hr(), create_carousel(titles, poster_links), html.Hr()])
            
            response_box2 = textbox('Type a movie name to get more information about the recommendations', 'bot')
            chat_box = chat_box + [response_box1, info_card, response_box2]
            state['last_sent'] = 'Type a movie name to get more information about the recommendations'
            state['previous'] = 1
            state['recommend'] = titles
            placeholder = 'Type a movie name or enter "Hi" to restart......'
                      
            
        else:
            response_box1 = textbox(response, 'bot')      
            chat_box = chat_box + [response_box1]
            placeholder = 'Type "Hi" to restart the conversation...'
            
            if new_state == 1:
                placeholder = 'Please type a movie name...'
                state['last_sent'] = ''
                
                
            elif new_state == 2:
                placeholder = 'Please type Action, Adventure, Animation, Comedy, Romance, Horror, Sci-Fi, or Documentary...'
                
                if (state['last_sent'] == 'Type a movie name to get more information about the recommendations'):
                    if response == f"Hi {user_name}! Would you like to tell me what specific movie you are interested in?":
                        state['previous'] = new_state
                        state['last_sent'] = ''
                        
                    else:
                        response = 'Sorry! I cannot understand that. Please ensure you provide a correct movie name.'
                        state['previous'] = previous_state
                    
                    placeholder = 'Please type a movie name or enter "Hi" to restart...'
                    response_box1 = textbox(response, 'bot') 
                    chat_box = chat_box + [response_box1]
                    
                else:
                    state['last_sent'] = ''
                    
            else:
                 state['last_sent'] = ''
            
    chat_box = chat_box + [loading]
            
    return chat_box, '', placeholder, state, [html.P('')]



# Main
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
