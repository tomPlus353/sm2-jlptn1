from datetime import datetime
import Models.card as card
from Config.config import *
from supermemo2 import SMTwo


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
    # Create session with questions
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

def getAnswerDetails(cardId):
    card = Card.find(cardId)
    return {
        "rightKanji": "Kanji: " + card.kanji,
        "rightKana": "Kana: " + card.kana,
        "rightEng": "English Definition: " + card.definition
    }

def saveCardAnswer(cardId, isCorrect):
    card = Card.find(cardId) #find card to update
    print(cardId)
    print(card.id)
    print(card.kanji)
    #return "early stop for checking right card"
    quality = 5 if isCorrect == True else 1 #calculate quality based on answer
    if not card.due_date:
        print("update for first review")
        print("quality:", quality);
        review = SMTwo.first_review(quality);
        print("review_date:",review.review_date);
        print("easiness:",review.easiness);
        print("interval:",review.interval);
        print("repetitions:",review.repetitions);
        dueDate = review.review_date.strftime(DUE_DATE_FORMAT);
        print("due date: ", dueDate)
        result = db.table("cards").where("id", card.id).update({"due_date": dueDate, 
        "easiness": review.easiness,
        "interval":review.interval,
        "repetitions": review.repetitions
        })
        print("number updated: ",result)
    else:
        print("update for 2nd review+")
        print("quality:", quality);
        review = SMTwo(card.easiness, card.interval, card.repetitions).review(quality);
        print("next review_date:",review.review_date);
        print("new easiness:",review.easiness);
        print("new interval:",review.interval);
        print("new repetitions:",review.repetitions);
        dueDate = review.review_date.strftime(DUE_DATE_FORMAT);
        print("due date: ", dueDate)
        result = db.table("cards").where("id", card.id).update({"due_date": dueDate, 
        "easiness": review.easiness,
        "interval":review.interval,
        "repetitions": review.repetitions
        })
        print("number updated: ",result)

def printCardsDict(cardsCollection):
    pass #the following really slows down the creation of the quiz, so only uncomment for debugging
    # for index in range(len(cardsCollection)):
    #     print(cardsCollection[index].to_dict())
    #     sentences = cardsCollection[index].sentences
    #     sentenceCount = sentences.count()
    #     print(sentenceCount)
    #     for index in range(len(sentences)):
    #         print(sentences[index].to_dict())