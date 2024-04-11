from datetime import datetime
import Models.card as card
from Config.config import *
"""
const
"""
DUE_DATE_FORMAT = "%Y-%m-%d"
Card = card.Card


def getActiveCardsCollection(numActiveCards):
    # ##use backup cards
    # backupCards = getBackupCards()
    # if usingBackup:
    #     print("using backup cards")
    #     return backupCards
    
    #1. get overdue cards
    dueCardsCollection = Card.where_raw('length(kanji) > 1' ) \
    .where('due_date', "<=", datetime.today().strftime(DUE_DATE_FORMAT)) \
    .limit(numActiveCards) \
    .get()
    count = dueCardsCollection.count()
    #if there are enough  cards that are due today, just return those cards
    if count >= numActiveCards:
        return dueCardsCollection
    #else randomly select remaining cards to get the minimum number needed
    else:
        cardsNeeded = numActiveCards - count #should always return a number greater than zero
        newCardsCollection = Card.where_raw('length(kanji) > 1' ) \
        .limit(cardsNeeded) \
        .order_by(db.raw('RANDOM()')) \
        .get() 
        return  dueCardsCollection.merge(newCardsCollection) #returns collection with both completely new cards and cards that are due today.

def convertActiveCardsToSession(cardsCollection):
    session = {
        'questions': [],
        'current_question_index': 0,
        'quiz_score': {'correct': 0, 'total': cardsCollection.count()},
        'quiz_ended': False
    }
    print(session)
    # # Create session with questions
    for i in range(cardsCollection.count()):
        # Here, you should fetch questions from your question database or API
        card = cardsCollection[i]
        englishHint = "" if card.hasOneSuccessfulReview() else f"Hint: English definition: {card.definition}\n\n" #only give hint when no successful review yet
        question = {
            "question_id": card.id,
            "question_text": f"What is the reading of{card.kanji}?" + englishHint,
            "example_sentence": f"{str.replace(card.sentence, card.kana,card.kanji)}",
            "answer": card.kana,
            "question_type": "READ"  # Assuming all questions are of READ type for simplicity
        }
        session["questions"].append(question)
    return session

def printCardsDict(cardsCollection):
    for index in range(len(cardsCollection)):
        print(cardsCollection[index].to_dict())
        sentences = cardsCollection[index].sentences
        sentenceCount = sentences.count()
        print(sentenceCount)
        for index in range(len(sentences)):
            print(sentences[index].to_dict())