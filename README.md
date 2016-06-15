# Beam
Markov Chain IRC bot<br>
Beam is a library that provides access to simple Markov Chains<br>
Beam aims to minimize the disk space used by the database as well<br>
Utilizes the Irx library for IRC connections and command handling<br>
To get Irx:<br>
```
git clone http://github.com/intangere/Irx.git
```
<hr>
Usage:<br>
```
  beam = Beam() #Initialize a Markov Chain state<br>
  vocab, vocab_rev = beam.getVocab() #Get our current vocabulary set<br>
  beam.addToVocab(word) #Add a word to our vocabulary set<br>
  beam.addToChain(sentence) #Adds a sentence to the database via triple sets<br>
  beam.generateText(seed_sentence) #Seed a markov chain state and generate new text<br>
```
