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
import time
from python_libs.evaluation_lib import evaluate_mfs, evaluate_lemma_random, evaluate_mfs_folded, evaluate_lemma_lda


if __name__ == '__main__':
    #Examples:
    #  evaluate.py all_occurrences MFS
    #  evaluate.py all_occurrences random
    ###########################
    
    occs_folder = sys.argv[1]
    this_type = sys.argv[2]
    if this_type == 'LDA':
        prefix = sys.argv[3]
    total_ok = total_wr = total_missing = 0
    min_occs = 3
    
    filename_lemma = 'lemma_out.'+this_type
    if this_type == 'LDA':
        filename_lemma +='.'+prefix
        
    fd_lemma = open(filename_lemma,'w')
    fd_lemma.write('%s\t%s\t%s\t%s\t%s\t%s\n' % ('lemma','precision','recall','F','num_senses','num_examples'))
    fd_lemma.close()
    total_words = total_considered = total_mono = 0
    for n,folder in enumerate(glob.glob(occs_folder+'/*')):
        total_words += 1
        print '%d) Evaluating %s (%s)' % (n, folder, time.strftime('%Y-%m-%dT%H:%M:%S%Z'))
        if this_type == 'MFS':
            values=  evaluate_mfs(folder,min_occs)
        elif this_type == 'MFSfolded':
            values =  evaluate_mfs_folded(folder,min_occs)
        elif this_type == 'random':
            values = evaluate_lemma_random(folder,min_occs)
        #elif this_type == 'LDA':
        #    values=  evaluate_lemma_lda(folder,prefix,min_occs)
        
        if values is None: #Ths is because the number of occurences
            continue
        ok, wr, missing, possible_senses, len_occs = values
        
        if len(possible_senses) == 1:
            continue
        
        if len(possible_senses) == 1:
            total_mono += 1 
        total_considered += 1
       
        P = (ok)*100.0/(ok+wr)
        R = (ok)*100.0/(ok+wr+missing)
        if P+R == 0:
            F = 0
        else:
            F = 2*P*R / (P+R)
        fd_lemma = open(filename_lemma,'a')
        fd_lemma.write('%s\t%.2f\t%.2f\t%.2f\t%d\t%d\n' % (folder,P,R,F,len(possible_senses),len_occs))
        fd_lemma.close()
        total_ok += ok
        total_wr += wr
        total_missing += missing
        
    
    print 'Lemma level output: %s' % filename_lemma
    
    filename_overall = 'overall.'+this_type
    if this_type == 'LDA':
        filename_overall+='.'+sys.argv[3]
    fd_overall = open(filename_overall,'w')
    fd_overall.write('Num tokens:\n')
    fd_overall.write('\tOK: %d\n' % total_ok)
    fd_overall.write('\tWRONG: %d\n' % total_wr)
    fd_overall.write('\tMISSING: %d\n' % total_missing)
    fd_overall.write('Figures\n')
    P = (total_ok)*100.0 / (total_ok + total_wr)
    R = (total_ok)*100.0 / (total_ok + total_wr + total_missing)
    if P+R == 0:
        F = 0
    else:
        F = 2*P*R / (P+R)
    fd_overall.write('\tPrecision: %.2f\n' % P)
    fd_overall.write('\tRecall: %.2f\n' % R)
    fd_overall.write('\tFscore: %.2f\n' % F)
    fd_overall.close()
    print 'Overall results at %s' % filename_overall
    faux = open(filename_overall)
    print faux.read()
    faux.close()
    print 'Total words', total_words
    print 'Total considered according to min of occs: %d  %.2f%%' % (total_considered, (total_considered*100.0/total_words))
    print 'Total considered that are monosemous       %d  %.2f%%' % (total_mono, total_mono*100.0/total_considered)

    