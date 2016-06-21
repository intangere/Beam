import sqlite3 as lite
from random import choice
import os

_POS = '<POS>'
_UPDATE_V_K = "UPDATE data set value = ? where key = ?"
_INSERT_V_K = "INSERT INTO data (key,value) VALUES (?,?)"
_SELECT_V = "SELECT value FROM data WHERE key =?"
_SELECT_ALL = "SELECT * FROM data"
_SELECT_K = "SELECT key from data WHERE key LIKE ?"

class Beam():
    def __init__(self):
        self.db_file = 'data/data.db'
        self.vocab_file = 'data/vocab.in'
        self.vocab, self.vocab_rev = self.getVocab()
    def query(self, database, statement, values):
        con = lite.connect(database)
        cur = con.cursor()
        cur.execute(statement, values)
        values = []
        if statement.startswith("INSERT") or statement.startswith("UPDATE") or statement.startswith("DELETE"):
            con.commit()
        else:
            values = cur.fetchall()
        if con:
            con.close()
        return values
    def addToChain(self, data):
        data = ' '.join([data.strip(), _POS])
        data = data.split(' ')
        data_ = []
        for d in data:
            if 'http' not in d:
                data_.append(d)
        data = data_
        words = self.toIdxs(data)
        if len(data) < 3:
            return
        for words in self.tripleSets(words):
            key = '%s,%s' % (words[0], words[1])
            value = words[2]
            query = self.query(self.db_file, _SELECT_V, (key,))
            if len(query) > 0 and query != None:
                if ',' in query[0][0]:
                    if value not in query[0][0].split(','):
                        value = ','.join([str(query[0][0]), value])
                        query = self.query(self.db_file, _UPDATE_V_K, (value, key,))
                else:
                    if query[0][0] != value:
                        value = ','.join([str(query[0][0]), value])
                        query = self.query(self.db_file, _UPDATE_V_K, (value, key,))
            else:
                query = self.query(self.db_file, _INSERT_V_K, (key, value,))
    def getVocab(self):
        if os.path.isfile(self.vocab_file):
            rev_vocab = []
            with open(self.vocab_file, "r+") as f:
                rev_vocab.extend(f.readlines())
                rev_vocab = [line.strip() for line in rev_vocab]
                vocab = dict([(x, y) for (y, x) in enumerate(rev_vocab)])
                return vocab, rev_vocab
    def addToVocab(self, word):
        f = open(self.vocab_file, 'a+')
        f.write('%s\n' % word)
        f.close()
        self.vocab, self.vocab_rev = self.getVocab()
    def generateRandomText(self):
        key = choice(self.query(self.db_file, _SELECT_ALL, ()))[0]
        idxs = []
        pos = self.vocab[_POS]
        #fail_counter = 0
        while pos not in idxs and len(idxs) < 50:
            query = self.query(self.db_file, _SELECT_V, (key,))
            if len(query) > 0:
                if len(query[0]) > 0:
                    values = query[0][0]
                    if ',' in values:
                        value = choice(values.split(','))
                        idxs.append(value)
                        key = '%s,%s' % (key.split(',')[1], value)
                    else:
                        idxs.append(values)
                        key = '%s,%s' % (key.split(',')[1], values)
        else:
        key = choice(self.query(self.db_file, _SELECT_ALL, ()))[0]
            #else:
            #    fail_counter += 1
        return self.fromIdxs(idxs)

    def generateText(self, seed):
        key = None
        if seed.count(' ') < 1:
            key = self.toIdxs(seed)
            query = self.query(self.db_file, _SELECT_K, ('%' + str(key[0]) + '%',))
            key = choice(query)[0]
        else:
            key = seed.split(' ')
            key = self.toIdxs(key)
            key = '%s,%s' % (key[0], key[1])
        idxs = []
        pos = self.vocab[_POS]
        fail_counter = 0
        while pos not in idxs and len(idxs) < 25 and fail_counter < 5:
            query = self.query(self.db_file, _SELECT_V, (key,))
            if len(query) > 0:
                if len(query[0]) > 0:
                    values = query[0][0]
                    if ',' in values:
                        value = choice(values.split(','))
                        idxs.append(value)
                        key = '%s,%s' % (key.split(',')[1], value)
                    else:
                        idxs.append(values)
                        key = '%s,%s' % (key.split(',')[1], values)
            else:
                fail_counter += 1
        return self.fromIdxs(idxs)

    def toIdxs(self, data):
        idxs = []
        for word in data:
            if not self.vocab.has_key(word):
                self.addToVocab(word)
        self.vocab, self.vocab_recv = self.getVocab()
        for word in data:
            idxs.append(str(self.vocab[word]))
        return idxs
    def fromIdxs(self, idxs):
        data = []
        for idx in idxs:
            if int(idx) != self.vocab[_POS]:
                data.append(self.vocab_rev[int(idx)])
        sentence = ' '.join(data)
        return sentence
    def tripleSets(self, words):
        sets = []
        for i in range(len(words) - 2):
            sets.append((words[i], words[i+1], words[i+2]))
        return sets


