#LDA and WSD#

Experiments on LDA and WSD on the Ancora corpus

##Installation##

As the Ancora corpus can not be distributed by ourselves, you will need to download it by yourself on [http://clic.ub.edu/corpus/es/ancora]. The rest
of installation is automatic by using one installation scripts. In summary:
* Clone this repository: `git clone https://github.com/rubenIzquierdo/lda_wsd`
* Download the ancora corpus and unzip it under lda_wsd/data/ancora_corpus
* Run the installation script `. install.sh` on the lda_wsd folder

This script will install all the dependencies and libraries required (gensim, KafNafParserPy) and the Ancora corpus will be converted to the NAF format automatically
on the folder $PATH/ancora_naf.

##Preparation of the data for 3-FCV##

With the installation in the previous step, the Ancora corpus has been converted to NAF on the folder `ancora_naf`. To generate the data for training and evaluating the system
using FCV you have to call to the extract_ocurrences.py script:
```shell
python extract_ocurrences.py ancora_naf ancora_eval
```

It will read the NAF files from the folder `ancora_naf` and will generate the proper data (one folder for every lemma) under `ancora_eval`. This folder will be the one
used for evaluation.


##Data used for the paper experiments##

The exacts test folds used for the experiments of the paper will be downloaded and unzipped automatically with the installation script. In this way is possible to reproduce all the experiments
and figures. The data will be found on the folder `lda_wsd/ancora_eval_paper`. This folder can be used as it is (make sure you have also the `ancora_naf` folder in the root folder) by the rest
of training and evaluation scripts (and baselines).

##Baselines##

Once the evaluation data folder is prepared. You can run these baselines:
* random: the random baseline
* MFS: the MFS baseline
* MFSfolded: MFS baseline calculated on the folds.

To obtain the figures just run:
```shell
python baselines.py ancora_eval random/MFS/MFSfolded
```

It will print the figures at the end of the process and also it will generate a file (for instance `lemma_out.MFS`) with the performance for every single lemma.


##Training and evuating the system##

The main script for this purpose is the file `train_eval.py`. If you call to the script with the option `-h` you will get the description of the parameters.
```shell
python train_eval.py -h
usage: train_eval.py [-h] -data OCSS_FOLDER -sLDA SENTENCE_WINDOW_LDA -tLDA
                     TOPICS_LDA [-sMFS SENTENCE_WINDOW_MFS] [-tMFS TOPICS_MFS]

Train LDA models and evaluate the result

optional arguments:
  -h, --help            show this help message and exit
  -data OCSS_FOLDER     Path to the data for FCV
  -sLDA SENTENCE_WINDOW_LDA
                        Sentence window for the LDA classifier (int)
  -tLDA TOPICS_LDA      Number of topics for the LDA classifier (int)
  -sMFS SENTENCE_WINDOW_MFS
                        Sentence window for the LDA classifier (int)
  -tMFS TOPICS_MFS      Number of topics for the LDA classifier (int)
```

The parametes are:
* The path to the evaluation data (`ancora_eval`): the -data parameter (required)
* Number of sentences and topics for the LDA classifier: number of topics and sentence size for the context (required)
* Number of sentences and topics for the MFS classifier: number of topics and sentence size for the context (optional), if they are not provided the MFS will not be used.

So, for instance to train and evaluate the system using a sentence window of 2 for the LDA classifier, 10 topics for the LDA classifier, and no MFS classifier, we would run:
```shell
python train_eval.py -data ancora_eval -sLDA 2 -tLDA10 > log.out 2> log.err &
```

It might take some time, so it is recommended to run it on the background. At the end it will generate an output file with all the numbers for every lemma. To get the overall
results for the whole set you have to call to the script get_overall.py:
```shell
python get_overall.py outputfile.txt
```

It will print the precision, recall and F-score. The same experiment as the previous one but creating MFS classifier using 5 sentences as window for extracting the features and 100 topics:
```shell
python train_eval.py -data ancora_eval -sLDA 2 -tLDA10 -sMFS 5 -tMFS 100 > log.out 2> log.err &
```
In this case it will take even longer due to the creation of the MFS models. Again at the end you can use the `get_overall.py` script to get the whole figures.

##Contact##

* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl  rubensanvi@gmail.com
* http://rubenizquierdobevia.com/
