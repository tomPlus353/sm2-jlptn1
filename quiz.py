import sys
from typing import Collection 
#append models to path
sys.path.append("c:\\Users\\tomas\\Code\\myPython\\Multi-Side Flashcard Project\\SM2 Quiz")
from Config.config import *
import Models.card as card
from datetime import datetime
import random, os, time, shelve
from supermemo2 import SMTwo
import pyttsx3, concurrent.futures

#set up card data
Card = card.Card
MIN_ACTIVE_CARDS = 3
MAX_ACTIVE_CARDS = 3
SKIP_QUIZ = False #skip the actual quiz as if all answers are correct
DUE_DATE_FORMAT = "%Y-%m-%d"

#Initiate usingBackup switch
usingBackup = False

#set up voice engine
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_JA-JP_HARUKA_11.0"
VOICE_SPEED = 125



def startNewQuiz():
    print("start new quiz")
    cards = getActiveCards()
    print("total cards found: ", cards.count())
    for index in range(len(cards)):
        global usingBackup
        if not usingBackup:
            cards[index].initializeWrongCounts()
        if SKIP_QUIZ:
            cards[index].setPerfectQuiz();
        print(cards[index].to_dict())
        sentences = cards[index].sentences
        sentenceCount = sentences.count()
        print(sentenceCount)
        for index in range(len(sentences)):
            print(sentences[index].to_dict())
    quiz(cards)

def getActiveCards():
    ##use backup cards
    backupCards = getBackupCards()
    if usingBackup:
        print("using backup cards")
        return backupCards
    
    #1. get overdue cards
    dueCardsCollection = Card.where_raw('length(kanji) > 1' ) \
    .where('due_date', "<=", datetime.today().strftime(DUE_DATE_FORMAT)) \
    .limit(MAX_ACTIVE_CARDS) \
    .get()
    count = dueCardsCollection.count()
    #if there are enough  cards that are due today, just return those cards
    if count >= MIN_ACTIVE_CARDS:
        return dueCardsCollection
    #else randomly select remaining cards to get the minimum number needed
    else:
        cardsNeeded = MIN_ACTIVE_CARDS - count #should always return a number greater than zero
        newCardsCollection = Card.where_raw('length(kanji) > 1' ) \
        .limit(cardsNeeded) \
        .order_by(db.raw('RANDOM()')) \
        .get() 
        return  dueCardsCollection.merge(newCardsCollection) #returns collection with both completely new cards and cards that are due today.

def getBackupCards():
    d = shelve.open('N1 vocab data backup')
    print("checking if backup exists")
    if "emergency_backup" in d.keys():
        wantToUseBackup = input("backup detected, use backup?(はい、いいえ)")
        #unless user doesn't say no
        if wantToUseBackup != "いいえ":
            print("using backup..")
            backupCards = d["emergency_backup"]
            global usingBackup
            usingBackup = True
            d.close()
            return backupCards
        print("not using backup..")
        deleteBackup = input("delete existing backup? (はい、いいえ)") 
        if deleteBackup == "はい":
            del d["emergency_backup"]
    d.close()
    return None


def quiz(activeGroup):
    try:
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
        print("Stage 2: Writing\n")
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
        print("an error occured before we could fully save your results, creating backup")
        d = shelve.open('N1 vocab data backup')
        d["emergency_backup"] = activeGroup
        d.close()
        print(repr(err))
    except KeyboardInterrupt as err:
        print("an error occured before we could fully save your results, creating backup")
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


def speakSentence(sentence):
    engine = pyttsx3.init()
    engine.setProperty("voice",VOICE_ID)
    engine.setProperty('rate', VOICE_SPEED)
    engine.say(sentence)
    engine.runAndWait()
    del engine

def speakTextParallel(prompt, sentence):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_tasks = {executor.submit(print, prompt), executor.submit(speakSentence, sentence)}
        for future in concurrent.futures.as_completed(future_tasks):
            try:
                data = future.result()
            except Exception as e:
                print(e)

#these three functions test different aspects of the target language
def testReading(card):
    #show the Kanji form and the meaning. User has to input the correct reading.
    englishHint =   "" if card.hasOneSuccessfulReview() else f"Hint: English definition: {card.definition}\n\n" #only give hint when no successful review yet
    exampleSentence = f"Sentence: {str.replace(card.sentence, card.kana,card.kanji)}"
    answer = input(f"How do you write {card.kanji} in kana? \n\n \
        {englishHint} \
    {exampleSentence}")
    #speakSentence(exampleSentence)
    if answer != card.kana:
        card.reading_score = 0
        card.wrongRead += 1
        feedback(card, isSuccessful=False)
    else:
        card.reading_score += 1
        feedback(card, isSuccessful=True)

#show reading + definition. User need to write the Kanji form and self check.
def testWriting(card):
    englishHint =   "" if card.hasOneSuccessfulReview() else f"Hint: English definition: {card.definition}\n\n " #only give hint when no successful review yet
    exampleSentence = str.replace(card.sentence, card.kanji,card.kana)
    prompt = f"\n\nHow do you write {card.kana} in Kanji?\n\n \
        {englishHint} \
    Example: {exampleSentence}"
    speakTextParallel(prompt,exampleSentence)
    answer = input(">")
    if answer != card.kanji:
        card.writing_score = 0
        card.wrongWrite += 1
        feedback(card, isSuccessful=False)
    else:
        card.writing_score += 1
        feedback(card, isSuccessful=True)

#Show English Definition. User Responds with the Kanji form.
def testMeaning(card):
    sentenceNoKanji = str.replace(card.sentence, card.kanji,"_")
    sentenceNoKanjiKana = str.replace(sentenceNoKanji, card.kana,"_")
    answer = input(f"\n\nWhat does \"{card.definition}\" mean in Japanese?\nReply with Kanji form if it exists.\n\
    Example: {sentenceNoKanjiKana}") 
    if answer != card.kanji:
        card.understanding_score = 0
        card.wrongMean += 1
        feedback(card, isSuccessful=False)
    else:
        card.understanding_score += 1
        feedback(card, isSuccessful=True)


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
    # cls for windows command console else clear for linux
    os.system('cls' if os.name == 'nt' else 'clear')

#random praise (From Ireland, just for the craic)     
def randPraise():
    return ["Go on you good thing!","You're class!", "You legend", "You sly dog", "Sound as a pound","Sure now ye're just showing off","Savage","Grand job","You lej","You are some man"][random.randint(0,9)]

def feedback(card, isSuccessful):
    print(randPraise()) if isSuccessful else print(f"\nIncorrect!")
    time.sleep(0.2)
    print(f"Kanji:    {card.kanji}")
    time.sleep(0.2)
    print(f"Kana:    {card.kana}")    
    time.sleep(0.2)
    print(f"English Definition:    {card.definition}")
    time.sleep(1.5)
    clear()

if __name__ == "__main__":
    #print(sys.path)
    print("run as main")
    startNewQuiz()
    
