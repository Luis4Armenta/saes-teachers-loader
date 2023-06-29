from typing import Optional
from googletrans import Translator as Trans
from abc import ABC, abstractclassmethod

class Translator(ABC):
  
  @abstractclassmethod
  def translate(self, text: str) -> str:
    pass
  
class GoogleTranslator(Translator):
  def __init__(self):
    self.translator = Trans()
    
  def translate(self, text: str) -> str:
    translation: str = self.translator.translate(text, 'en').text
    
    return translation
