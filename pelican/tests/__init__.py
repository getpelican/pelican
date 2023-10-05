import logging
import warnings

# Direct Warnings to the "py.warnings" logger
logging.captureWarnings(True)

# enable DeprecationWarnings
warnings.simplefilter("default", DeprecationWarning)
# treat warnings in pelican's codebase as errors
warnings.filterwarnings("error", ".*", Warning, "pelican")

# Use: pytest --cli-log-level DEBUG for debug-level logging
logging.basicConfig(handlers=[logging.NullHandler()])
