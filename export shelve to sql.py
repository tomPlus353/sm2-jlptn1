## export cards from shelve to sql db

import shelve, os, sqlite3
from datetime import datetime

#import module from adjacent folder
import sys
sys.path.append('C:/Users/tomas/Code/myPython/Multi-Side Flashcard Project/Scrape Sentences from Google')
import sentenceFinderGoogle

def checkForSentences():
    #load data from shelve file
    os.chdir(TARGET_DIR)
    data = shelve.open(SHELVE_NAME)
    vocab = data[ACTIVE_VOCAB_KEY]
    data.close()

    #try to add sentences for any vocab without them
    print(type(vocab))
    print(vocab[55])
    print("remaining words without example sentences", len([x for x in vocab if x[3] == ['Sentence not found.'] ]))
    count = 0
    for index, s in enumerate(vocab):
        if vocab[index][3] == ['Sentence not found.']:
            sentencesFound = sentenceFinderGoogle.getSentencesForOneWord(vocab[index][0])
            if len(sentencesFound) > 0 and vocab[index][3] == ['Sentence not found.']:
                vocab[index][3] = sentencesFound
    #backup old data, sync new data and close the connection
    data = shelve.open(SHELVE_NAME)
    data['backup-' + str(datetime.now()) ] = data[ACTIVE_VOCAB_KEY]
    data[ACTIVE_VOCAB_KEY] = vocab
    data.close()

def exportShelveToSql():
    os.chdir(TARGET_DIR)
    data = shelve.open(SHELVE_NAME)
    vocab = data[ACTIVE_VOCAB_KEY]
    data.close()

    con = sqlite3.connect('n1_vocab.db')
    cur= con.cursor()
    cur.execute('''CREATE TABLE cards
               (id integer primary key, kanji text, kana text, definition text, reading_score integer,  writing_score integer, understanding_score integer)''')
    for line in vocab:
        cur.execute('''INSERT INTO cards values (null,?,?,?,0,0,0)''',(line[0],line[1],line[2]))

    cur.execute('''CREATE TABLE sentences
               (id integer PRIMARY KEY, sentence TEXT, card_id INTEGER,
               CONSTRAINT fk_cards
               FOREIGN KEY(card_id)
               REFERENCES cards(id))''')
    #TODO: INSERT SENTENCES INTO DB
    for index, line in enumerate(vocab):
        insertQuery = "INSERT INTO sentences values (null,?," + str(index + 1) + ")"
        print(line[3])
        listOfSentences = line[3]
        for sentence in listOfSentences:
            print(sentence)
            cur.execute(insertQuery,(sentence,))
        
    con.commit()
    cur.execute('''SELECT * from sentences WHERE sentences.card_id = 56 ''')
    print(cur.fetchall())
    con.commit()
    con.close()

if __name__ == "__main__":
    TARGET_DIR = "C:/Users/tomas/Code/myPython/Multi-Side Flashcard Project"
    SHELVE_NAME = 'N1 vocab Data'
    ACTIVE_VOCAB_KEY = 'VocabWithSentences'
    
    #checkForSentences()
    exportShelveToSql()
    

    
