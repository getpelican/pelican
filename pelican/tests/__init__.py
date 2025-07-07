import logging
import warnings

from pelican.log import log_warnings

# redirect warnings module to use logging instead
# "ignore" means "don't raise on logging an error"
log_warnings("ignore")

# setup warnings to log DeprecationWarning's and error on
# warnings in pelican's codebase
warnings.simplefilter("default", DeprecationWarning)
warnings.filterwarnings("error", ".*", Warning, "pelican")

# Add a NullHandler to silence warning about no available handlers
logging.getLogger().addHandler(logging.NullHandler())
