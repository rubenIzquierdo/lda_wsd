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
from libs.KafNafParserPy import KafNafParser

def create_tokens_per_sent(naf_filename):
    tokens_for_sentencenum = {}
    naf_obj = KafNafParser(naf_filename)
    for token in naf_obj.get_tokens():
        sent_id = token.get_sent()
        if sent_id not in tokens_for_sentencenum:
            tokens_for_sentencenum[sent_id] = [token.get_text()]
        else:
            tokens_for_sentencenum[sent_id].append(token.get_text())
    return tokens_for_sentencenum
        

def get_features(naf_filename, this_sentence, window_sentence):
    tokens_for_sentencenum = None
    sentences_filename = naf_filename+'.sentences'
    if os.path.exists(sentences_filename):
        fd = open(sentences_filename,'rb')
        tokens_for_sentencenum = pickler.load(fd)
        fd.close()
    else:
        tokens_for_sentencenum = create_tokens_per_sent(naf_filename)
        fd = open(sentences_filename,'wb')
        pickler.dump(tokens_for_sentencenum, fd, protocol=-1)
        fd.close()
    tokens = []
    for num_sent, these_tokens in tokens_for_sentencenum.items():
        if abs(int(num_sent) - int(this_sentence)) <= window_sentence:
            tokens.extend(these_tokens)
    return tokens
        
##dbpedia_onto = Cdbpedia_ontology()
#
#def get_dblinks_for_filename(naf_filename):
#    naf_obj = KafNafParser(naf_filename)
#    dblinks_with_sentence = []
#    
#    sentence_for_tokenid = {}
#    for token in naf_obj.get_tokens():
#        sentence_for_tokenid[token.get_id()] = token.get_sent()
#    sentence_for_termid = {}
#    for term in naf_obj.get_terms():
#        sentence_for_termid[term.get_id()] = sentence_for_tokenid[term.get_span().get_span_ids()[0]]
#    
#    for entity in naf_obj.get_entities():
#        types = entity.get_type()
#        deepest_ontolabel = None
#        deepest_depth = 0
#        
#        #Parse the types:
#        for this_type in types.split(','):
#            if 'DBpedia:' in this_type:
#                p = this_type.find(':')+1
#                ontolabel = 'http://dbpedia.org/ontology/%s' % this_type[p:].strip()
#                depth = dbpedia_onto.get_depth(ontolabel)
#                if depth > deepest_depth:
#                    deepest_depth = depth
#                    deepest_ontolabel = ontolabel
#        is_leaf = False
#        if deepest_ontolabel is not None:
#            is_leaf = dbpedia_onto.is_leaf_class(deepest_ontolabel)
#        
#       
#        for ref in entity.get_references():
#            first_termid = ref.get_span().get_span_ids()[0]
#            break
#        if first_termid is not None:
#            list_references = [(ext_ref.get_reference(),float(ext_ref.get_confidence())) for ext_ref in entity.get_external_references()]
#            if len(list_references) > 0:
#                best_link, best_confidence = sorted(list_references, key = lambda t: -t[1])[0]
#                sentence_for_link = sentence_for_termid[first_termid]
#                #dblinks_with_sentence.append((best_link,sentence_for_link))
#                dblinks_with_sentence.append((best_link,sentence_for_link,deepest_ontolabel,deepest_depth, is_leaf))
#    return dblinks_with_sentence
#            
#            
#def get_links_within_num_sentences(naf_filename, term_id,this_sentence, sentence_window,only_leaves):
#    links_filename = naf_filename+'.dblinks'
#    if os.path.exists(links_filename):
#        fd = open(links_filename,'rb')
#        links_and_sentences = pickler.load(fd)
#        fd.close()
#    else:
#        links_and_sentences = get_dblinks_for_filename(naf_filename)
#        fd = open(links_filename,'wb')
#        pickler.dump(links_and_sentences, fd, protocol=-1)
#        fd.close()
#    #cache_links is a lisf of dblinks + sentence [(dblink, s1), (dblink2, s2)
#    selected_links = []
#    #print 'Termid %s, sentence %s' % (term_id, this_sentence)
#    for dblink, dblink_sentence, deepest_ontolabel,deepest_depth, is_leaf in links_and_sentences:
#        #print '  Comparing to %s %s'  % (dblink.encode('utf-8'), dblink_sentence)
#        distance_in_sentences = int(dblink_sentence) - int(this_sentence)
#        if distance_in_sentences <= sentence_window:
#            if not only_leaves or (is_leaf):
#                selected_links.append(dblink)
#    return selected_links

if __name__ == '__main__':
    f = '/home/izquierdo/mybitbucket/sepln_2015/ancora_naf/CESS-CAST-P#178_20010401_b.tbf.naf'
    links = get_dblinks_for_filename(f)
    for l in links:
        print l