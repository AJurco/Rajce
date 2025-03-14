import atexit
import os

from .constants import RajceButton
from .logger import Logger
from .main import Rajce
from .utils import InOut, TaskExecutor
from pathlib import Path


CONFIG = InOut.read_json(file=Path(__file__).parent.parent / Path(r'config/config.json'))

Logger.config = CONFIG['logger']
# rajce
atexit.register(Rajce.cleanup)
# set popups
Rajce.homepage_popups = [RajceButton.COOKIES_AGREEMENT]
Rajce.download_folder = Path.home() / Path('Downloads')
os.chmod(Rajce.download_folder, 0o755)

# set chromedriver
Rajce.driver_file = Path(__file__).parent.parent / Path(r'drivers/chromedriver.exe')
os.chmod(Rajce.driver_file, 0o755)
# driver options
Rajce.driver_options = CONFIG.get('driver_options')
