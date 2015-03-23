#!/bin/bash

##############################################
# Author:   Ruben Izquierdo Bevia            # 
#           VU University of Amsterdam       #
# Mail:     ruben.izquierdobevia@vu.nl       #
#           rubensanvi@gmail.com             #
# Webpage:  http://rubenizquierdobevia.com   #
# Version:  1.0                              #
# Modified: 23-mar-2015                      #  
##############################################

here=`pwd`

rm -rf libs 2> /dev/null
mkdir libs
cd libs
touch __init__.py

# KafNafPArserPy
git clone https://github.com/cltl/KafNafParserPy.git

cd .. #Back to $here

#Transform ancora to NAF
python convert_ancora_to_naf.py $here/data/ancora_corpus/ancora-es-2.0.0/ $here/ancora_naf

# gensim
python -c 'import gensim' 2> /dev/null

if [ "$?" -eq "1" ];
then
  echo 'GENSIM not installed'
  pip install --user SPARQLWrapper
else
 echo 'Gensim is installed, so we skip this step'
fi
     