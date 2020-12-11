import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import time
import plotly.graph_objects as go
import dash_trich_components as dtc
import pandas as pd

import os
from dash_player.DashPlayer import DashPlayer
from dash_chatbots.chatbot_v4 import send_message, fuzzy_match, select_movie
from dash_chatbots.knn_recommender_v1 import *
from dash_chatbots.get_movie_info import *

# setup app with stylesheets
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


def textbox(text, box="bot"):
    style = {
        "max-width": "55%",
        "width": "max-content",
        "padding": "10px 15px",
        "border-radius": "25px",
        "margin-top": '5px',
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





def create_pie_chart(metric_name, ratio1, ratio2):
    fig = go.Figure(go.Pie(labels=['rating', 'grey'], 
                           values=[ratio1, ratio2],
                           textposition = 'outside',
                           textinfo='none',
                           hoverinfo='none',
                           sort=False,
                           insidetextorientation='radial', 
                           marker_colors=['#f5be41', 'lightgrey'], 
                           hole=.6))
    
    if metric_name == 'RottenTomatoesRating':
        metric_name = 'Rotten Tomatoes'
        ratio1 = '{}%'.format(ratio1)
    fig.update_layout(margin={"r":2,"t":2,"l":2,"b":2},
                      annotations=[dict(text=str(ratio1), x=0.5, y=0.5, yanchor='middle', font_size=24, showarrow=False)],
                      showlegend=False, uniformtext_mode='hide')
    
    return fig


def create_movie_info(user_input):
    
 #   user_input = 'Monsters, Inc'
    
    df = get_movie_info(user_input, 'e4beb4c3')
  #  df = pd.read_csv('C://Users/admin/Documents/Python2/project 3/monsters_inc_info.csv')

        
    basic_info0 = html.P(df['Summary'].values, style={'margin-top':'10px', 'margin-bottom':'10px'})
    
    colors = ['primary', 'danger', 'success', 'warning', 'info', 'dark']
    
    genre_badges = html.Span(
    [
        dbc.Badge(genre, pill=True, color=colors[i % len(colors)], style={'margin-right':'5px'}) for i, genre in enumerate(df.loc[0, 'Genre'].split(','))
        ]
    )

    basic_info2 = [dcc.Markdown('**{}:** {}'.format(col, df.loc[0, col]), style={'margin-top':'0px', 'margin-bottom':'0px'}) for col in ['Directors', 'Writers', 'Actors', 'Awards']]
        
    

    
    rating_graphs = dbc.FormGroup(
        dbc.Row(
            [
                dbc.Col([html.H5('IMDB', style={'text-align':'center', 'margin-bottom':'10px', 'margin-top':'10px'}),
                         dcc.Graph(figure=create_pie_chart('IMDB', float(df['imdbRating']), 10-float(df['imdbRating'])), style={'height':'180px'})]),
                dbc.Col([html.H5('Metascore', style={'text-align':'center', 'margin-bottom':'10px', 'margin-top':'10px'}),
                         dcc.Graph(figure=create_pie_chart('Metascore', int(df['Metascore']), 100-int(df['Metascore'])), style={'height':'180px'})]),
                dbc.Col([html.H5('Rotten Tomatoes', style={'text-align':'center', 'margin-bottom':'10px', 'margin-top':'10px'}),
                         dcc.Graph(figure=create_pie_chart('RottenTomatoesRating', int(df['RottenTomatoesRating'].str[:-1]), 100-int(df['RottenTomatoesRating'].str[:-1])), style={'height':'180px'})]),
                ],
            style={'margin-top': '15px', 
                   #'height': '250px'
                   },
            align='center',
            justify='center'
            )
        )
    
    trailer = html.Div(
                        children=DashPlayer(
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
    reviews_info = html.P([textbox('"{}".'.format(review)) for review in reviews])
    
    movie_info = dbc.FormGroup(
        [
         dbc.Row(html.H2(df.loc[0, 'Title'])),
         dbc.Row([genre_badges, html.P(' | {} | {} '.format(df.loc[0, 'Year'], df.loc[0, 'Runtime']))]),
         dbc.Row(
             [
                 dbc.Col([dbc.CardImg(src=df['Poster'], style={'align':'center'})], width=3),
                 dbc.Col([trailer], width=9)
                 ],
             justify='center',
             align='center'
             ),
      #   html.Hr(),
         dbc.Row(dbc.Col(dbc.Tabs(
             [
                 dbc.Tab(rating_graphs, label='Ratings'),
                 dbc.Tab(dbc.Row(dbc.Col([basic_info0]+basic_info2), justify='begin', align='center'), label='Summary'),
                 dbc.Tab(dbc.Row(dbc.Col(reviews_info), justify='begin', align='center'), label='Reviews'),
                 ]
             )), 
                 style={'margin-top':'25px', 'height': '300px', "overflow-y": "auto"})

        ],
        style={"width": "90%",  "max-width": "1000px", "margin": "auto",}
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
             #   speed=2000,
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
    children = [loading],
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
    style={"width": "100%",  "max-width": "1000px", "margin": "auto", 'margin-top': '15px', 'margin-bottom':'0px'},
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.InputGroupAddon(dbc.Button("Submit", id="submit"), addon_type="append",),
    ],
)



chat_box = dbc.Card(
    [
     conversation,
     html.Hr(),
     chat_input,
     html.P(id='typing_status')
     ],
    body=True,
    )



app.layout = dbc.Container(
    [   dcc.Store(id="store-conversation", data={'text':[], 'role':[]}),
        dcc.Store(id='bot-store', data={'text':[], 'state':[]}),
        dcc.Store(id='user-store', data={'text':[]}),
        dcc.Store(id='state', data={'previous':0, 'last_sent':'', 'movie':'', 'options':[]}),

        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Movie Chatbot", style={'margin-bottom':'15px'}),
                        html.Hr(),
                        html.P('This chatbot can provide information about movies you are interested in and suggest similar movies for you!')
                        ], 
                    width=3,
                    style={'margin-left': '60px'}),
                
                dbc.Col(
                    [
                        chat_box
                        ], 
                    width=7),
            ],
            align='center',
            justify='around',
            style={'margin-top':'30px'}
        ),
    ],
    id="main-container",
    style={"display": "flex", "flex-direction": "column"},
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
     State('state', 'data')]
)
def update_bot_response(n_clicks, n_submit, user_input, chat_box, state):
    
    previous_state = state['previous']
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    chat_box = chat_box[:-1]
    placeholder = 'Say "Hi" to start the conversation...'
        
    if 'submit' in changed_id:
        user_box = textbox(user_input, 'user')  
        chat_box = chat_box + [user_box]
        
        new_state, response = send_message(previous_state, user_input)
        state['previous'] = new_state
        state['last_sent'] = ''
        
        
        if response == "Hey! we found some possible matches in the database.Please choose one by specifying the order in the provided list: (Note: the order starts from 1)":
            all_options = fuzzy_match(user_input)
            all_options_text = ['{0}.{1}\n  '.format(i, title) for i, title in all_options]
            response_box1 = textbox(response, 'bot') 
            response_box2 = textbox(all_options_text, 'bot') 
            chat_box = chat_box + [response_box1, response_box2]
            state['options'] = all_options
        
        
        elif response == 'Perfect! Would you want some recommendations?':     
            movie = select_movie(int(user_input), state['options'])
            response_box1 = textbox('Perfect! Here you go', 'bot')        
            info_card = dbc.FormGroup([html.Hr(), create_movie_info(movie), html.Hr()]) 
            response_box2 = textbox('Would you want some recommendations?', 'bot')
            chat_box = chat_box + [response_box1, info_card, response_box2]
            placeholder = 'Type yes or no...'
            state['movie'] = movie
            

        elif (response == 'Here are the recommendations!') | (response == "Here I find some movies you may like!"):
            response_box1 = textbox(response, 'bot')     

            titles = ['Toy Story', 'Monster University', 'Finding Nemo', 'The Incredibles']
            poster_links = ['https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BMTUyODgwMDU3M15BMl5BanBnXkFtZTcwOTM4MjcxOQ@@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BZTAzNWZlNmUtZDEzYi00ZjA5LWIwYjEtZGM1NWE1MjE4YWRhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_UX182_CR0,0,182,268_AL_.jpg',
                            'https://m.media-amazon.com/images/M/MV5BMTY5OTU0OTc2NV5BMl5BanBnXkFtZTcwMzU4MDcyMQ@@._V1_UX182_CR0,0,182,268_AL_.jpg'
                            ]
            
            if (response == "Here I find some movies you may like!"):
                
               # user_input = 'Adventure'
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
            
            response_box2 = textbox('If you want to get more information, just type the movie name.', 'bot')
            chat_box = chat_box + [response_box1, info_card, response_box2]
            state['last_sent'] = 'If you want to get more information, just type the movie name.'
            state['previous'] = 1
            placeholder = 'Type a movie name...'
            
        
            
     #   elif response=="Sorry we can't find that movie in our database. Would you tell me what types of movie you usually watch?":
         #   placeholder = 'Type Action/Adventure/Animation/Comedy/Romance/Horror/Sci-Fi/Documentary...'
            
            
        else:
            response_box1 = textbox(response, 'bot')      
            chat_box = chat_box + [response_box1]
            
    chat_box = chat_box + [loading]
            
    return chat_box, '', placeholder, state, [html.P('')]





# Main
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
