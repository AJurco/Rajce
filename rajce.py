from src import Rajce, Logger, TaskExecutor
import streamlit as st
import os

logger = Logger(name=__name__, level='INFO')

def main():
  Rajce.start_driver()
  user = st.text_input('rajce_username:')
  Rajce.set_user(user)
  logger.info(F'User set to {Rajce.user}.')
  if st.button("Download Images"):
    # get album -> date mapping
    mapping = Rajce.save_albumdate_mapping()
    tasks = Rajce.get_image_tasks(album_date_mapping=mapping)
    TaskExecutor.init(tasks)
    TaskExecutor.run_tasks(task_performer=Rajce.task_performer)


if __name__ == '__main__':
  main()
  Rajce.cleanup()
  logger.info('Rajce cleanup complete.')

