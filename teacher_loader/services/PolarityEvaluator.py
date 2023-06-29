from textblob import TextBlob
from teacher_loader.services.Translator import Translator
from abc import ABC, abstractclassmethod
from typing import Optional


class PolarityEvaluator(ABC):
  
  @abstractclassmethod
  def get_polarity(self, text: str) -> float:
    pass
  
class TextBlobEvaluator(PolarityEvaluator):
  def __init__(self, translator: Optional[Translator]):
    if translator:
      self.translator = translator
  
  def get_polarity(self, text: str) -> float:
    blob: TextBlob
    
    if self.translator:
      trans_text = self.translator.translate(text)
      blob = TextBlob(trans_text)
    else:
      blob = TextBlob(text)

    polarity = blob.sentiment.polarity
    if polarity:
      return polarity
    else:
      return 0.0