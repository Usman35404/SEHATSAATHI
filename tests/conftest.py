"""Never load local credential files during automated tests."""
import os

os.environ['PYTHON_DOTENV_DISABLED'] = '1'
os.environ['FLASK_SKIP_DOTENV'] = '1'
