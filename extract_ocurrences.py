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

import sys
import glob
import os
import shutil
import random
try:
    import cPickle as pickler
except:
    import pickle as pickler
    
from collections import defaultdict
from libs.KafNafParserPy import KafNafParser

if __name__ == '__main__':
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    occurrences_per_lemma = defaultdict(list)    # [lemma,pos] ==> (doc_id, term_id, sense)

    for naf_file in glob.glob(input_folder+'/*.naf'):
        naf_obj = KafNafParser(naf_file)
        print 'Processing %s' % naf_file
        ################################
        #### Sentences for tokens ###
        ################################
        sentence_for_tokenid = {}
        for token in naf_obj.get_tokens():
            sentence_for_tokenid[token.get_id()] = token.get_sent()
        ################################        
        
        ################################
        # Target words
        ################################
        for term in naf_obj.get_terms():
            lemma = term.get_lemma()
            pos = term.get_pos()[0]
            sense = None
            for ext_ref in term.get_external_references():
                if ext_ref.get_resource() == 'WordNet-1.6':
                    sense = ext_ref.get_reference()
                    break
                    
            if sense is not None and 'eng16-cs' not in sense.lower() and len(sense) == len('eng16-10885886-n'):
                num_sentence = sentence_for_tokenid[term.get_span().get_span_ids()[0]]
                occurrences_per_lemma[(lemma,pos)].append((naf_file,term.get_id(), num_sentence, sense))
                
                
    ##Create output folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
        print>>sys.stderr,'Output folder %s has been removed as it existed' % output_folder
    os.mkdir(output_folder)
    
    MIN_OCCURRENCES = 0 #all of them
    N_FOLDS = 3
    for (lemma,pos), list_occurrences in occurrences_per_lemma.items():
        possible_classes = set(sense for filename, termid, num_sentence, sense in list_occurrences)
        if len(possible_classes) == 1 or len(list_occurrences) > MIN_OCCURRENCES:

            ################################
            #Create a folder for this
            ################################
            new_folder = os.path.join(output_folder,lemma.encode('utf-8')+'.'+pos.encode('utf-8'))
            os.mkdir(new_folder)

            if len(possible_classes) == 1:
                print 'Created folder %s, is monosemous so no FCV' % (new_folder)
            
            
            
            ################################
            #Save the possible classes
            ################################
            fd = open(os.path.join(new_folder,'possible_senses'),'w')
            fd.write('\t'.join(list(possible_classes))+'\n')
            fd.close()
            ################################
            
            ################################
            # Save all the ocurrences
            ################################
            fd_o = open(os.path.join(new_folder,'all_occurrences.bin'),'w')
            pickler.dump(list_occurrences, fd_o, protocol=-1)
            fd_o.close()
            ################################
            
            
            
            if len(list_occurrences) > MIN_OCCURRENCES: 
                
                #### Obtain distribution per sense ####
                ocs_per_sense = defaultdict(list)
                for oc in list_occurrences:
                    filename, termid, num_sentence, sense = oc
                    ocs_per_sense[sense].append(oc)
                    
                ################################
                #Save the possible classes
                ################################
                fd = open(os.path.join(new_folder,'sense_distribution.txt'),'w')
                for sense, this_list in ocs_per_sense.items():
                    fd.write('%s\t%d\n' % (sense, len(this_list)))
                fd.close()
                    
                for sense in ocs_per_sense.keys():
                   random.shuffle(ocs_per_sense[sense])
                
                ################################
                # Create the folds
                ################################
                begin_end_size_fold_4sense = {}
                for sense, this_list in ocs_per_sense.items():
                    size_of_fold = len(this_list) / N_FOLDS
                    begin_end_size_fold_4sense[sense] = (0,size_of_fold, size_of_fold)
                
                print 'Creating folds for %s with %d total occurrences' % (new_folder,len(list_occurrences))
                for n in range(N_FOLDS):
                    name_fold = os.path.join(new_folder,'fold_%d' % n)
                    os.mkdir(name_fold)
                    
                    #Do this for every
                    my_train = []
                    my_test = []
                    for sense, this_list in ocs_per_sense.items():
                        my_begin, my_end, size_of_fold = begin_end_size_fold_4sense[sense]
                        
                        this_test = this_list[my_begin:my_end]
                        this_train = this_list[:my_begin] + this_list[my_end:]
                        my_test.extend(this_test)
                        my_train.extend(this_train)
                        begin_end_size_fold_4sense[sense] = (my_end, my_end + size_of_fold, size_of_fold)
                        
                    
                    if len( set(my_test) & set(my_train)) != 0:
                        print>>sys.stderr,'Error overlapping'
                        print>>sys.stderr,my_train
                        print>>sys.stderr,my_test

                    
                    fd_train = open(os.path.join(name_fold,'train_occurences.bin'),'wb')
                    pickler.dump(my_train,fd_train,protocol=-1)
                    fd_train.close()
                    
                    fd_test = open(os.path.join(name_fold,'test_occurences.bin'),'wb')
                    pickler.dump(my_test,fd_test,protocol=-1)
                    fd_test.close()                 
            