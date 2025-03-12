# via streamlit
import streamlit as st
import base64

# 3rd party
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

# base packages
import os
from pathlib import Path
import time
from typing import Generator, List, Set
import xml.etree.ElementTree as ET

# relative imports
from .constants import RajceButton
from .utils import InOut, TaskExecutor
from .logger import Logger


logger = Logger(name=__name__, level='INFO')


def setup():
  if not os.path.exists("/usr/bin/chromedriver"):
    st.write("Setting up Chromium and Chromedriver...")
    os.system("apt-get update")
    os.system("apt-get install -y chromium-browser chromium-chromedriver")
    st.write("Chromedriver installed!")


def get_driver(driver_file: Path, options: list=None):
  if options is not None:
    chrome_options = Options()
    for option in options:
      chrome_options.add_argument(option)
  else:
    chrome_options = None
  # Initialize the WebDriver
  service = Service(driver_file)
  return webdriver.Chrome(service=service, options=chrome_options)


def find_element(driver, xpath):
  return driver.find_element(By.XPATH, xpath)


def scroll_to(driver, element: WebElement):
  driver.execute_script("arguments[0].scrollIntoView();", element)


def wait_on_button(driver, xpath, timeout: int=10):
  return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def parse_rss(rss, namespace: dict=None, look_for: str='media:content', get: str='url') ->list:
  if namespace is None:
    namespace = {'media': 'http://search.yahoo.com/mrss/'}
  root = ET.fromstring(rss)
  results = []
  for element in root.findall('.//item'):
    media_content = element.find(f'.//{look_for}', namespaces=namespace)
    if media_content is not None:
      result = media_content.get(get)
      if result:
        results.append(result)
  return results


def download_image_streamlit(image_url, save_dir: Path, filename: Path):
  try:
    response = requests.get(image_url)
    if response.status_code == 200:    
      # Convert image data to base64
      b64 = base64.b64encode(response.content).decode()
      href = f'<a href="data:image/jpeg;base64,{b64}" download="{save_dir}/{filename}">Download {filename}</a>'
      st.markdown(href, unsafe_allow_html=True)

      # Trigger the download by simulating a click
      js_code = f"""
      <script>
          var link = document.createElement('a');
          link.href = "{href.split('href=')[1].split('><')[0]}";
          link.download = "{filename}";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      </script>
      """
      st.markdown(js_code, unsafe_allow_html=True)
  except Exception as err:
    logger.warning(f'Failed to download an image: {err}.')
    st.error(f'Failed to download an image: {err}.')    


