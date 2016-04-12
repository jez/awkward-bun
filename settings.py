
import os

#
# Python caches imports so that this code is only executed once.
# As such, this file should be used only to define constants, or to set
# environment variables.
#

TOPLEVEL = os.path.dirname(os.path.realpath(__file__))

if 'CLASSPATH' in os.environ:
    os.environ['CLASSPATH'] += ':' + TOPLEVEL + '/jars'
else:
    os.environ['CLASSPATH'] = TOPLEVEL + '/jars'

os.environ['STANFORD_PARSER'] = TOPLEVEL + '/jars'
os.environ['STANFORD_MODELS'] = TOPLEVEL + '/jars' + ':' + TOPLEVEL + '/classifiers'

os.environ['NLTK_DATA'] = './nltk_data'

ENGLISH_TAGGER = 'classifiers/english.all.3class.distsim.crf.ser.gz'

# Run `export DEBUG=1` to enable debugging mode
try:
    DEBUG = bool(os.environ['DEBUG'])
except:
    DEBUG = False
