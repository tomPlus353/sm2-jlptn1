import sys
from typing import Collection 
#append models to path
sys.path.append("c:\\Users\\tomas\\Code\\myPython\\Multi-Side Flashcard Project\\SM2 Quiz\\Models")
from Models.config import *
import Models.card as card
from datetime import datetime
import random, os, time, shelve
from supermemo2 import SMTwo


Card = card.Card
MIN_ACTIVE_CARDS = 10
MAX_ACTIVE_CARDS = 10
SKIP_QUIZ = False #skip the actual quiz as if all answers are correct
DUE_DATE_FORMAT = "%Y-%m-%d"
usingBackup = False


def startNewQuiz():
    print("start new quiz")
    cards = getActiveCards()
    print("total cards found: ", cards.count())
    for index in range(len(cards)):
        cards[index].initializeWrongCounts()
        if SKIP_QUIZ:
            cards[index].setPerfectQuiz();
        print(cards[index].to_dict())
    quiz(cards)

def getActiveCards():
    backupCards = getBackupCards()
    if usingBackup:
        print("using backup cards")
        return backupCards
    #collects 
    dueCardsCollection = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
    .where_raw('length(kanji) > 1' ) \
    .where('due_date', "<=", datetime.today().strftime(DUE_DATE_FORMAT)) \
    .group_by("cards.id") \
    .limit(MAX_ACTIVE_CARDS) \
    .get()
    count = dueCardsCollection.count()
    #first check if there are enough  cards that are due today
    if count >= MIN_ACTIVE_CARDS:
        return dueCardsCollection
    #else randomly select remaining cards to get the minimum number needed
    else:
        cardsNeeded = MIN_ACTIVE_CARDS - count #should always return a number greater than zero
        newCardsCollection = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
        .where_raw('length(kanji) > 1' ) \
        .limit(cardsNeeded) \
        .group_by("cards.id") \
        .order_by(db.raw('RANDOM()')) \
        .get() 
        return  dueCardsCollection.merge(newCardsCollection) #returns collection with both completely new cards and cards that are due today.

def getBackupCards():
    d = shelve.open('N1 vocab data backup')
    print("checking if backup exists")
    if "emergency_backup" in d.keys():
        print("need to use backup cards")
        backupCards = d["emergency_backup"]
        global usingBackup
        usingBackup = True
        d.close()
        return backupCards
    d.close()
    return None


def quiz(activeGroup):
    try:
        #causeError = 1 + "1"
        print("Stage 1: Reading")
        canRead = False
        while canRead == False:
            term = random.choice(activeGroup)
            if term.reading_score < 2:
                testReading(term)
            twoCount = 0
            #causeError = 1 + "1"
            for i in activeGroup:
                if i.reading_score == 2:
                    twoCount += 1
            if twoCount == len(activeGroup):
                canRead = True
        print("Stage 2: Writing\nGet out a pen and paper for this next round.")
        canWrite = False
        while canWrite == False:
            term = random.choice(activeGroup)
            if term.writing_score < 2:
                testWriting(term)
            twoCount = 0
            for i in activeGroup:
                if i.writing_score == 2:
                    twoCount += 1
            if twoCount == len(activeGroup):
                break
                #canWrite == True  (program stalls here for some reason)
                
        print("Stage 3: Meaning")
        canUnderstand = False
        while canUnderstand == False:
            term = random.choice(activeGroup)
            if term.understanding_score < 2:
                testMeaning(term)
            twoCount = 0
            for i in activeGroup:
                if i.understanding_score == 2:
                    twoCount += 1
            if twoCount == len(activeGroup):
                break
                #canUnderstand == True (ditto as line 74)
        saveResults(activeGroup)
    #if error before saving data
    except Exception as err:
        print("an error occured before we could fully save your results.")
        d = shelve.open('N1 vocab data backup')
        d["emergency_backup"] = activeGroup
        d.close()
        print(repr(err))
    except KeyboardInterrupt as err:
        print("an error occured before we could fully save your results.")
        d = shelve.open('N1 vocab data backup')
        d["emergency_backup"] = activeGroup
        d.close()
        print(repr(err))
    #if no error
    else:
        answer = input("Do you want to play again?<はい/いいえ>\n>")
        if answer == "いいえ":
            print("Goodbye")
        if answer == "はい":
            startNewQuiz()