class Rajce:
  # most of these are defined in __init__.py
  user = None
  homepage = None
  download_folder = None # see init
  output_folder = None
  mapping_file = Path(__file__).parent.parent / Path('config/mapping.json')

  driver_file = None  # see init
  driver_options = None  # see init
  driver: webdriver.Chrome = None # see init
  homepage_popups = [] # see init


  @staticmethod
  def cleanup():
    try:
      Rajce.driver.close()
      logger.info('Driver closed at exit.')
    except:
      logger.warning('Could not close driver.')
    if not TaskExecutor.task_file.exists():
      Rajce.mapping_file.unlink(missing_ok=True)

  @staticmethod
  def album_name_from_link(url: str):
    url = url.rstrip('/')
    return url.rsplit('/', 1)[-1]

  @staticmethod
  def img_name_from_link(url: str):
    return url.rsplit('/', 1)[-1]

  @classmethod
  def start_driver(cls):
    cls.driver = get_driver(driver_file=cls.driver_file, options=cls.driver_options)

  @classmethod
  def kill_pop_up(cls, pop_up: RajceButton, timeout: int=10):
    try:
      button = wait_on_button(cls.driver, pop_up.value, timeout)
    except:
      logger.warning(f'Pop-up {pop_up.name} did not appear in time.')
    else:
      button.click()

  @classmethod
  def goto_album_page(cls, page: int) -> None:
    cls.driver.get(cls.homepage.rstrip('/') + f'/?page={page}')

  @classmethod
  def get_album_date(cls):
    try:
      element = cls.driver.find_element(By.CSS_SELECTOR, "span.album-date.rajce-datetime")
      return element.get_attribute('data-start-date')
    except:
      return ''

  @classmethod
  def get_album_links_from_albumpage(cls) ->Set[str]:
    links = set()
    elements = cls.driver.find_elements(by=By.CLASS_NAME, value='photo-wrapper-link')
    for element in elements:
      links.add(element.get_attribute('href'))
    return {link for link in links if '/album/' in link}

  @classmethod
  def goto_album(cls, album: WebElement|str):
    if isinstance(album, WebElement):
      scroll_to(cls.driver, album)
      time.sleep(1)
      album.click()
    elif isinstance(album, str):
      cls.driver.get(album)

  @classmethod
  def goto_homepage(cls) -> None:
    # goto rajce homepage
    cls.driver.get(cls.homepage)
    time.sleep(.5)
    # consent cookies, kill popups like black friday
    for popup in cls.homepage_popups:
      cls.kill_pop_up(popup)

  @classmethod
  def get_album_links(cls) -> List[str]:
    album_links = set()
    i = 0
    while True:
      cls.goto_album_page(i)
      time.sleep(RajceButton.SMALL_SLEEP.value)
      new_links = cls.get_album_links_from_albumpage()
      if new_links.intersection(album_links) or not new_links:
        break
      album_links = album_links.union(new_links)
      i += 1
    return sorted(list(album_links))

  @staticmethod
  def get_img_links(album_link: str) -> list:
    rss = requests.get(url=album_link + '/media.rss').text
    return parse_rss(rss)

  @classmethod
  def get_image_tasks(cls, album_date_mapping: dict=None) -> Generator[dict, None, None]:
    if album_date_mapping is None:
      album_date_mapping = dict()
    cls.goto_homepage()
    album_links = cls.get_album_links()

    # get image links
    for link in album_links:
      img_links = cls.get_img_links(link)
      album_name = cls.album_name_from_link(link)
      album_name = f'{album_date_mapping.get(album_name, "")}_' + album_name

      album_folder = cls.output_folder / Path(album_name)
      # album_folder.mkdir(exist_ok=True, parents=True)

      for url in img_links:
        yield {'url': url, 'album_folder': str(album_folder), 'filename': cls.img_name_from_link(url)}

  @staticmethod
  def task_performer(task: dict, download_function=download_image_streamlit):
    img_name = task['filename']
    save_dir = Path(task['album_folder'])
    download_function(image_url=task['url'], save_dir=save_dir, filename=img_name)
    time.sleep(RajceButton.TINY_SLEEP.value)

  @classmethod
  def get_album_date_mapping(cls) -> dict:
    mapping = dict()

    album_links = cls.get_album_links()
    for link in album_links:
      album_name = cls.album_name_from_link(link)
      logger.info(f'Deriving date of creation for album: {album_name}.')
      cls.goto_album(link)
      time.sleep(RajceButton.SMALL_SLEEP.value)
      date = cls.get_album_date()
      mapping[album_name] = date
      logger.info(f'Album folder {album_name} created.')
    return mapping

  @classmethod
  def save_albumdate_mapping(cls):
    mapping_file = Path(__file__).parent.parent / Path(r'config/mapping.json')
    if not mapping_file.exists():
      mapping = cls.get_album_date_mapping()
      InOut.write_to_json(file=cls.mapping_file, data=mapping)
    return InOut.read_json(file=cls.mapping_file)

  @classmethod
  def set_user(cls, user: str) -> None:
    cls.user = user
    cls.homepage = f"https://{cls.user}.rajce.idnes.cz/"
    cls.output_folder = cls.download_folder / Path(f'rajce_{user}')
