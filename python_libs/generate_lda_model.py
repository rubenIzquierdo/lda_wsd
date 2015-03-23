#!/usr/bin/env python

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 23-mar-2015                      #  
##############################################

import os
try:
    import cPickle as pickler
except:
    import pickle as pickler

from variables import *
from gensim import *
from get_features import get_features
#Otherwise LDA generates different models!!!!
import numpy
numpy.random.seed(0)

class Cmy_corpus:
    def __init__(self, list_training_instances,options):
        self.texts = []
        self.options = options
        self.generate_texts(list_training_instances)
        self.dictionary = None
        self.create_dictionary()
        
    def generate_texts(self,list_instances):
        for naf_filename, term_id, this_sentence in list_instances:
            list_tokens_for_example = get_features(naf_filename, this_sentence, self.options['sentence_window'])

            if self.options['lowercase']:
                lower_list = [token.lower() for token in list_tokens_for_example]
                list_tokens_for_example = lower_list[:]
                del lower_list
            if self.options['remove_stopwords']:
                filtered_list = [token for token in list_tokens_for_example if token not in SPANISH_STOPWORDS]
                list_tokens_for_example = filtered_list[:]
                del filtered_list
            self.texts.append(list_tokens_for_example)
            
    def create_dictionary(self):
        self.dictionary = corpora.Dictionary()

        
        from collections import defaultdict
        
        freq = defaultdict(int)
        for text in self.texts:
            for token in text:
                freq[token] += 1
        
        for tokens in self.texts:
            self.dictionary.add_documents([[token for token in tokens if freq[token]>=2]])
            #self.dictionary.add_documents([tokens])

    def get_dictionary(self):
        return self.dictionary
        
    def __iter__(self):
        for tokens in self.texts:
            yield self.dictionary.doc2bow(tokens)
    
    def __len__(self):
        return len(self.texts)

    

def generate_lda_model(list_training, sense, options, output_folder):
    
    my_corpus = Cmy_corpus(list_training, options)
    #print my_corpus, len(my_corpus), my_corpus.get_dictionary()

    if len(my_corpus) == 0:
        print '\t\tThere are no documents!! Skipping'
        return -1

    dict_filename = os.path.join(output_folder,options['prefix_models']+ '#'+sense+'#'+ DICTIONARY_FILENAME)
    my_corpus.get_dictionary().save(dict_filename)
    #print '\t\t\tDictionary saved to %s' % dict_filename
    
    # MODEL
    try:
        my_model = models.LdaMulticore(my_corpus, num_topics = options['num_topics'])
    except:
        return -1
        
    model_filename = os.path.join(output_folder,options['prefix_models']+ '#'+sense+'#'+ MODEL_FILENAME)
    my_model.save(model_filename)
    print '\t\t\tModel saved to %s' % model_filename
    
    # SIMILARITY MATRIX
    #If you dont set the number of features to the number of topics, in testing time you will get index_error in some cases
    # as it will be calculated automatically from the corpus
    similarity_matrix = similarities.MatrixSimilarity(my_model[my_corpus],num_features = options['num_topics'])
    sim_mat_filename = os.path.join(output_folder,options['prefix_models']+ '#'+sense+'#'+ SIMILARITY_MATRIX_FILENAME)
    similarity_matrix.save(sim_mat_filename)
    #print '\t\t\tSimilarity matrix saved to %s' % sim_mat_filename
    
    return 0
