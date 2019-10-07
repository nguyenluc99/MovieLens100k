import numpy as np
import math
import pandas as pd
import sys
u_cols = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
users = pd.read_csv('ml-100k/u.user', sep='|', names=u_cols, encoding='latin-1')
n_users = users.shape[0]
r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']

ratings_base = pd.read_csv('ml-100k/ua.base', sep='\t', names=r_cols, encoding='latin-1')
ratings_test = pd.read_csv('ml-100k/ua.test', sep='\t', names=r_cols, encoding='latin-1')

rate_train = ratings_base.values
rate_test = ratings_test.values
i_cols = ['movie id', 'movie title' ,'release date','video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

items = pd.read_csv('ml-100k/u.item', sep='|', names=i_cols, encoding='latin-1')

n_items = items.shape[0]

X0 = items.values
X_train_counts = X0[:, -19:]
print('X_train_counts', type(X_train_counts))

from sklearn.feature_extraction.text import TfidfTransformer
transformer = TfidfTransformer(smooth_idf=True, norm ='l2')
tfidf = transformer.fit_transform(X_train_counts.tolist()).toarray()
print('=======', type(tfidf), tfidf)

def get_items_rated_by_user(rate_matrix, user_id):
    """
    in each line of rate_matrix, we have infor: user_id, item_id, rating (scores), time_stamp
    we care about the first three values
    return (item_ids, scores) rated by user user_id
    """
    # print('user_id', user_id)
    y = rate_matrix[:,0] # all users
    # print('type of y is ', type(y),'shape is :', y.shape, ', y is', y)
    # item indices rated by user_id
    # we need to +1 to user_id since in the rate_matrix, id starts from 1 
    # while index in python starts from 0
    ids = np.where(y == user_id +1)[0] 
    # print('type of ids is ', type(ids),'shape is :', ids.shape, ', ids is', ids)
    # ids2 = np.where(y == user_id +1)
    # print('ids2', ids2 )
    # print('y', y )
    # print('user_id', user_id )
    # print('ids', type(ids))
    item_ids = rate_matrix[ids, 1] - 1 # index starts from 0 
    # print('type of item_ids is ', type(item_ids),'shape is :', item_ids.shape, ', item_ids is', item_ids)
    # print('item_ids', type(item_ids))
    scores = rate_matrix[ids, 2]
    # print('type of scores is ', type(scores),'shape is :', scores.shape, ', scores is', scores)
    # print('scores', type(scores))
    return (item_ids, scores)

from sklearn.linear_model import Ridge

d = tfidf.shape[1] # data dimension
W = np.zeros((d, n_users))
b = np.zeros((1, n_users))

for n in range(n_users):    
    ids, scores = get_items_rated_by_user(rate_train, n)
    clf = Ridge(alpha=0.01, fit_intercept  = True)
    print('clf', clf, type(clf))
    Xhat = tfidf[ids, :]
    print('Xhat', Xhat, type(Xhat))
    
    clf.fit(Xhat, scores) 
    W[:, n] = clf.coef_
    b[0, n] = clf.intercept_
    print('W', W, type(W))
    print('b', b, type(b))

# predicted scores
Yhat = tfidf.dot(W) + b
print('yhat is ', Yhat)
n = 10
np.set_printoptions(precision=2) # 2 digits after . 
ids, scores = get_items_rated_by_user(rate_test, n)
Yhat[n, ids]
print('Rated movies ids :', ids )
print('True ratings     :', scores)
print('Predicted ratings:', Yhat[ids, n])

def evaluate(Yhat, rates, W, b):
    se = 0
    cnt = 0
    # for n in range(3, 4):
    for n in range(n_users):
        ids, scores_truth = get_items_rated_by_user(rates, n)
        scores_pred = Yhat[ids, n]
        e = scores_truth - scores_pred # an array
        se += (e*e).sum(axis = 0) # sum of elements in array
        cnt += e.size 
    return math.sqrt(se/cnt)

print ('RMSE for training:', evaluate(Yhat, rate_train, W, b))
print ('RMSE for test    :', evaluate(Yhat, rate_test, W, b))