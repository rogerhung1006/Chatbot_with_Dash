import pandas as pd

movies = pd.read_csv('data/movies.csv')
links = pd.read_csv('data/links.csv', converters={'imdbId': lambda x: str(x)})

movies_links = movies.merge(links, on='movieId')
movies_links.to_csv('movies_links.csv', index=False)