# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from typing import List

class TeacherLoaderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
  
class Teacher(Item):
  name: str = Field()
  url: str = Field()
  subjects: List[str] = Field()
  comments: List = Field()
  polarity: float = Field()
