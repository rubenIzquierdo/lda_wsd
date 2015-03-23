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
import time
import cPickle as pickler 
import glob

from collections import defaultdict
from get_features import get_features
from variables import *
from gensim import *
import numpy 
numpy.random.seed(777) 


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

        '''
        from collections import defaultdict
        
        freq = defaultdict(int)
        for text in self.texts:
            for token in text:
                freq[token] += 1
        '''
        for tokens in self.texts:
            #self.dictionary.add_documents([[token for token in tokens if freq[token]>=2]])
            self.dictionary.add_documents([tokens])

    def get_dictionary(self):
        return self.dictionary
        
    def __iter__(self):
        for tokens in self.texts:
            yield self.dictionary.doc2bow(tokens)
    
    def __len__(self):
        return len(self.texts)

def train_mfs_models(ocs_mfs, ocs_no_mfs, output_folder, options):
    #First train the mfs model
    my_corpus_mfs = Cmy_corpus(ocs_mfs,options)
    #print my_corpus_mfs, len(my_corpus_mfs), my_corpus_mfs.get_dictionary()
    
    dict_filename = os.path.join(output_folder,options['prefix_models']+'#'+ DICTIONARY_FILENAME_MFS)
    my_corpus_mfs.get_dictionary().save(dict_filename)
    #print '\t\t\tDictionary saved to %s' % dict_filename
    
    # MODEL
    try:
        my_model_mfs = models.LdaMulticore(my_corpus_mfs, num_topics = options['num_topics'])
    except:
        return -1
        
    model_filename_mfs = os.path.join(output_folder,options['prefix_models']+'#'+ MODEL_FILENAME_MFS)
    my_model_mfs.save(model_filename_mfs)
    #print '\t\t\tModel saved to %s' % model_filename_mfs

    # SIMILARITY MATRIX
    #If you dont set the number of features to the number of topics, in testing time you will get index_error in some cases
    # as it will be calculated automatically from the corpus
    similarity_matrix_mfs = similarities.MatrixSimilarity(my_model_mfs[my_corpus_mfs],num_features = options['num_topics'])
    sim_mat_filename_mfs = os.path.join(output_folder,options['prefix_models']+'#'+ SIMILARITY_MATRIX_FILENAME_MFS)
    similarity_matrix_mfs.save(sim_mat_filename_mfs)
    #print '\t\t\tSimilarity matrix saved to %s' % sim_mat_filename_mfs
    
    ## THE SAME FOR THE NONMFS MODEL
    my_corpus_nomfs = Cmy_corpus(ocs_no_mfs,options)
    #print my_corpus_mfs, len(my_corpus_mfs), my_corpus_mfs.get_dictionary()
    
    dict_filename_nomfs = os.path.join(output_folder,options['prefix_models']+'#'+ DICTIONARY_FILENAME_NOMFS)
    my_corpus_nomfs.get_dictionary().save(dict_filename_nomfs)
    #print '\t\t\tDictionary saved to %s' % dict_filename_nomfs
    
    # MODEL
    try:
        my_model_nomfs = models.LdaMulticore(my_corpus_nomfs, num_topics = options['num_topics'])
    except:
        return -1
        
    model_filename_nomfs = os.path.join(output_folder,options['prefix_models']+'#'+ MODEL_FILENAME_NOMFS)
    my_model_nomfs.save(model_filename_nomfs)
    #print '\t\t\tModel saved to %s' % model_filename_nomfs

    # SIMILARITY MATRIX
    #If you dont set the number of features to the number of topics, in testing time you will get index_error in some cases
    # as it will be calculated automatically from the corpus
    similarity_matrix_nomfs = similarities.MatrixSimilarity(my_model_nomfs[my_corpus_nomfs],num_features = options['num_topics'])
    sim_mat_filename_nomfs = os.path.join(output_folder,options['prefix_models']+'#'+ SIMILARITY_MATRIX_FILENAME_NOMFS)
    similarity_matrix_nomfs.save(sim_mat_filename_nomfs)
    #print '\t\t\tSimilarity matrix saved to %s' % sim_mat_filename_nomfs


def train_folder_lemma(this_folder,options):
    #Load the possible senses
    fd_senses = open(os.path.join(this_folder,'possible_senses'),'r')
    possible_senses = fd_senses.readline().strip().split()
    fd_senses.close()
    start_time = time.time()
    print '%s Training models for %s  List of senses: %s' % (time.strftime('%Y-%m-%dT%H:%M:%S%Z'), this_folder, str(possible_senses))
    print '\tOptions: %s' % str(options)    


    sense_distribution = {}
    fd_d = open(os.path.join(this_folder,'sense_distribution.txt'),'r')
    for line in fd_d:
        sense, freq = line.strip().split()
        sense_distribution[sense] = int(freq)
    fd_d.close()
    #print 'Sense distribution: %s' % str(sense_distribution)    

    process_this = True
    if 'min_occs' in options:
        for sense, freq in sense_distribution.items():
            if freq < options['min_occs']:
                print '\tNot trained because there are only %d occurrences for the sense %s and the minimum was set to %d'  % (freq, sense,options['min_occs'] )
                process_this = False
                ret = -1
                break
            
    if process_this:
        ##Save the options
        fd_opts = open(os.path.join(this_folder,options['prefix_models']+'#'+OPTIONS_FILENAME_MFS),'w')
        pickler.dump(options,fd_opts,0)
        fd_opts.close()
       
        #print '\tOption saved to %s' % fd_opts.name
        if len(possible_senses) == 1:
            print '\tIt is a monosemous lemma, nothing to train'
            ret = 0
        else:
            for name_fold in glob.glob(os.path.join(this_folder,'fold_*')):
                fd_train = open(os.path.join(name_fold,'train_occurences.bin'),'rb')
                train_instances = pickler.load(fd_train)
                fd_train.close()
                print '\tFold %s with %d examples' % (name_fold,len(train_instances))
                
                instances_for_sense = defaultdict(int)
                for naf_filename, term_id, num_sentence, sense in train_instances:                    
                    instances_for_sense[sense] += 1
                    
                mfs_folder = sorted(instances_for_sense.items(), key=lambda t: -t[1])[0][0]
                
                mfs_sense_filename = os.path.join(name_fold,MFS_SENSE)
                fds = open(mfs_sense_filename,'w')
                fds.write('%s\n' % mfs_folder)
                fds.close()
                ocs_mfs = []
                ocs_no_mfs = []
                for naf_filename, term_id, num_sentence, sense in train_instances:
                    if sense == mfs_folder:
                        ocs_mfs.append((naf_filename, term_id, num_sentence))
                    else:
                        ocs_no_mfs.append((naf_filename, term_id, num_sentence))
                print '\tNum instances for MFS: %d' % len(ocs_mfs)
                print '\tNum instances for NO MFS: %d' % len(ocs_no_mfs)
                ret_code = train_mfs_models(ocs_mfs, ocs_no_mfs, name_fold, options)

if __name__ == '__main__':
    options = {}
    options['min_ocs'] = 3
    options['prefix_models'] = 'fake'
    options['sentence_window'] = 5
    options['lowercase'] = True
    options['remove_stopwords'] = True
    options['num_topics'] = 1000
    
    this_folder = 'ocs_distributed/obra.n'
    train_folder_lemma(this_folder, options)
