from keras.models import Sequential
from keras.layers import Dense
from keras import backend as K
from keras import optimizers
import numpy as np

class Regularizer(object):    
    def __call__(self, x):
        return 0.
   
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
class My_L2_Regularizer(Regularizer):
    def __init__(self, old_params, beta=0., alpha=0.):
        self.beta = K.cast_to_floatx(beta)
        self.alpha = K.cast_to_floatx(alpha)
        self.old_params = old_params

    def __call__(self, x):
        prev_param = x - self.old_params
        regularization = 0.
        regularization += self.alpha * K.sum(K.square(x))#self.l2 * K.sum(K.square(x))
        regularization += self.beta * K.sum(K.square(prev_param))#prev_param
        return regularization

    def get_config(self):
        return {'beta': float(self.beta),'alpha': float(self.alpha)}


class LogRegTransfer:
    
    def __init__(self,nb_classes,alpha,old_beta,old_weights=None,
                N_EPOCHS = 100, learning_rate = 0.01, batch_size  = 128):
        self.nb_classes = nb_classes
        self.alpha = alpha
        self.old_beta = old_beta
        self.old_weights = old_weights
        self.N_EPOCHS = N_EPOCHS
        self.learning_rate  = learning_rate
        self.batch_size = batch_size

    def fit(self,X_train,Y_train,k_count):
    
        max_feats = X_train.shape[1]
        beta = 0 if k_count == 0 else self.old_beta  
        old_w =  np.zeros((self.nb_classes,max_feats)) if self.old_weights is None else self.old_weights
        
        m_reg = My_L2_Regularizer(old_w,beta,self.alpha)
        model = Sequential()
        model.add(Dense(self.nb_classes, input_shape=(max_feats,),kernel_regularizer=m_reg))
        
        adam = optimizers.Adam(lr=self.learning_rate, amsgrad=True)#beta_1=0.9, beta_2=0.999, 
        #sgd = optimizers.SGD(lr=self.learning_rate)#decay=1e-6, momentum=0.9, nesterov=True
        model.compile(loss='mean_squared_error',
                          optimizer=adam,
                          metrics=["mean_squared_error"])
        
        history = model.fit(X_train, Y_train,
                        epochs=self.N_EPOCHS, batch_size=self.batch_size,
                        verbose=1,)# validation_data=(X_dev,Y_dev)
       
        #extract current weight
        current_weight  =  None
        for layer in model.layers:
            w = layer.get_weights()
            if len(w) == 2:
                current_weight = w[0].reshape(self.nb_classes, max_feats)
        
        return model, current_weight
    
    def evaluate(self, model, X_test, Y_test):
        score = model.evaluate(X_test, Y_test,
                               batch_size=self.batch_size, verbose=1)
        print('Test score:', score[1])
        return score[1]
        
