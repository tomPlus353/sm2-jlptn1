import sys
from typing import Collection 
#append models to path
sys.path.append("c:\\Users\\tomas\\Code\\myPython\\Multi-Side Flashcard Project\\SM2 Quiz\\Models")
from Models.config import *
import Models.card as card
from datetime import datetime
import random, os, time


Card = card.Card
MIN_ACTIVE_CARDS = 3


def startNewQuiz():
    print("start new quiz")
    cards = getActiveCards()
    print("total cards found: ", cards.count())
    
    for index in range(len(cards)):
        print(cards[index].to_dict())
    quiz(cards)

def getActiveCards():
    dueCardsCollection = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
    .where_raw('length(kanji) > 1' ) \
    .where('date_due', "<=", "date('now')") \
    .group_by("cards.id") \
    .get() 
    count = dueCardsCollection.count()
    print(dueCardsCollection.to_json())
    #first check if there are enough  cards that are due today
    if count >= MIN_ACTIVE_CARDS:
        return dueCardsCollection
    #else randomly select remaining cards to get the minimum number needed
    else:
        cardsNeeded = MIN_ACTIVE_CARDS - count #should always return a number greater than zero
        newCardsCollection = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
        .where_raw('length(kanji) > 1' ) \
        .where('date_due', ">", "date('now')") \
        .limit(cardsNeeded) \
        .group_by("cards.id") \
        .order_by(db.raw('RANDOM()')) \
        .get() 
        return  dueCardsCollection.merge(newCardsCollection) #returns collection with both completely new cards and cards that are due today.

def quiz(activeGroup):
    print("Stage 1: Reading")
    canRead = False
    while canRead == False:
        term = activeGroup[random.randint(0,len(activeGroup)-1)]
        if term.reading_score < 2:
            testReading(term)
        twoCount = 0
        for i in activeGroup:
            if i.reading_score == 2:
                twoCount += 1
        if twoCount == len(activeGroup):
            canRead = True
    # print("Stage 2: Writing\nGet out a pen and paper for this next round.")
    # canWrite = False
    # while canWrite == False:
    #     term = activeGroup[random.randint(0,len(activeGroup)-1)]
    #     if term[4] < 2:
    #         testWriting(term)
    #     twoCount = 0
    #     for i in activeGroup:
    #         if i[4] == 2:
    #             twoCount += 1
    #     if twoCount == len(activeGroup):
    #         break
    #         #canWrite == True  (program stalls here for some reason)
            
    # print("Stage 3: Meaning")
    # canUnderstand = False
    # while canUnderstand == False:
    #     term = activeGroup[random.randint(0,len(activeGroup)-1)]
    #     if term[5] < 2:
    #         testMeaning(term)
    #     twoCount = 0
    #     for i in activeGroup:
    #         if i[5] == 2:
    #             twoCount += 1
    #     if twoCount == len(activeGroup):
    #         break
    #         #canUnderstand == True (ditto as line 74)
    print(f"All Done! {randPraise()}")
    answer = input("Do you want to play again?<yes/no>\n>")
    if answer == "no":
        print("Goodbye")
    if answer == "yes":
        startNewQuiz()

#these three functions test different aspects of the target language
def testReading(card):
    #show the Kanji form and the meaning. User has to input the correct reading.
    answer = input(f"How do you write {card.kanji} in kana? \nHint: English definition: {card.definition}")
    if answer != card.kana:
        card.reading_score = 0
        print(f"\n\nIncorrect. The correct answer was:\n {card.kana}.")
        time.sleep(1)
    else:
        card.reading_score += 1
        print(randPraise())

#show reading + definition. User need to write the Kanji form and self check.
def testWriting(card):
    print(f"\n\nHow do you write {card[1]} in Kanji? Try writing my hand. Hint: English definition: {card[2]}")
    time.sleep(1)
    input('Ok, did you manage to write out the Kanji? Hit "Enter" to continue.')
    answer = input(f'{card[1]} is written as {card[0]}.\n\nWere you correct?[yes/no]')
    if answer.lower() == "no":
        card[4] == 0
        print("Incorrect")
        time.sleep(1)
    elif answer.lower() == "yes":
        card[4] += 1
        print(randPraise())

#Show English Definition. User Responds with the Kanji form.
def testMeaning(card):
    answer = input(f"\n\nWhat does \"{card[2]}\" mean in Japanese?\nReply with Kanji form if it exists.\n")
    if answer != card[0]:
        card[5] = 0
        print(f"\nIncorrect. The correct answer was:\n {card[0]},\n with the reading of:\n {card[1]}.")
        time.sleep(1)
    else:
        card[5] += 1
        print(randPraise())

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
    