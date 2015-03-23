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
import subprocess
import argparse                                             
from python_libs.train_lib import train_folder_lemma, clean_models
from python_libs.evaluation_lib import evaluate_mfs, evaluate_lemma_random, evaluate_mfs_folded, evaluate_lemma_lda
from python_libs.train_mfs import train_folder_lemma as train_folder_lemma_mfs

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Train LDA models and evaluate the result')
    parser.add_argument('-data', dest='ocss_folder', required=True, help='Path to the data for FCV')
    parser.add_argument('-sLDA', dest='sentence_window_LDA', type=int, required=True, help='Sentence window for the LDA classifier (int)')
    parser.add_argument('-tLDA', dest='topics_LDA', type=int, required=True, help='Number of topics for the LDA classifier (int)')
    parser.add_argument('-sMFS', dest='sentence_window_MFS', type=int, help='Sentence window for the LDA classifier (int)')
    parser.add_argument('-tMFS', dest='topics_MFS', type=int, help='Number of topics for the LDA classifier (int)')

    args = parser.parse_args()
    
    if (args.sentence_window_MFS is None and args.topics_MFS is not None) or (args.sentence_window_MFS is not None and args.topics_MFS is None):
        print>>sys.stderr,'You can not provide just one value for sentence_window/topics on the MFS classifier!'
        print>>sys.stderr,'Provide both values of none of them for not using MFS classifier'
        sys.exit(-1)
        
    occs_folder = args.ocss_folder    
    options = {}
    options['lowercase'] = options['remove_stopwords'] = True
    options['sentence_window'] = args.sentence_window_LDA	#0 3 50
    options['num_topics'] = args.topics_LDA	#3 10 100
    options['min_occs'] = 3
    this_prefix = 'lower%s_rmstop%s_sentwin%d_topics%d_minoccs%d' % (str(options['lowercase']),
                                                                    str(options['remove_stopwords']),
                                                                    options['sentence_window'],
                                                                    options['num_topics'],
                                                                    options['min_occs'])
    options['prefix_models'] = this_prefix
    output_filename = 'output.%s.txt' % this_prefix

    options_mfs = None
    if args.sentence_window_MFS is not None:
        
        options_mfs = {}
        options_mfs['sentence_window'] = args.sentence_window_MFS
        options_mfs['num_topics'] = args.topics_MFS
        options_mfs['min_ocs'] = options['min_occs']
        options_mfs['prefix_models'] = 'MFS'
        options_mfs['lowercase'] = options_mfs['remove_stopwords'] = True


    labels = ['folder','prec','rec','fscore','num_ok','num_wrong','num_missing','num_senses','num_occurrences','time']
    fd = open(output_filename,'w')
    fd.write('|'.join(labels)+'\n')
    fd.close()
    total_ok = total_wr = total_miss = 0 
    for folder_for_lemma in glob.glob(os.path.join(occs_folder,'*')):
        #print 'Unzipping %s' % folder_for_lemma
        #subprocess.check_output(["gunzip","-r",folder_for_lemma])
        
        print>>sys.stderr,'Starting with %s (%s)' % (folder_for_lemma,time.strftime('%Y-%m-%dT%H:%M:%S%Z'))
        
        these_values = []
        these_values.append(folder_for_lemma)
        
        use_mfs_now = None
        if options_mfs is not None:            
            print 'Creating MFS classifiers'
            print 'MFS options',str(options_mfs)
            train_folder_lemma_mfs(folder_for_lemma, options_mfs)
            use_mfs_now = True
        else:
            print 'Not using MFS'
            use_mfs_now = False
            
        train_folder_lemma(folder_for_lemma, options)
        values = evaluate_lemma_lda(folder_for_lemma,this_prefix,options['min_occs'], use_mfs=use_mfs_now)
        if values is not None:
            ok, wr, missing, possible_senses, len_occs = values
            P = (ok)*100.0/(ok+wr)
            R = (ok)*100.0/(ok+wr+missing)
            if P+R == 0: F = 0
            else:        F = 2*P*R / (P+R)
            #clean_models(folder_for_lemma,options)
            
           
            these_values.append('%.2f' % P)
            these_values.append('%.2f' % R)
            these_values.append('%.2f' % F)
            these_values.append('%d' % ok)
            these_values.append('%d' % wr)
            these_values.append('%d' % missing)
            these_values.append('%d' % len(possible_senses))
            these_values.append('%d' % len_occs)       

            total_ok += ok
            total_wr += wr
            total_miss += missing
            P = (total_ok)*100.0/(total_ok+total_wr)
            R = (total_ok)*100.0/(total_ok+total_wr+total_miss)
            if P+R == 0: F = 0
            else:        F = 2*P*R / (P+R)
            print>>sys.stderr,'Accumulated values:'
            print>>sys.stderr,'\tPrec %.2f' % P
            print>>sys.stderr,'\tRec %.2f' % R
            print>>sys.stderr,'\tF %.2f' % F
        
        else:
            these_values.append('Not processed because number of instances smaller than minimum')
            
        these_values.append(time.strftime('%Y-%m-%dT%H:%M:%S%Z'))
        
        fd = open(output_filename,'a')
        fd.write('|'.join(these_values)+'\n')
        fd.close()
        
        #print 'Zipping %s' % folder_for_lemma    
        #subprocess.check_output(["gzip","-r",folder_for_lemma])
        
    
    
    print 'ALL DONE OK',time.strftime('%Y-%m-%dT%H:%M:%S%Z')