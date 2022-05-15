import sys 
#append models to path
sys.path.append("c:\\Users\\tomas\\Code\\myPython\\Multi-Side Flashcard Project\\SM2 Quiz\\Models")
from Models.config import *
import Models.card as card
Card = card.Card



def startNewQuiz():
    print("start new quiz")
    cards = Card.join("sentences", "sentences.card_id", "=", "cards.id") \
    .where_raw('length(kanji) = 1' ) \
    .group_by("cards.id") \
    .get()

    for card in cards:
        print(card.to_dict())
        print(card.kanji)
        print(card.kana)
        print(card.sentence)
        print(card.definition)
    print("total cards found: ", cards.count())
    
    # #Points 1 and 2
    # os.chdir('C:\\Users\\tomas\\Desktop\\Multi-Side Flashcard Project')
    # d = shelve.open('N1 vocab data')
    # vocab = d['Vocab 1']
    # d.close()
    # activeGroup = setActiveGroup(vocab)
    # #introduction
    # print("Welcome to your Japanese Quiz")
    # print(f"You have {len(activeGroup)} random terms to study. Here they are: ")
    # for i in activeGroup:
    #     print(f"{activeGroup.index(i) + 1}. Kanji: {i[0]}\nKana: {i[1]}\nMeaning: {i[2]}\nStatus: {i[6]}.")

    # input("""Press "enter" to begin""")
    # # 3. b.
    # quiz(activeGroup)

if __name__ == "__main__":
    print("run as main")
    startNewQuiz()
    