##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 23-mar-2015                      #  
##############################################

try:
    import cPickle as pickler
except:
    import pickle as pickler

import time
import os
import glob 

from variables import *
from collections import defaultdict    
from generate_lda_model import generate_lda_model



def train_sense(list_train_examples, name_fold, sense, options):
    ret_code = generate_lda_model(list_train_examples, sense, options, name_fold)   
    
    #all_dbpedia_links = []
    #print 'Training sense %s' % sense
    #for naf_filename, term_id, num_sentence in list_occs:
    #    links =  get_links_within_num_sentences(naf_filename, term_id,num_sentence, options['sentence_window'], only_leaves=False)
    #    all_dbpedia_links.extend(links)
        
        #print '\tTerm id %s in file %s' % (term_id, naf_filename)
        #for l in links:
        #    print '\t\t',l.encode('utf-8')
        
        
    #print '\tFull list of dbpedia links for the sense'   , sense
    #for l in sorted(all_dbpedia_links):
    #    print '\t\t%s' % l.encode('utf-8')
        
    return ret_code
    
    
def clean_models(this_folder,options):
    filename_opts = os.path.join(this_folder,options['prefix_models']+'#'+OPTIONS_FILENAME)
    if os.path.exists(filename_opts):
        os.remove(filename_opts)
    for name_fold in glob.glob(os.path.join(this_folder,'fold_*')):
        for this_file in glob.glob(name_fold+'/'+options['prefix_models']+'*'):
            os.remove(this_file)
            
     
def train_folder_lemma(this_folder,options):
    #Load the possible senses
    fd_senses = open(os.path.join(this_folder,'possible_senses'),'r')
    possible_senses = fd_senses.readline().strip().split()
    fd_senses.close()
    start_time = time.time()
    print '%s Training models for %s  List of senses: %s' % (time.strftime('%Y-%m-%dT%H:%M:%S%Z'), this_folder, str(possible_senses))
    print '\tOptions: %s' % str(options)
    #fd_o = open(os.path.join(this_folder,'all_occurrences.bin'),'r')
    #all_occs = pickler.load(fd_o)
    #fd_o.close()
    
    sense_distribution = {}
    fd_d = open(os.path.join(this_folder,'sense_distribution.txt'),'r')
    for line in fd_d:
        sense, freq = line.strip().split()
        sense_distribution[sense] = int(freq)
    fd_d.close()
    
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
        fd_opts = open(os.path.join(this_folder,options['prefix_models']+'#'+OPTIONS_FILENAME),'w')
        pickler.dump(options,fd_opts,0)
        fd_opts.close()
       
        print '\tOption saved to %s' % fd_opts.name
        if len(possible_senses) == 1:
            print '\tIt is a monosemous lemma, nothing to train'
            ret = 0
        else:
            for name_fold in glob.glob(os.path.join(this_folder,'fold_*')):
                fd_train = open(os.path.join(name_fold,'train_occurences.bin'),'rb')
                train_instances = pickler.load(fd_train)
                fd_train.close()
                print '\tFold %s with %d examples' % (name_fold,len(train_instances))
                instances_for_sense = defaultdict(list)
                for naf_filename, term_id, num_sentence, sense in train_instances:
                    instances_for_sense[sense].append((naf_filename, term_id, num_sentence))
                
                for sense, list_train_examples in instances_for_sense.items():
                    print '\t\t==> Sense %s with %d training examples' % (sense.encode('utf-8'),len(list_train_examples))
                    ret_code = train_sense(list_train_examples, name_fold, sense, options)
            ret = 0
    end_time = time.time()
    total_secs = int(end_time - start_time)
    num_min = total_secs/60
    num_secs = total_secs - (num_min*60)
    print '\tTotal time: %d min and %d seconds' % (num_min, num_secs)
    return ret

