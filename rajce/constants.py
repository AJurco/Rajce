from enum import Enum


class RajceButton(Enum):
  COOKIES_AGREEMENT = '//*[@id="didomi-notice-agree-button"]'
  BLACK_FRIDAY_CLOSE = '//*[@id="event-modal"]/div/div/div[3]/a[1]'
  LOAD_MORE_ALBUMS = '//*[@id="user-albums-list"]/div/div/div/div[2]/div/button'
  NEXT_ALBUM_PAGE = '//*[@id="user-albums-list"]/div/div/div/div[2]/div/ul/li[11]/span'
  GOTO_ALBUM_PAGE = lambda page: f'//*[@id="user-albums-list"]/div/div/div/div[2]/div/ul/li[{page + 1}]/span'
  SMALL_SLEEP = 0.5
  TINY_SLEEP = 0.1


class Encoding(Enum):
  UTF8 = 'utf8'
