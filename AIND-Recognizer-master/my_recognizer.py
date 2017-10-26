import warnings
from asl_data import SinglesData
import numpy as np


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    iTW = test_set.get_all_Xlengths()
    
    # Loop over each word, and the each model to find max likelihood model-word.
    for iWI, iWT in iTW.items():
        bestGuessWord = None
        maxLL = float('-inf')
        testWordDict = dict()  # Keep track of the probabilities for each model per test word
        testSequence = np.array(iWT[0]) 
        testLen = np.array(iWT[1]) 
        for iMW, iM in models.items():
            
            try:
                logL = iM.score(testSequence, testLen)
            except:
                logL = float('-inf') 
                
            testWordDict[iMW] = logL    
            
            if logL > maxLL:
                maxLL=logL
                bestGuessWord = iMW

        guesses.append(bestGuessWord)
        probabilities.append(testWordDict)
            
    return probabilities, guesses
