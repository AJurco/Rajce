from src import Rajce, TaskExecutor, Logger
import streamlit as st

logger = Logger(name=__name__, level='INFO')

def main():
  Rajce.start_driver()
  user = st.text_input('Rajce username:')
  Rajce.set_user(user)
  # get album -> date mapping
  mapping = Rajce.save_albumdate_mapping()
  tasks = Rajce.get_image_tasks(album_date_mapping=mapping)
  TaskExecutor.init(tasks)
  TaskExecutor.run_tasks(task_performer=Rajce.task_performer)


def no_streamlit():
  Rajce.start_driver()
  Rajce.set_user('salomaaje91')
  logger.info(F'User set to {Rajce.user}.')
  # get album -> date mapping
  mapping = Rajce.save_albumdate_mapping()
  tasks = Rajce.get_image_tasks(album_date_mapping=mapping)
  TaskExecutor.init(tasks)
  TaskExecutor.run_tasks(task_performer=Rajce.task_performer)


if __name__ == '__main__':
  no_streamlit()
