"""
Lightweight preview server wrapper to avoid local logging.py shadowing stdlib logging
This sets sys.modules['logging'] to standard library logging, then runs uvicorn
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com
import sys
import os
import importlib

# Temporarily remove the current working directory from sys.path so that
# importing 'logging' returns the standard library module instead of our
# local backend/logging.py module that shadows it.
cwd = os.getcwd()
original_sys_path = sys.path.copy()
sys.path = [p for p in sys.path if p and os.path.abspath(p) != os.path.abspath(cwd)]

# Import the standard library logging module
std_logging = importlib.import_module('logging')
sys.modules['logging'] = std_logging

# Restore original sys.path
sys.path = original_sys_path

# Now import the application after setting up logging to avoid the local 'logging.py' shadow
from main_simple import app

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
