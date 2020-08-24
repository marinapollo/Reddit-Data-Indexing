from collections import defaultdict, Counter
from keras.preprocessing.text import Tokenizer
import math           
from datetime import datetime
from datetime import date, timedelta
from abc import ABC, abstractmethod
from nltk.corpus import stopwords
import pandas as pd

class LexiconTokenizer():
    
    def __init__(self,lexicon_path):
        self.max_feats, self.tokenizer = self.get_vocab(lexicon_path)
    
    def get_vocab(self,lexicon_path):
        #download opinion word list
        lex_subj = lexicon_path
        df_subj = pd.read_table(lex_subj)
        lexicon_words = set()
        for info in df_subj["info"]:
            typ = [el for el in info.split()][0]
            polar = [el for el in info.split()][-1]
            word = [el for el in info.split()][2]
            if polar == "priorpolarity=negative" or polar == "priorpolarity=positive" or polar == "priorpolarity=neutral":
                lexicon_words.add(word[6:])
        tokenizer  = Tokenizer()
        seed_words = " ".join(lexicon_words)
        tokenizer.fit_on_texts([seed_words])
        vocab = [w for w, ind in list(tokenizer.word_index.items())]
        print("number of vocab words:", len(vocab))
        return len(vocab)+1,tokenizer

class DataMovie(): 
    
    def __init__(self,datapath,min_year = 2009, max_year=2018):
        self.min_year = min_year
        self.max_year = max_year
        self.data, self.classes, self.all_years = self.get_data(datapath)    
        
    def get_cla(self, price_rate):
        label = None
        if price_rate > 10:
            label = 2#"UP"
        elif price_rate < -10:
            label = 0#"DOWN"
        else:
            label = 1#"STAY"
        return label#,price_rate
    
   
    def get_movie_info(self,data):
        data = data[data["Theater Count"]!="-"]
        data = data[data["bo_year"]>=self.min_year]
        data = data[data["bo_year"]<=self.max_year]
        movies = data["title"].tolist()
        monthes = data["bo_month"].tolist()
        years = data["bo_year"].tolist()
        first_days = data["firstDay"].tolist()#Friday
        changes = data["change"].tolist()
        grosses = data["Weekend Gross"].tolist()
        theaters = data["Theater Count"].tolist()
        theaters = [int(el) for el in theaters]#1 if el == "-" else 
        last_days = [int(d)+2 for d in first_days]

        movieDict = defaultdict(list)
        for movie,f_day,l_day,month,y,ch,gr,th in zip(movies,first_days,last_days, monthes,years,changes,grosses,theaters):
            monday = f_day-4
            date = str(monday)+" "+str(l_day)+" "+str(month)+" "+str(y)
            movieDict[movie].append((date,ch,gr,th))

        deltaMyDict = defaultdict(dict)
        for m,d in movieDict.items():
            prev_price_mydelta = {}
            for i in range(len(d)):
                date, change, price, theat = d[i]
                prev_date, prev_change, prev_price,prev_theat = d[i-1]                
                income_per_screen = price/theat
                income_per_screen_prev = prev_price/prev_theat
                log_price_rate = math.log(income_per_screen/income_per_screen_prev)
                cla = self.get_cla(log_price_rate*100)
                prev_price_mydelta[date] =  log_price_rate #cla
            deltaMyDict[m] = prev_price_mydelta

        deltas = []
        saved_grosses = []
        final_data = []
        possible_dates = set()
        for movie,f_day,l_day,month,y,change,gross in zip(movies,first_days,last_days,monthes,years,changes,grosses):
            deltaDatesInfo = deltaMyDict[movie]
            monday = f_day-4
            date = str(monday)+" "+str(l_day)+" "+str(month)+" "+str(y)
            delta = deltaDatesInfo[date]

            if  change != "-":
                date_to_save = str(y)+"-"+str(month)+"-"+str(f_day)#'%Y-%m-%d'
                possible_dates.add(date_to_save)
                dateToSearch = self.zero_map(str(monday))+" "+self.zero_map(str(l_day))+" "+self.zero_map(str(month))+" "+str(y)
                final_data.append((movie, date_to_save, dateToSearch))#firm,date,text
                deltas.append(delta)
                saved_grosses.append(gross)

        classes = deltas          
        myyears = sorted(list(possible_dates), key=lambda x: datetime.strptime(x, '%Y-%m-%d'))     
        return final_data, classes, myyears
    
    def zero_map(self,el):
        if len(el) == 1:
            return "0"+el
        else:
            return el
    
    def get_data(self,datapath):
        init_data = pd.read_csv(datapath)
        data,classes,myyears = self.get_movie_info(init_data)
        myyears = [self.zero_map(el.split("-")[0])+"-"+self.zero_map(el.split("-")[1])+"-"+self.zero_map(el.split("-")[2]) for el in myyears]
        data = [(movie, self.zero_map(el.split("-")[0])+"-"+self.zero_map(el.split("-")[1])+"-"+self.zero_map(el.split("-")[2]),date)
                for movie,el,date in data]
        
        return (data,classes,myyears)

