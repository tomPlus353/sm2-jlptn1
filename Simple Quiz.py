#sm-2 spaced rep algorithm(supermemo 2)
##Trial run of quiz program
## 1. Uploads vocab from shelve file
## 2. Picks 10 random vocab and puts them in an active group variable
## 3. a. Defines and
##    b. Runs quiz method which is made up of question methods.
## 4. Each question's pass/fail changes the relevant scoring variable
## DONE to here
##
## TO-DO
## 1. Introduce persistance.
## 2. Implement SM-2
## 3. Stop the writing element
## 4. More kinds of questions, random questions etc.
import shelve, os, random, time

def startNewQuiz():
    #Points 1 and 2
    os.chdir('C:\\Users\\tomas\\Desktop\\Multi-Side Flashcard Project')
    d = shelve.open('N1 vocab data')
    vocab = d['Vocab 1']
    d.close()
    activeGroup = setActiveGroup(vocab)
    #introduction
    print("Welcome to your Japanese Quiz")
    print(f"You have {len(activeGroup)} random terms to study. Here they are: ")
    for i in activeGroup:
        print(f"{activeGroup.index(i) + 1}. Kanji: {i[0]}\nKana: {i[1]}\nMeaning: {i[2]}\nStatus: {i[6]}.")

    input("""Press "enter" to begin""")
    # 3. b.
    quiz(activeGroup)
    
def setActiveGroup(vocab):
    random10 = random.sample(range(0,len(vocab)), 3)
    activeGroup = []
    for i in random10:
        activeGroup.append(vocab[i])
    return activeGroup

def clear():
    # for windows command console
    if os.name == 'nt':
        _ = os.system('clear')

#random praise (From Ireland, just for the craic)     
def randPraise():
    return ["Go on you good thing!","You're class!", "You legend", "You sly dog", "Sound as a pound","Sure now ye're just showing off","Savage","Grand job","You lej","You are some man"][random.randint(0,9)]

#Hmmm, have to think about this one carefully...
#def randomSlur


# 3. a.
# Note: if once all terms are correct two in a row for that particular category then we proceed to the next round.
def quiz(activeGroup):
    print("Stage 1: Reading")
    canRead = False
    while canRead == False:
        term = activeGroup[random.randint(0,len(activeGroup)-1)]
        if term[3] < 2:
            testReading(term)
        twoCount = 0
        for i in activeGroup:
            if i[3] == 2:
                twoCount += 1
        if twoCount == len(activeGroup):
            canRead = True
    print("Stage 2: Writing\nGet out a pen and paper for this next round.")
    canWrite = False
    while canWrite == False:
        term = activeGroup[random.randint(0,len(activeGroup)-1)]
        if term[4] < 2:
            testWriting(term)
        twoCount = 0
        for i in activeGroup:
            if i[4] == 2:
                twoCount += 1
        if twoCount == len(activeGroup):
            break
            #canWrite == True  (program stalls here for some reason)
            
    print("Stage 3: Meaning")
    canUnderstand = False
    while canUnderstand == False:
        term = activeGroup[random.randint(0,len(activeGroup)-1)]
        if term[5] < 2:
            testMeaning(term)
        twoCount = 0
        for i in activeGroup:
            if i[5] == 2:
                twoCount += 1
        if twoCount == len(activeGroup):
            break
            #canUnderstand == True (ditto as line 74)
    print(f"All Done! {randPraise()}")
    answer = input("Do you want to play again?<yes/no>\n>")
    if answer == "no":
        print("Goodbye")
    if answer == "yes":
        startNewQuiz()
        



#these three functions test different aspects of the target language
def testReading(card):
    #show the Kanji form and the meaning. User has to input the correct reading.
    answer = input(f"How do you write {card[0]} in kana? \nHint: English definition: {card[2]}")
    if answer != card[1]:
        card[3] = 0
        print(f"\n\nIncorrect. The correct answer was:\n {card[1]}.")
        time.sleep(1)
    else:
        card[3] += 1
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

startNewQuiz()

