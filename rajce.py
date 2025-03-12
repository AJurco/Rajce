from src import Rajce, Logger, TaskExecutor, setup
import streamlit as st

logger = Logger(name=__name__, level='INFO')

def main():
  setup()
  Rajce.start_driver()
  if st.button("Download Images"):
    Rajce.set_user('salomaaje91')
    logger.info(F'User set to {Rajce.user}.')
    # get album -> date mapping
    mapping = Rajce.save_albumdate_mapping()
    tasks = Rajce.get_image_tasks(album_date_mapping=mapping)
    TaskExecutor.init(tasks)
    TaskExecutor.run_tasks(task_performer=Rajce.task_performer)


if __name__ == '__main__':
  main()
  Rajce.cleanup()
  logger.info('Rajce cleanup complete.')
