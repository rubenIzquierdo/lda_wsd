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
import random
import glob
import sys
import time
from collections import defaultdict 
try:
    import cPickle as pickler
except:
    import pickle as pickler
from variables import *
from gensim import *
from get_features import get_features
from eval_mfs import eval_folder_lemma as eval_folder_lemma_mfs
import numpy 
numpy.random.seed(777) 


def load_senses(lemma_folder):
    fd_senses = open(os.path.join(lemma_folder,'possible_senses'),'r')
    possible_senses = fd_senses.readline().strip().split()
    fd_senses.close()
    return possible_senses

def load_all_occurrences(lemma_folder):
    fd_o = open(os.path.join(lemma_folder,'all_occurrences.bin'),'r')
    all_occs = pickler.load(fd_o)
    fd_o.close()
    return all_occs

def evaluate_lemma_random(lemma_folder,min_occs = None):
    ok = wr = missing = 0
    ## Load list of possible senses
    possible_senses = load_senses(lemma_folder)    
    all_occurrences = load_all_occurrences(lemma_folder)

    
    if len(possible_senses) == 1:
        ok = len(all_occurrences)
    else:
        sense_distribution = {}
        fd_d = open(os.path.join(lemma_folder,'sense_distribution.txt'),'r')
        for line in fd_d:
            sense, freq = line.strip().split()
            sense_distribution[sense] = int(freq)
        fd_d.close()
    
    
        if min_occs is not None:
            for sense, freq in sense_distribution.items():
                if freq < min_occs:
                    print '\tNot evaluated because there are only %d occurrences for the sense %s and the minimum was set to %d'  % (freq, sense,min_occs)
                    return None
                 
        for naf_filename, term_id, sentence, correct_sense in all_occurrences:
            random_sense = random.choice(possible_senses)
            if random_sense == correct_sense:
                ok += 1
            else:
                wr += 1
    return ok, wr, missing, possible_senses, len(all_occurrences)


def evaluate_mfs(lemma_folder,min_occs = None):
    ok = wr = missing = 0
    ## Load list of possible senses
    possible_senses = load_senses(lemma_folder)    
    all_occurrences = load_all_occurrences(lemma_folder)
    
    
    if len(possible_senses) == 1:
        ok = len(all_occurrences)
    else:
        sense_distribution = {}
        fd_d = open(os.path.join(lemma_folder,'sense_distribution.txt'),'r')
        for line in fd_d:
            sense, freq = line.strip().split()
            sense_distribution[sense] = int(freq)
        fd_d.close()
        
        if min_occs is not None:
            for sense, freq in sense_distribution.items():
                if freq < min_occs:
                    print '\tNot evaluated because there are only %d occurrences for the sense %s and the minimum was set to %d'  % (freq, sense,min_occs)
                    return None
                
        #Get the mosf frequent sense on ALL the occurences
        freq_per_sense = defaultdict(int)
        for naf_filename, term_id, sentence, correct_sense in all_occurrences:
            freq_per_sense[correct_sense] += 1
        
        most_freq_sense, highest_freq = sorted(freq_per_sense.items(),key=lambda t: -t[1])[0]
        ok = highest_freq   #number of ok equal to the frequency of the most frequent sense
        wr = len(all_occurrences) - ok #The rest are wrong
        
    return ok, wr, missing, possible_senses, len(all_occurrences)


def evaluate_mfs_folded(lemma_folder,min_occs = None):
    ok = wr = missing = 0
    ## Load list of possible senses
    possible_senses = load_senses(lemma_folder)    
    all_occurrences = load_all_occurrences(lemma_folder)
    
    

    
    if len(possible_senses) == 1:
        ok = len(all_occurrences)
    else:
        sense_distribution = {}
        fd_d = open(os.path.join(lemma_folder,'sense_distribution.txt'),'r')
        for line in fd_d:
            sense, freq = line.strip().split()
            sense_distribution[sense] = int(freq)
        fd_d.close()
    
    
        if min_occs is not None:
            for sense, freq in sense_distribution.items():
                if freq < min_occs:
                    print '\tNot evaluated because there are only %d occurrences for the sense %s and the minimum was set to %d'  % (freq, sense,min_occs)
                    return None
                
        for name_folder in glob.glob(lemma_folder+'/fold_*'):
            
            
            fd_train = open(os.path.join(name_folder,'train_occurences.bin'),'rb')
            train_instances = pickler.load(fd_train)
            fd_train.close()
                        
            fd_test = open(os.path.join(name_folder,'test_occurences.bin'),'rb')
            test_instances = pickler.load(fd_test)
            fd_test.close()
                
            #Get the mosf frequent sense on the train part
            freq_per_sense = defaultdict(int)
            for naf_filename, term_id, sentence, correct_sense in train_instances:
                freq_per_sense[correct_sense] += 1
        
            most_freq_sense, highest_freq = sorted(freq_per_sense.items(),key=lambda t: -t[1])[0]
            for naf_filename, term_id, sentence, correct_sense in test_instances:
                if correct_sense == most_freq_sense:
                    ok += 1
                else:
                    wr += 1
    return ok, wr, missing, possible_senses, len(all_occurrences)

