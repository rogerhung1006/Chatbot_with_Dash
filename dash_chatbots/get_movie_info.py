import requests
from bs4 import BeautifulSoup
import pandas as pd
from youtube_search import YoutubeSearch
from codecs import encode, decode
import ast
from gensim.summarization.summarizer import summarize
import os
os.chdir('C://Users/admin/Documents/Python2/project 3/dash_chatbots')
#key = 'e4beb4c3'
# key2 = 'd11685fd'
movies_links = pd.read_csv('data/movies_links.csv', converters={'imdbId': lambda x: str(x)})
ratings = pd.read_csv('data/rating_by_genre.csv')
movies = pd.read_csv('data/movies.csv')


def get_imdbid(movie):
    imdbId = movies_links.loc[movies_links.title == movie, 'imdbId'].iloc[0]
    return imdbId

def get_title(imdbId):
    title = movies_links.loc[movies_links.imdbId == imdbId, 'title'].iloc[0]
    return title

def get_genre(movie):
    genre = ratings.loc[ratings.title == movie, 'genres'].values[0].split('|')[0]
    return genre

def get_movie_info(movie, key):
    imdbId = get_imdbid(movie)
    response = requests.get(f'http://www.omdbapi.com/?i=tt{imdbId}&apikey={key}')
    
    cols = ['Title', 'Year', 'Rated', 'Runtime', 'Genre', 'Director',
        'Writer', 'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Poster',
        'Ratings', 'Metascore', 'imdbRating', 'Production', 'Website']
    
    try:
        result = pd.DataFrame(ast.literal_eval(response.text))
        result_df = result[cols].copy().rename({'Director':'Directors', 'Writer':'Writers'}, axis=1)

        try:
            if result_df.loc[1, 'Ratings']['Source'] == 'Rotten Tomatoes':
                RottenTomatoesRating = result_df['Ratings'][1]['Value']
                result_df.loc[:,'RottenTomatoesRating'] = RottenTomatoesRating
                result_df.drop('Ratings', axis=1, inplace=True)
        except:
            result_df.drop('Ratings', axis=1, inplace=True)
    except:
        result_df = pd.DataFrame(columns=cols).rename({'Director':'Directors', 'Writer':'Writers'}, axis=1)
    
    
    try:
        URL = 'https://www.imdb.com/title/tt{}/?ref_=fn_al_tt_2'.format(imdbId)
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')  
        result_df['Summary'] = soup.find(class_='summary_text').get_text().strip()
    
    except:
        result_df = result_df.append(pd.DataFrame(columns=['Summary']))

    return result_df.drop_duplicates()


def get_reviews(movie):
    imdbId = get_imdbid(movie)
    URL = 'https://www.imdb.com/title/tt{}/reviews?ref_=tt_ql_3'.format(imdbId)
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')  
    results = soup.find_all(class_='text show-more__control')
    reviews = []
    
    for i in results:
        try:
            review = i.get_text()
          #  review = decode(encode(reviews, 'latin-1', 'backslashreplace'), 'unicode-escape')
            review = summarize(review, word_count=30)
            reviews.append(review)
        except:
            continue
        
    
    return reviews
   
    
def get_movie_posters(imdbId_list):
    image_link_dict = {}
    
    for imdbId in imdbId_list:
        try:
            URL = 'https://www.imdb.com/title/tt{}/?ref_=fn_al_tt_2'.format(imdbId)
            page = requests.get(URL)
            soup = BeautifulSoup(page.content, 'html.parser')  
            image_link = soup.find(class_='poster').find('img')['src']
            image_link_dict[imdbId] = image_link
        except:
            continue
        
        if len(image_link_dict) == 6:
            break
        
    return image_link_dict


def get_trailer(movie, year):  
    textToSearch = '{}, {}, trailer'.format(movie, year)
    results = YoutubeSearch(textToSearch, max_results=10).to_dict()
    link = 'https://www.youtube.com' + results[0]['url_suffix']
    return link


def get_top_rating_movies(genre, n=10):
    genre = str(genre).lower()
    top_movies = ratings.loc[(ratings[genre] == 1) & (ratings.Year > 2000)].sort_values('rating', ascending=False).head(n)
    return top_movies



if __name__ == "__main__":

    movie = 'Lion King, The (1994)'
    df = get_movie_info(movie, key='e4beb4c3')
    print(get_genre(movie))
    print(get_movie_posters([get_imdbid(movie)]))
    #df.to_csv('C://Users/admin/Documents/Python2/project 3/monsters_inc_info.csv', index=False)    
    



