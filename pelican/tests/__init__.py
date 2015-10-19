import logging
import warnings

from pelican.log import log_warnings

# redirect warnings modulole to use logging instead
log_warnings()

# setup warnings to log DeprecationWarning's and error on
# warnings in pelican's codebase
warnings.simplefilter("default", DeprecationWarning)
warnings.filterwarnings("error", ".*", Warning, "pelican")

# Add a NullHandler to silence warning about no available handlers
logging.getLogger().addHandler(logging.NullHandler())
