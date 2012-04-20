$SRILM/ngram -ppl test/$1 -lm lm/t2.lm.gz | grep -Eo "logprob= [^ ]* " | perl -i -pe "s/logprob=//g" | perl -i -pe "s/ //g" > tclassprob
$SRILM/ngram -ppl test/$1 -lm lm/d2.lm.gz | grep -Eo "logprob= [^ ]* " | perl -i -pe "s/logprob=//g" | perl -i -pe "s/ //g" > dclassprob
python compareProbs.py > $1-class
rm -f tclassprob
rm -f dclassprob
