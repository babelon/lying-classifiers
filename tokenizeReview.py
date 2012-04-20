import sys
from tok import Tokenizer
tok = Tokenizer()
for review in sys.stdin:
	print ' '.join(tok.tokenize(review))
