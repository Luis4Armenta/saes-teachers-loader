# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from itemadapter import ItemAdapter
from teacher_loader.items import Teacher

class TeacherLoaderPipeline:
    def process_item(self, item, spider):
        return item
      
class MongoPipeline:
  def __init__(self):
    self.mongo_uri = 'localhost'
    self.mongo_port = 27017
    self.mongo_db = 'teachers_dictionary'
    self.collection_name_of_teachers = 'teachers'
    self.collection_name_of_subjects = 'subjects'
    
  def open_spider(self, spider):
    self.client = pymongo.MongoClient(self.mongo_uri)
    self.db = self.client[self.mongo_db]
    
    self.teachers_collection = self.db[self.collection_name_of_teachers]
    self.subjects_collection = self.db[self.collection_name_of_subjects]
    
  def close_spider(self, spider):
    self.client.close()
  
  def process_item(self, item: Teacher, spider):
    subjects = item['subjects']
    item['subjects'] = []
    
    teacher = self.teachers_collection.find_one({"name": item['name']})
    
    if teacher is None:
      teacher_id = self.teachers_collection.insert_one(ItemAdapter(item).asdict()).inserted_id
    else:
      teacher_id = teacher["_id"]
    
    for subject in subjects:
      self.__add_subject_to_teacher(teacher_id, subject)
    
    item["subjects"] = subjects
    
    return item
  
  def __add_subject_to_teacher(self, teacher_id, subject_name: str):
    # Verificar si la asignatura ya existe en la colección
    subject = self.subjects_collection.find_one({"name": subject_name})
    
    # Si la asignatura no existe, crearla y obtener su ID
    if subject is None:
        subject = {"name": subject_name, "teachers": [teacher_id]}
        subject_id = self.subjects_collection.insert_one(subject).inserted_id
    else:
        subject_id = subject["_id"]

        # Verificar si el profesor ya está en la lista de profesores de la asignatura
        if teacher_id not in subject["teachers"]:
            # Agregar el profesor a la lista de profesores de la asignatura
            self.subjects_collection.update_one({"_id": subject_id}, {"$addToSet": {"teachers": teacher_id}})
    
    # Agregar la referencia de la asignatura al profesor
    self.teachers_collection.update_one({"_id": teacher_id}, {"$addToSet": {"subjects": subject_id}})

