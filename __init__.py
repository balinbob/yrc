''' this does most of the parsing and editing work '''
import re
import sys

__all__ = ['main', 'pytaggr', 'taggr']
from yamav import *
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
