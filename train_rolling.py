from classifyKeras import LogRegTransfer
from extract_feature import FeatureExtractor
from data_loader import DataMovie
import logging
import pickle
    
class Classificator():
    def __init__(self):
        
        self.elements = {'nb_classes':1,'alpha':0.01, 'beta':0.01, 'rolling': True,
                        'train_min': 2009, 'train_max': 2018, 'test_min':2015, 'test_max':2016}
        other_attributes = ['data', 'tokenizer', 'index_name']
        for att in other_attributes:
            self.elements[att] = None
        
    def train(self,trainset_year,testset_year,k,old_weights,beta=0):
        data = self.elements['data'].data #data is an DataMovie object
        classes = self.elements['data'].classes
        tokenizer = self.elements['tokenizer'].tokenizer
        index_name = self.elements['index_name']
        
        feature_extractor = FeatureExtractor(data,classes,tokenizer,index_name)   
        X_train,Y_train = feature_extractor.extract_features(trainset_year)
        X_test,Y_test = feature_extractor.extract_features(testset_year)
        
        alpha = self.elements['alpha']
        nb_classes = self.elements['nb_classes']
        
        classif = LogRegTransfer(nb_classes,alpha,beta,old_weights)
        model, old_weights = classif.fit(X_train,Y_train,k)
        score = classif.evaluate(model,X_test,Y_test)
        
        # add filemode="w" to overwrite
        filename= open("rolling"+str(self.elements['rolling'])+".log", 'a')
        if int(testset_year[0][:4]) == self.elements['test_min']:
            log_inf = [alpha, beta, trainset_year[-1], testset_year[0], score] 
            log_inf = list(map(lambda x:str(x),log_inf)) + ["\n"]
            filename.write(" ".join(log_inf))
        return old_weights
    
    
    def train_rolling(self):
        
        all_years = self.elements['data'].all_years
        old_weights = None
        year_and_month = None

        if self.elements['rolling']:
            selected_years = [y for y in all_years if  self.elements['train_min'] <= int(y[:4]) <= self.elements['test_max']]
            for k in range(len(selected_years)-1):    
                trainset_year = [selected_years[k]]
                testset_year = [selected_years[k+1]]#rest_test
                year_and_month = selected_years[k+1]#the model tasted on this year
                print(f"years train: {trainset_year}")
                print(f"years test: {testset_year}")
                old_weights = self.train(trainset_year,testset_year,k,old_weights,self.elements['beta'])
        else:
            train_years = [y for y in all_years if  self.elements['train_min'] <= int(y[:4]) <= self.elements['train_max']]
            test_years = [y for y in all_years if  self.elements['test_min'] <= int(y[:4]) <= self.elements['test_max']]
            for k in range(len(test_years)):
                testset_year = [test_years[k]]#rest_test
                year_and_month = test_years[k]#the previous model
                print(f"years train: {train_years}")
                print(f"years test: {testset_year}")
                old_weights = self.train(train_years,testset_year,k,old_weights,beta=0)
                train_years.append(test_years[k])
            
        print(f"Saving weight of {year_and_month}")
        rolling = self.elements['rolling']
        with open('rolling'+str(rolling)+'weight'+str(self.elements['beta'])+'-'+str(year_and_month)+'.pickle', 'wb') as handle:
            pickle.dump(old_weights, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        
class ClassificatorBuilder:
    classificator = Classificator()

    def add_field(self, type, name):
        self.classificator.elements[type] = name
        return self
    

    
        
        
