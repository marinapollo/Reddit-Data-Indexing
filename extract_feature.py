from search_index import get_posts
import numpy as np
import string


class FeatureExtractor(): 

    def __init__(self,data,classes,tokenizer,index_name):
        self.data = data
        self.classes = classes
        self.tokenizer = tokenizer
        self.index_name = index_name
    
    def _preprocess(self,post):
        #punct = "\"#$%&'()*+-/:;<=>@[\]^_`{|}~"
        translator = str.maketrans('', '', string.punctuation)
        post = post.lower()
        post = post.translate(translator)
        #post = " ".join([lemmatizer.lemmatize(el) for el in post.split() if el.isalpha()])#lemmatizer.lemmatize(el), if 
        return post
    
    def _extract_data(self,set_year):
        #first_year = set_year[0][:4]
        #if int(first_year) >= 2016:# and int(first_year) < 2019
        #    index_name = 'day-reddit-index-ab2016'
        i=0        
        train_posts,train_prices = [],[]
        for instance,date,dateForSearch in self.data:
            if date in set_year:
                #print(instance + " " + dateForSearch)
                text = get_posts(instance + " " + dateForSearch,self.index_name)
                if text:
                    train_posts.append(text)
                    train_prices.append([self.classes[i]])
                    #time_series_instances.append(instance)
            i += 1
        return  train_posts,train_prices
    
    def extract_features(self, set_year):
        #,train_posts,train_prices,nb_cla
        posts, prices = self._extract_data(set_year)
        
        posts = [" ".join([self._preprocess(text) for text in text_list]) for text_list in posts] 
        X = self.tokenizer.texts_to_matrix(posts,  mode='count')
        Y = np.array([el[0] for el in prices]) 
        print("X shape",X.shape)
        print("Y shape",Y.shape)
        return X,Y
