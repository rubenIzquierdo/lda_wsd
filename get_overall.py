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

total_ok = total_wr = total_miss = 0
fin = open(sys.argv[1])
#sents = sys.argv[2]
#topics = sys.argv[3]

T = 0 
for n, line in enumerate(fin):
  if n != 0:
    fields = line.strip().split('|')
    if len(fields) >= 9:
      num_senses = int(fields[7])
      if num_senses >= 2:
        total_ok += int(fields[4])
        total_wr += int(fields[5])
        total_miss += int(fields[6])
        T += 1
fin.close()

P = (total_ok)*100.0 / (total_ok + total_wr)
R = (total_ok)*100.0 / (total_ok + total_wr + total_miss)
if P+R == 0:
  F = 0
else:
  F = 2*P*R / (P+R)

#print 'S:%s  T:%s & %.2f &  %.2f &  %.2f\\\\' % (sents, topics, P, R, F)
print 'Precision: %.2f' % P
print 'Recall: %.2f' % R
print 'Fscore: %.2f' % F
print 'Total lemmas: %d' % T             
                                              