def evaluate_lemma_lda(lemma_folder,prefix, min_occs = None, use_mfs=True):
    ok = wr = missing = 0
    ## Load list of possible senses
    possible_senses = load_senses(lemma_folder)      
    all_occurrences = load_all_occurrences(lemma_folder)
    
   
    if len(possible_senses) == 1:
        ok = len(all_occurrences)
    else:
        sense_distribution = {}
        fd_d = open(os.path.join(lemma_folder,'sense_distribution.txt'),'r')
        for line in fd_d:
            sense, freq = line.strip().split()
            sense_distribution[sense] = int(freq)
        fd_d.close()
        
        most_frequent_sense, most_frequent_sense_frequency = sorted(sense_distribution.items(), key=lambda t: -t[1])[0]    
    
        if min_occs is not None:
            for sense, freq in sense_distribution.items():
                if freq < min_occs:
                    print '\tNot evaluated because there are only %d occurrences for the sense %s and the minimum was set to %d'  % (freq, sense,min_occs)
                    return None
                
        #Do the evaluation for every folder
        fd_opt = open(os.path.join(lemma_folder,prefix+'#'+OPTIONS_FILENAME),'rb')
        options = pickler.load(fd_opt)
        fd_opt.close()
        
        guess_by_mfs = {}
        if use_mfs:
            _, _, _, _, _, guess_by_mfs = eval_folder_lemma_mfs(lemma_folder, 'MFS',  min_occs)
        
        for name_folder in glob.glob(lemma_folder+'/fold_*'):
            # LOAD THE OPTIONS
            #Load test instances:
            dictionary_for_sense = {}
            model_for_sense = {}
            similarity_matrix_for_sense = {}
            for sense in possible_senses:
                model_filename = os.path.join(name_folder,prefix+ '#'+sense+'#'+ MODEL_FILENAME)
                if not os.path.exists(model_filename):
                    continue                
                dictionary_for_sense[sense] = corpora.dictionary.Dictionary.load(os.path.join(name_folder,prefix+ '#'+sense+'#'+ DICTIONARY_FILENAME))
                model_for_sense[sense] = models.LdaMulticore.load(os.path.join(name_folder,prefix+ '#'+sense+'#'+ MODEL_FILENAME))
                similarity_matrix_for_sense[sense] = similarities.MatrixSimilarity.load(os.path.join(name_folder,prefix+ '#'+sense+'#'+ SIMILARITY_MATRIX_FILENAME))
                
            
            fd_test = open(os.path.join(name_folder,'test_occurences.bin'),'rb')
            test_instances = pickler.load(fd_test)
            fd_test.close()
            for naf_filename, term_id, num_sentence, correct_sense in test_instances:
                #HERE IS the point to decide if evaluate this instance or not!!!!
                # We can get the MFS and decide to leave out of the evaluation all the cases where the correct is the MFS
                #if correct_sense == most_frequent_sense:
                #    ok += 1
                #    continue
                    
                #print 'Evaluating %s of file %s with correct sense %s' % (term_id, naf_filename, correct_sense)
                
                
                these_mfs_guess = None
                if (term_id, name_folder) in guess_by_mfs:
                    these_mfs_guess = guess_by_mfs[(term_id, name_folder)]
                    
                if these_mfs_guess is not None:
                    if these_mfs_guess == correct_sense:
                        ok += 1
                        continue
                    
                
                
                tokens_for_test_instance = get_features(naf_filename, num_sentence, options['sentence_window'])
                
                if options['lowercase']:
                    lower_list = [token.lower() for token in tokens_for_test_instance]
                    tokens_for_test_instance = lower_list[:]
                    del lower_list
                    
                if len(tokens_for_test_instance) == 0:
                    missing +=1
                else:
                    sense_similarity = defaultdict(list)
                    for sense in possible_senses:
                        if sense in model_for_sense and sense != most_frequent_sense:  #The second classifier can not assign the MFS sense
                            word_vector = dictionary_for_sense[sense].doc2bow(tokens_for_test_instance)
                            projected_vector = model_for_sense[sense][word_vector] 
                            list_similarities = similarity_matrix_for_sense[sense][projected_vector]
                            value = sum(list_similarities)
                            sense_similarity[sense].append(value)
                    
                    list_sense_similarity = []
                    for sense,list_values in sense_similarity.items():
                        value = sum(list_values)
                        list_sense_similarity.append((sense,value))
                    
                    #for sense, value in sorted(list_sense_similarity, key=lambda t: -t[1]):
                    #    print '\t%s %.3f Correct: %s' % (sense.encode('utf-8'), value, correct_sense)   
                   
                    if len(list_sense_similarity) == 0: #there is no info about any sense
                        missing += 1
                    else:
                        best_sense, best_simil = sorted(list_sense_similarity, key=lambda t: -t[1])[0]
                        if best_sense == correct_sense:
                            ok += 1
                        else:
                            wr += 1
               
    return ok, wr, missing, possible_senses, len(all_occurrences)

