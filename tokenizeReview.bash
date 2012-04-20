cat $1 | python tokenizeReview.py > $1-2 && mv $1-2 $1
