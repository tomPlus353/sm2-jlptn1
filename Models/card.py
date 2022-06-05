
from datetime import date
from config import Model
import sentence
from orator.orm import has_many,accessor

import math

class Card(Model):
   # __dates__ = ["due_date"]
    
    __timestamps__ = False

    def initializeWrongCounts(self):
       self.wrongRead = 0
       self.wrongWrite = 0
       self.wrongMean = 0
    
    def setPerfectQuiz(self):
       self.reading_score = 2
       self.writing_score = 2
       self.understanding_score = 2

       self.wrongRead = 1
       self.wrongWrite = 1
       self.wrongMean = 2
       #self.due_date = date.today()

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

#debugging
# testCard = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
# .where("sentences.id", "=", "5000" ) \
# .get()

# for card in testCard:
#     print(card.kanji)
#     print(card.sentence)
#     print(card.kana)
#     print(card.definition)
# print(testCard.count())

#.where("sentences.sentence", "LIKE", "%あ%" ) \
