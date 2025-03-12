import atexit
import os

from .constants import RajceButton
from .logger import Logger
from .main import Rajce, setup
from .utils import InOut, TaskExecutor
from pathlib import Path


CONFIG = InOut.read_json(file=Path(__file__).parent.parent / Path(r'config/config.json'))
Logger.config = CONFIG['logger']
# rajce
atexit.register(Rajce.cleanup)

# set popups
Rajce.homepage_popups = [RajceButton.COOKIES_AGREEMENT]

# set chromedriver
Rajce.driver_file = Path(CONFIG['driver_path']) # Path(__file__).parent.parent / Path(r'drivers/chromedriver')
os.chmod(Rajce.driver_file, 0o755)

# driver options
Rajce.driver_options = CONFIG.get('driver_options')

# task executor
TaskExecutor.task_file = Path(__file__).parent.parent / Path(r'config/rajce_taskfile.txt')