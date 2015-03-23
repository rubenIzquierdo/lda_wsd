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
import cPickle as pickler
import glob
from variables import *
from gensim import *
import numpy 
numpy.random.seed(777) 
from get_features import get_features
import subprocess


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


def eval_folder_lemma(lemma_folder,prefix,min_occs = None):
    ok = wr = missing = 0
    ## Load list of possible senses
    possible_senses = load_senses(lemma_folder)      
    all_occurrences = load_all_occurrences(lemma_folder)
    guess_by_mfs = {}
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
        
        #Do the evaluation for every folder
        fd_opt = open(os.path.join(lemma_folder,prefix+'#'+OPTIONS_FILENAME_MFS),'rb')
        options = pickler.load(fd_opt)
        fd_opt.close()
        
        for name_folder in glob.glob(lemma_folder+'/fold_*'):
            
            #What is the mfs of the folder
            mfs_sense_filename = os.path.join(name_folder,MFS_SENSE)
            fds = open(mfs_sense_filename,'r')
            mfs_folder = fds.readline().strip()
            fds.close()
            
            dictionary_for_mfs = corpora.dictionary.Dictionary.load(os.path.join(name_folder,options['prefix_models']+'#'+ DICTIONARY_FILENAME_MFS))
            model_for_mfs = models.LdaMulticore.load(os.path.join(name_folder,options['prefix_models']+'#'+ MODEL_FILENAME_MFS))
            similarity_matrix_for_mfs = similarities.MatrixSimilarity.load(os.path.join(name_folder,options['prefix_models']+'#'+ SIMILARITY_MATRIX_FILENAME_MFS))

            dictionary_for_nomfs = corpora.dictionary.Dictionary.load(os.path.join(name_folder,options['prefix_models']+'#'+ DICTIONARY_FILENAME_NOMFS))
            model_for_nomfs = models.LdaMulticore.load(os.path.join(name_folder,options['prefix_models']+'#'+ MODEL_FILENAME_NOMFS))
            similarity_matrix_for_nomfs = similarities.MatrixSimilarity.load(os.path.join(name_folder,options['prefix_models']+'#'+ SIMILARITY_MATRIX_FILENAME_NOMFS))

            fd_test = open(os.path.join(name_folder,'test_occurences.bin'),'rb')
            test_instances = pickler.load(fd_test)
            fd_test.close()
            for naf_filename, term_id, num_sentence, correct_sense in test_instances:
                ##print 'Evaluating %s of file %s with correct sense %s' % (term_id, naf_filename, correct_sense)
                
                tokens_for_test_instance = get_features(naf_filename, num_sentence, options['sentence_window'])

                if options['lowercase']:
                    lower_list = [token.lower() for token in tokens_for_test_instance]
                    tokens_for_test_instance = lower_list[:]
                    del lower_list
            
                if len(tokens_for_test_instance) == 0:
                    missing +=1
                    guess_by_mfs[(term_id,name_folder)] = None
                else:
                    #do the stuff
                    #calculate similarity with the MFS and with the NONMFS
                    word_vector_mfs = dictionary_for_mfs.doc2bow(tokens_for_test_instance)
                    projected_vector_mfs = model_for_mfs[word_vector_mfs] 
                    list_similarities_mfs = similarity_matrix_for_mfs[projected_vector_mfs]
                    valueMFS = sum(list_similarities_mfs)

                    word_vector_nomfs = dictionary_for_nomfs.doc2bow(tokens_for_test_instance)
                    projected_vector_nomfs = model_for_nomfs[word_vector_nomfs] 
                    list_similarities_nomfs = similarity_matrix_for_nomfs[projected_vector_nomfs]
                    valueNOMFS = sum(list_similarities_nomfs)
                    
                    predicted_as_MFS = (valueMFS > valueNOMFS)
                    if predicted_as_MFS:
                        guess_by_mfs[(term_id,name_folder)] = mfs_folder
                    else:
                        guess_by_mfs[(term_id,name_folder)] = None
                    
                    is_a_case_of_mfs = (correct_sense == mfs_folder)
                    '''if is_a_case_of_mfs:
                        print 'IS a CASe OF MFS'
                        print 'Predicted?', predicted_as_MFS
                        print 
                    '''
                    if is_a_case_of_mfs:
                        if predicted_as_MFS:
                            ok += 1
                        else:
                            wr += 1
                    #else:
                    #    if predicted_as_MFS:
                    #        wr += 1
                    #    else:
                    #        ok += 1
    return ok, wr, missing, possible_senses, len(all_occurrences), guess_by_mfs


def eval_all(this_folder, this_options, out):
    for folder in glob.glob(this_folder+'/*'):
        subprocess.check_output(["gunzip","-r",folder_for_lemma])
        
        values = eval_folder_lemma(folder, this_options['prefix_models'],  this_options['min_ocs'])
        if values is not None:
            ok, wr, missing, possible_senses, len_occs, _ = values
            P = (ok)*100.0/(ok+wr)
            R = (ok)*100.0/(ok+wr+missing)
            if P+R == 0: F = 0
            else:        F = 2*P*R / (P+R)

            out.write("%s|%.2f|%.2f|%.2f|%d|%d|%d|%d|%d\n" % (folder,P,R,F,ok,wr,missing,len(possible_senses), len_occs))

        subprocess.check_output(["gzip","-r",folder_for_lemma])
                   
            
if __name__ == '__main__':
    options_mfs = {}
    options_mfs['min_ocs'] = 3
    options_mfs['prefix_models'] = 'MFS'
    #options_mfs['sentence_window'] = 5
    #options_mfs['lowercase'] = True
    #options_mfs['remove_stopwords'] = True
    #options_mfs['num_topics'] = 100
    import sys
    out = open(sys.argv[2],'w')
    eval_all(sys.argv[1], options_mfs,out)
    out.close()
    
    '''
    options = {}
    options['min_ocs'] = 3
    options['prefix_models'] = 'fake'
    
    this_folder = 'ocs_distributed/obra.n'
    ok, wr, missing, possible_senses, len_occs, guess_by_mfs = eval_folder_lemma(this_folder, options['prefix_models'],  options['min_ocs'])
    P = (ok)*100.0/(ok+wr)
    R = (ok)*100.0/(ok+wr+missing)
    if P+R == 0:
        F = 0
    else:
        F = 2*P*R / (P+R)
    print
    print this_folder
    print '\tPrec: %.2f' % P
    print '\tRec: %.2f' % R
    print '\tF: %.2f' % F
    import pprint
    pprint.pprint(guess_by_mfs)
    '''
    