#these three functions test different aspects of the target language
def testReading(card):
    #show the Kanji form and the meaning. User has to input the correct reading.
    englishHint =   "" if card.hasOneSuccessfulReview() else "Hint: English definition: {card.definition}\n\n" #only give hint when no successful review yet
    answer = input(f"How do you write {card.kanji} in kana? \n\n \
        {englishHint} \
    Sentence: {str.replace(card.sentence, card.kana,card.kanji)}")
    if answer != card.kana:
        card.reading_score = 0
        card.wrongRead += 1
        print(f"\n\nIncorrect. The correct answer was:\n {card.kana}.")
        time.sleep(1)
    else:
        card.reading_score += 1
        print(randPraise())

#show reading + definition. User need to write the Kanji form and self check.
def testWriting(card):
    englishHint =   "" if card.hasOneSuccessfulReview() else "Hint: English definition: {card.definition}\n\n " #only give hint when no successful review yet
    answer = input(f"\n\nHow do you write {card.kana} in Kanji?\n\n \
        {englishHint} \
    Example: {str.replace(card.sentence, card.kanji,card.kana)}")
    # time.sleep(3)
    # input('Ok, did you manage to write out the Kanji? Hit "Enter" to continue.')
    # answer = input(f'{card.kana} is written as {card.kanji}.\n\nWere you correct?[はい/いいえ]')
    if answer == card.kanji:
        card.writing_score += 1
        print(randPraise()) 
    else:
        card.writing_score = 0
        card.wrongWrite += 1
        print("Incorrect")
        time.sleep(1) 

#Show English Definition. User Responds with the Kanji form.
def testMeaning(card):
    sentenceNoKanji = str.replace(card.sentence, card.kanji,"_")
    sentenceNoKanjiKana = str.replace(sentenceNoKanji, card.kana,"_")
    answer = input(f"\n\nWhat does \"{card.definition}\" mean in Japanese?\nReply with Kanji form if it exists.\n\
    Example: {sentenceNoKanjiKana}") 
    if answer != card.kanji:
        card.understanding_score = 0
        card.wrongMean += 1
        print(f"\nIncorrect. The correct answer was:\n {card.kanji},\n with the reading of:\n {card.kana}.")
        time.sleep(1)
    else:
        card.understanding_score += 1
        print(randPraise())

def saveResults(activeGroup):
    print("saving your results..");
    for card in activeGroup:
        quality = card.calculateAverageQuality()
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
            result = db.table("cards").where("id", card.card_id).update({"due_date": dueDate, 
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
            result = db.table("cards").where("id", card.card_id).update({"due_date": dueDate, 
            "easiness": review.easiness,
            "interval":review.interval,
            "repetitions": review.repetitions
            })
            print("number updated: ",result)
    global usingBackup
    if usingBackup:
        willRemove = input("Do you want to remove backup data? 「はい」／「いいえ」")
        if willRemove == "はい":
            print("removing backup data")
            usingBackup = False
            d = shelve.open('N1 vocab data backup')
            del d["emergency_backup"]
            d.clear
            d.close()

         




def clear():
    # for windows command console
    if os.name == 'nt':
        _ = os.system('clear')

#random praise (From Ireland, just for the craic)     
def randPraise():
    return ["Go on you good thing!","You're class!", "You legend", "You sly dog", "Sound as a pound","Sure now ye're just showing off","Savage","Grand job","You lej","You are some man"][random.randint(0,9)]


if __name__ == "__main__":
    print("run as main")
    startNewQuiz()
    