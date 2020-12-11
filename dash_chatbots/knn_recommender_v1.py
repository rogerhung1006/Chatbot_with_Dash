import pandas as pd
import re
from scipy.sparse import csr_matrix

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

# utils import
from fuzzywuzzy import fuzz

ratings = pd.read_csv('data/ratings.csv')
movies = pd.read_csv('data/movies_links_clean.csv')
ratings = ratings[ratings.movieId.isin(movies.movieId)]



r_matrix = ratings.pivot_table(values='rating', index='movieId', columns='userId').fillna(0)

# Center each users ratings around 0 and fill in the missing data with 0s
avg_ratings = r_matrix.mean(axis=1)
r_matrix_centered = r_matrix.sub(avg_ratings, axis=0)
r_matrix_normed = r_matrix_centered.fillna(0)

# create mapper from movie title to index
movie_to_idx = {
    movie: idx for idx, movie in 
    enumerate(list(movies.set_index('movieId').loc[r_matrix_normed.index].title))
}
# transform matrix to scipy sparse matrix
r_matrix_sparse = csr_matrix(r_matrix_normed.values)


# define model
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)

def fuzzy_matching(mapper, movie_in_search, verbose=True):
    """
    return the closest match via fuzzy ratio. If no match found, return None
    
    Parameters
    ----------    
    mapper: dict, map movie title name to index of the movie in data

    fav_movie: str, name of user input movie
    
    verbose: bool, print log if True

    Return
    ------
    index of the closest match
    """
    match_tuple = []
    # choice = 0
    # get match
    for title, idx in mapper.items():
        ratio = fuzz.ratio(title.lower(), movie_in_search.lower())
        if ratio >= 90:
            match_tuple.append((title, idx, ratio))
    # sort
    match_tuple = sorted(match_tuple, key=lambda x: x[2])[::-1]
    if not match_tuple:
        print('Oops! No match is found')
        return
    if verbose:
        return match_tuple[0][1]
        # all_options = [x[0] for x in match_tuple]
        # if len(all_options) >= 3:
        #     choice = int(input(f'\nFind possible matches in the database: {all_options}, \nPlease choose one by specifying the order in the list: \n(note: the order starting from 1) ')) - 1
        #     try: 
        #         return match_tuple[choice][1]
        #     except:
        #         return match_tuple[0][1]

    
def make_recommendation(model_knn, data, mapper, movie_in_search, n_recommendations):
    # fit
    model_knn.fit(data)
    # get input movie index
    print('You have input movie:', movie_in_search)
    idx = fuzzy_matching(mapper, movie_in_search, verbose=True)
    if idx is None:
        return 
    distances, indices = model_knn.kneighbors(data[idx], n_neighbors=n_recommendations+1)
    # get list of raw idx of recommendations
    raw_recommends = \
        sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[1:] #[:0:-1]
    # get reverse mapper
    reverse_mapper = {v: k for k, v in mapper.items()}
    
    # print recommendations
  #  print(f'\nRecommendations for {reverse_mapper[idx]}:')
   # for i, (idx, dist) in enumerate(raw_recommends):
    #    print('{0}: {1}, with distance of {2}'.format(i+1, reverse_mapper[idx], round(dist, 3)))
    return([reverse_mapper[idx] for idx, dist in raw_recommends])

if __name__ == '__main__':
    print('')
    movie_in_search = 'Iron Man 3 (2013)'
    # movie_in_search = 'Lion King, The (1994)'

    recommendation_list = make_recommendation(
        model_knn=model_knn,
        data=r_matrix_sparse,
        movie_in_search=movie_in_search,
        mapper=movie_to_idx,
        n_recommendations=20)
    