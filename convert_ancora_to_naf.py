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
import os
import glob
import shutil
from lxml import etree
from libs.KafNafParserPy import *

def process_node(this_node):
    '''
    Recursive function for a given node
    1) if it's a leaf --> extracts token, lemma, pos and sense
    2) if it's not --> calls to this same function for each of its children
    '''
    num_children = len(this_node.getchildren())
    if num_children == 0:
        #is a leaf node
        token = this_node.get('wd',None)
        lemma = this_node.get('lem',None)
        pos = this_node.get('pos',None)
        if pos is None:
            pos = this_node.tag+'#tag'
        sense = this_node.get('sense',None)
        return [(token,lemma,pos,sense)]
    else:
        my_list = []
        for child in this_node.getchildren():
            sub_list = process_node(child)
            my_list.extend(sub_list)
        return my_list

def convert_file(ancora_filename,output_file):
    '''
    Converts one single ancora file to NAF by reading tokens, lemmas, pos-tags and senses and creating
    the text and term layers.
    '''
    article_obj = etree.parse(ancora_filename)
    this_type = 'NAF'
    naf_obj = KafNafParser(type=this_type)
    naf_obj.set_language('es')
    naf_obj.set_version('1.0')
    num_sentence = 1
    num_token = 1
    offset = 0 
    for sentence in article_obj.findall('sentence'):
        list_nodes = process_node(sentence)     #[(token,lemma,pos,sens)...]
        
        for token,lemma,pos,sense in list_nodes:
            if token is not None:
                #Creating the token
                new_token = Cwf(type=this_type)
                token_id = 'w'+str(num_token)
                new_token.set_id(token_id)
                new_token.set_offset(str(offset))
                new_token.set_sent(str(num_sentence))
                new_token.set_text(token)
                naf_obj.add_wf(new_token)
                
                #Create the term
                new_term = Cterm(type=this_type)
                term_id = 't'+str(num_token)
                new_term.set_id(term_id)
                new_term.set_lemma(lemma)
                new_term.set_pos(pos)
                my_span = Cspan()
                my_span.add_target_id(token_id)
                new_term.set_span(my_span)
                
                #Create the external reference if applies
                if sense is not None:
                    ext_ref = CexternalReference()
                    ext_ref.set_confidence('1.0')
                    reference = 'eng16-'+sense.split(':')[1]+'-'+pos[0]
                    ext_ref.set_reference(reference)
                    ext_ref.set_reftype('ancora_manual_annotation')
                    ext_ref.set_resource('WordNet-1.6')
                    new_term.add_external_reference(ext_ref)
                naf_obj.add_term(new_term)

                
                num_token += 1
                offset = offset + len(token) + 1
        num_sentence += 1
                
            
    lp1 = Clp()
    lp1.set_name('Original tokenization Ancora')
    lp1.set_version('1.0')
    lp1.set_timestamp()
    naf_obj.add_linguistic_processor('text', lp1)

    lp2 = Clp()
    lp2.set_name('Original lemmas, pos and manual annotated senses Ancora')
    lp2.set_version('1.0')
    lp2.set_timestamp()
    naf_obj.add_linguistic_processor('terms', lp2)


    naf_obj.dump(output_file)    
    
        
        
if __name__ == '__main__':
    '''
    Converts the ANCORA corpus in the original format to NAF. You have to provide the
    path to the original folder and it will create a new ancora_naf folder with the NAF
    files
    '''
    #root_folder = '/Users/ruben/WSD/corpora/ancora_corpus/ancora-es-2.0.0'
    subfolders = ['3LB-CAST','CESS-CAST-A','CESS-CAST-AA','CESS-CAST-P']
    
    if len(sys.argv) == 1:
        print>>sys.stderr,'Usage: %s input_folder outputfolder' % sys.argv[0]
        print>>sys.stderr,'\tinput_folder: path to "ancora-es.2.0.0"'
        print>>sys.stderr,'\toutput_folder: the path to the out folder'
        sys.exit(-1)
    
    root_folder = sys.argv[1]   #pointing to ancora-es-2.0.0
    output_folder = sys.argv[2]
    
    
    output_folder = 'ancora_naf'
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)

    N = 0     
    for subfolder in subfolders:
        for ancora_file in glob.glob(root_folder+'/'+subfolder+'/*.xml'):
            basename = (os.path.basename(ancora_file)).replace('.xml','.naf')
            outfile = output_folder+'/'+subfolder+'#'+basename
            convert_file(ancora_file,outfile)
            print str(N)+') NAF file created at:',outfile
            N+=1
            