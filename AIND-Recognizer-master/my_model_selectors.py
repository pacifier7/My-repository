import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=15,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """
    mina = float('Inf')
    model = None
    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        models = self.base_model(self.n_constant)
        mina = float('Inf')
        model = None
        try:
            for i in range(self.min_n_components,(self.max_n_components+1)):
                random_states = i
                models = self.base_model(random_states).fit(self.X, self.lengths)
                logL = models.score(self.X, self.lengths)
                p = (random_states**2)+(2*random_states*len(self.X[0])-1)
                score = ((-2)*logL) + (p*(np.log(len(self.X))))
                if score<mina:
                    mina = score
                    model = models

        except:
            pass
        return model
        # TODO implement model selection based on BIC scores
        #raise NotImplementedError


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        #warnings.filterwarnings("error", category=RuntimeWarning) # Raise an exception.
        
        maxDIC = float('-inf')
        model = None
        models = self.base_model(self.n_constant)           
        for i in range(self.min_n_components, self.max_n_components+1):
        
            try:
                models = self.base_model(i).fit(self.X, self.lengths)
                    
                logL_test = models.score(self.X, self.lengths)
            
            except:
                continue
            accumLogL = 0.0
            modelCount = 0  
            for iWord, iTuple in self.hwords.items():
                X_DIC = np.array(iTuple[0])
                lengths_DIC = iTuple[1]
                
                if iWord == self.this_word:
                    continue 
                else:
                    try:
                        logL = models.score(X_DIC, lengths_DIC)
                        modelCount = modelCount+1
                        accumLogL = accumLogL + logL
                    except: 
                        continue
            
            score = logL_test - (1.0/(1.0-1.0*modelCount))*accumLogL
            if score > maxDIC:
                maxDIC=score
                model = models

        
        return model



class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        if len(self.lengths) < 2:
            return None 
        minSplit = min(len(self.lengths),3)
        split_method = KFold(n_splits=minSplit)
        maxLL = float('-inf')
        bestModel = None
                    
        for iHidden in range(self.min_n_components, self.max_n_components+1):
            avgLL = 0.0 
            validSplit = 0
            maxLocalLL = float('-inf') 
            bestLocalModel = None
            for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                X_train_cat = []
                lengths_train = []
                for iExtract in cv_train_idx:
                    X_train_cat = X_train_cat+self.sequences[iExtract]
                    lengths_train.append(self.lengths[iExtract])

                X_train = np.array(X_train_cat)              
                X_holdout_cat = []
                lengths_holdout = []
                
                for iExtract in cv_test_idx:
                    X_holdout_cat = X_holdout_cat+self.sequences[iExtract]
                    lengths_holdout.append(self.lengths[iExtract])

                X_holdout = np.array(X_holdout_cat)
                  
                try:
                    model = GaussianHMM(n_components=iHidden, covariance_type="diag", 
                                        random_state=self.random_state, n_iter=1000).fit(X_train, lengths_train)
                    
                    logL = model.score(X_holdout, lengths_holdout)
                    validSplit = validSplit+1 
                    if logL > maxLocalLL:
                        maxLocalLL = logL
                        bestLocalModel = model
                except:
                    logL = 0
                    
                avgLL = avgLL + logL

            if validSplit > 0:
                avgLL = avgLL/(1.0*validSplit)
            else:
                avgLL = float('-inf')
            if avgLL > maxLL:
                maxLL=avgLL
                bestModel = bestLocalModel

        
        if bestModel == None:
            return None
        else:
            return bestModel



