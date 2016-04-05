
import os
TOPLEVEL = os.path.dirname(os.path.realpath(__file__))

if 'CLASSPATH' in os.environ:
    os.environ['CLASSPATH'] += ':' + TOPLEVEL
else:
    os.environ['CLASSPATH'] = TOPLEVEL

os.environ['STANFORD_PARSER'] = TOPLEVEL + '/jars'
os.environ['STANFORD_MODELS'] = TOPLEVEL + '/jars'

os.environ['NLTK_DATA'] = './nltk_data'
