import re
from scrapy import Spider
from typing import List, TypedDict
from teacher_loader.items import Teacher

class Comment(TypedDict):
  text: str
  date: str
  likes: int
  dislikes: int

class TeachersSpiderSpider(Spider):
  name = "teachers_spider"
  allowed_domains = ["foroupiicsa.net"]
  start_urls = ["https://foroupiicsa.net/diccionario/"]

  custom_settings = {
    'FEED_URI': 'teachers.json',
    'FEED_FORMAT': 'json',
    'CONCURRENT_REQUEST': 4,
    'ROBOTSTXT_OBEY': True,
    'FEED_EXPORT_ENCODING': 'utf-8'
  }
  

  def parse_teacher(self, response):
    name: str = response.xpath('//p[@class="encontrados"]/span[@class="txbuscado"]/text()').get()
    
    if name:
      subjs: List[str] = response.xpath('//div[@class="row text-center top25 comentariosbox"]//h5/text()').getall()
      subjs = [subj.strip() for subj in subjs]
      subjs = list(set(subjs))
      subjects: List[str] = subjs
      
      comments: List[Comment] = []
      
      raw_comments = response.xpath('//div[@class="row text-center top25 comentariosbox"]/div[@class="panel1"]')
      for raw_comment in raw_comments:
        text: str = raw_comment.xpath('.//p[@class="comentariotx"]/text()').get().strip()
        likes: int = int(raw_comment.xpath('.//div[@class="col-md-3 text-right"]/button[@class="btn btn-default btn-comentario btn-ok tipo_enlace"]/span/text()').get().strip())
        dislikes: int = int(raw_comment.xpath('.//div[@class="col-md-3 text-right"]/button[@class="btn btn-default btn-comentario btn-nop"]/span/text()').get().strip())
        date: str = raw_comment.xpath('.//div[@class="date-comment col-md-6 text-left"]/i/text()').get().strip()

        comment: Comment = {
          'text': text,
          'date': date,
          'likes': likes,
          'dislikes': dislikes
        }

        comments.append(comment)
      
      
      teacher: Teacher = Teacher()
      teacher['name'] = name
      teacher['url'] = response.url
      teacher['subjects'] = subjects
      teacher['comments'] = comments
      
      yield teacher
    
    
  def parse_section(self, response):
    teachers = response.xpath('//ul[@class="lista lisprofes"]/li/span/text()').getall()[:4]
    teachers = [re.sub(r'[^a-zA-ZñÑáéíóúÁÉÍÓÚ\s]', '', name.strip()) for name in teachers]
    teachers = list(set(teachers))
    
    for teacher in teachers:
      teacher: str = teacher.strip()
      
      if len(teacher.split(' ')) < 2:
        continue
      
      teacher_page = self._get_url_for_teacher(teacher)
      
      yield response.follow(teacher_page, callback=self.parse_teacher)
      

  def parse(self, response):
    sections = response.xpath('//ul[@class="pagination abcd"]/li/a/@href').getall()[2:4]
    
    for section in sections:
      yield response.follow(section, callback=self.parse_section)


  def _parse_name(self, name: str) -> str:
    name_without_especial_characters = re.sub(r'[^a-zA-ZñÑáéíóúÁÉÍÓÚ\s]', '', name.strip())
    name_without_spaces = name_without_especial_characters.replace(' ', '+')
    
    return name_without_spaces


  def _get_url_for_teacher(self, teacher: str) -> str:
    name_parsed: str = self._parse_name(teacher.strip())
    
    url = f'/diccionario/buscar/{name_parsed}'
    return url