import atexit
from .constants import RajceButton
from .logger import Logger
from .scraper import Rajce
from .utils import InOut
from pathlib import Path


config_file = Path('config.json')
config = InOut.read_json(file=config_file)
Logger.config = config['logger']

# rajce config
atexit.register(Rajce.cleanup)
rajce = config['rajce']
# Rajce.homepage = f"https://{rajce['user']}.rajce.idnes.cz/"
Rajce.output_folder = Path.home() / Path('Downloads') / Path(rajce['user'])

# set popups
Rajce.homepage_popups = [RajceButton.COOKIES_AGREEMENT]

#driver options
# Rajce.driver_file = Path(rajce['chromedriver'])
# look for chromedriver
for file in Path().rglob('*chromedriver.exe'):
  Rajce.driver_file = file
  break

Rajce.driver_options = None if config.get('driver_options') is None else config['driver_options']
