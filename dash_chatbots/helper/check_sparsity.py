def check_sparsity(matrix):
    # calcuate total number of entries in the movie-user matrix
    num_entries = matrix.shape[0] * matrix.shape[1]
    # calculate total number of entries with zero values
    num_zeros = (matrix==0).sum(axis=1).sum()
    # calculate ratio of number of zeros to number of entries
    ratio_zeros = num_zeros / num_entries
    print('The sparsity of this matrix is about {:.2%}'.format(ratio_zeros))
    return ratio_zeros