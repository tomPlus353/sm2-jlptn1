from Config.config import *
from . import card
from orator.orm import has_one, belongs_to


class Sentence(Model):
    pass 
    # @has_one
    # def card(self):
    #     Card = card.Card
    #     return Card
    @belongs_to
    def card(self):
        return card.Card