
from config import Model
import sentence
from orator.orm import has_many

class Card(Model):

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
