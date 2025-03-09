from rajce import Rajce, TaskExecutor
import streamlit as st


def main():
  Rajce.start_driver()
  Rajce.user = st.text_input('Rajce username:')
  Rajce.set_homepage()
  # get album -> date mapping
  mapping = Rajce.save_albumdate_mapping()
  tasks = Rajce.get_image_tasks(album_date_mapping=mapping)
  TaskExecutor.init(tasks)
  TaskExecutor.run_tasks(task_performer=Rajce.task_performer)


if __name__ == '__main__':
  main()
