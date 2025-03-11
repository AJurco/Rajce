from collections import deque
import json
from pathlib import Path
from typing import Generator, Callable
from .logger import Logger

logger = Logger(name=__name__, level='INFO')


class InOut:
  @staticmethod
  def write_to_json(file: Path, data: dict|list, encoding='utf8', indent: int=2):
    with open(file=file, mode='w', encoding=encoding) as f:
      json.dump(obj=data, fp=f, indent=indent)

  @staticmethod
  def writeln_to_json(file: Path, func: Generator[dict, None, None], encoding='utf8', indent: int=2):
    data = list(func)
    InOut.write_to_json(file=file, data=data, encoding=encoding, indent=indent)

  @staticmethod
  def readln_json(file: Path, encoding='utf8') -> Generator[dict, None, None]:
    with open(file=file, mode='r', encoding=encoding) as f:
      source = json.load(f)
      if isinstance(source, dict):
        yield source
      if isinstance(source, list):
        yield from source

  @staticmethod
  def read_json(file: Path, encoding='utf8'):
    with open(file=file, mode='r', encoding=encoding) as f:
      return json.load(f)


class TaskExecutor:
  task_file: Path = Path(__file__).parent.parent / Path('config/task_executor.txt')
  tasks: deque = None

  @staticmethod
  def save_progress():
    task_file = TaskExecutor.task_file
    tmp_task_file = task_file.with_stem('tmp_' + task_file.stem)
    InOut.writeln_to_json(file=tmp_task_file, func=(_ for _ in TaskExecutor.tasks))
    tmp_task_file.replace(task_file)

  @classmethod
  def progress_tracker(cls, total: int) -> str:
    percent = 100 * (1 - len(cls.tasks)/total)
    return f'{percent:.1f}%'

  @classmethod
  def init(cls, tasks: Generator[dict, None, None]) -> None:
    if not cls.task_file.parent.exists():
      raise FileExistsError('Task file directory does not exist, create one to proceed.')
    if cls.task_file.exists():
      logger.warning('Existing task file found, resuming task execution.')
    else:
      logger.info('No task file found, creating new one.')
      cls.task_file.touch(exist_ok=True)
      InOut.writeln_to_json(file=cls.task_file, func=tasks)
    cls.tasks = deque(InOut.read_json(cls.task_file))

  @classmethod
  def run_tasks(cls, task_performer: Callable) -> None:
    total = len(cls.tasks)
    try:
      while cls.tasks:
        try:
          task = cls.tasks[0]
          task_performer(task)
          logger.info(f'Completed {cls.progress_tracker(total)}')
        except Exception:
          raise
        else:
          cls.tasks.popleft()
    finally:
      if cls.tasks:
        cls.save_progress()
    logger.info('All tasks completed, deleting task files.')
    cls.task_file.with_stem('tmp_' + cls.task_file.stem).unlink(missing_ok=True)
    cls.task_file.unlink(missing_ok=True)
