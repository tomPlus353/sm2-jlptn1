
from datetime import date
from config import Model
import sentence
from orator.orm import has_many,accessor

import math

class Card(Model):
   # __dates__ = ["due_date"]
    
    __timestamps__ = False

    def initializeWrongCounts(self):
       #set wrong count to zero always
       self.wrongRead = 0
       self.wrongWrite = 0
       self.wrongMean = 0
       #when studying a card for the second time, user gets chance to pass with just one correct answer for each category
       if self.hasOneSuccessfulReview():
          self.reading_score = 1
          self.writing_score = 1
          self.understanding_score = 1
      #when studing for the first time 2 correct answers in a row are always required
       else:
          self.reading_score = 0
          self.writing_score = 0
          self.understanding_score = 0

    
    def hasOneSuccessfulReview(self):
       #false is repetitions is none type else true if greater than 1(note: 0 should really be start/default value for repetitions to avoid need to check for null..)
       return False if not self.repetitions else self.repetitions >= 1
    
    def setPerfectQuiz(self):
       self.reading_score = 2
       self.writing_score = 2
       self.understanding_score = 2

       self.wrongRead = 1
       self.wrongWrite = 0
       self.wrongMean = 0
       #self.due_date = date.today()
   
    def partWrittenKanji(self):
       #return character
       return ''.join([charKanji if charKanji not in self.kana else '' for charKanji in self.kanji])

    def calculateAverageQuality(self):
       #start with max quality if 5 and subtract two points for each wrong answer
       print(self.wrongRead)
       readQuality = 5 - (self.wrongRead * 2)
       writeQuality = 5 - (self.wrongWrite * 2)
       meaningQuality = 5 - (self.wrongMean * 2)
       #get average of all qualities
       averageQuality = math.floor((readQuality+writeQuality+meaningQuality) / 3) # floor returns lowest int
       if averageQuality < 0:
          averageQuality = 0
       return averageQuality

    @has_many
    def sentences(self):
        Sentence = sentence.Sentence
        return Sentence
