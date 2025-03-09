import logging
from pathlib import Path
import time
import sys


class Logger:
  default_logfolder = Path()
  config = None

  def __init__(self, name: str, level: str, file: str|Path=None):
    name = name if name == '__main__' else f'__main__.{name}'
    self._logger = logging.getLogger(name)
    self._logger.setLevel(level)

    if name == '__main__':
      self.add_console_handler()
      if file is not None:
        self.add_file_handler(Path(file))

  @staticmethod
  def logfile_name(file: Path) -> Path:
    return Path(f"{file.stem}_{time.strftime('%Y%m%d%H%M%S')}.log")

  @classmethod
  def determine_logfile(cls, file: Path) -> Path:
    if file.name == str(file):
      return Logger.default_logfolder / cls.logfile_name(file)
    return file

  def add_console_handler(self) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(Logger.config['level'])
    handler.setFormatter(logging.Formatter(Logger.config['console_format']))
    self._logger.addHandler(handler)

  def add_file_handler(self, file: Path) -> None:
    logfile = Logger.determine_logfile(file)
    logfile.parent.mkdir(exist_ok=True, parents=True)

    handler = logging.FileHandler(filename=logfile, mode=Logger.config['mode'], encoding=Logger.config['encoding'])
    handler.setLevel(Logger.config['level'])
    handler.setFormatter(logging.Formatter(Logger.config['file_format']))
    self._logger.addHandler(handler)

  def info(self, msg):
    self._logger.info(msg)

  def debug(self, msg):
    self._logger.debug(msg)

  def warning(self, msg):
    self._logger.warning(msg)

  def error(self, msg):
    self._logger.error(msg)

  def critical(self, msg):
    self._logger.critical(msg)
