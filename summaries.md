These are some summaries of other 11-411 projects in the past that we looked at
for inspiration.


# Team Hydra

Drop "semantics" for "syntax." That is, instead of trying to extract relations
from the data, like `(X, "in", "Y")`, use the parse trees and manipulate them.

## Question Generation

First, find all the simple predicate sentences you can find. This is the most
reliable way to find facts. These look like `NP VP .`

Second, construct some extra simple predicate sentences by extracting appositive
statements. Appositives look like `NP1 , NP2 ,`, i.e., a noun phrase wrapped by
commas. We can construct a simple predicate sentence by doing `NP1 "is" NP2 .`,
then feed this into the bank of simple predicate sentences we already found.

We'll generate three types of questions:

- Binary questions:
  1. Invert positions of subject and auxiliary verb
  2. Insert "do" if no auxiliary verb. You can conjugate this with the
     `pattern.en` module
- Confounded binary questions:
  1. Substitute subject with a synonym. Use WordNet relations to get synonyms.
- Wh-questions:
  1. Start at simple predicate sentences
  2. Look for specific parts of speech, and use named entity recognition
    - How questions: look for adverb in `VP` of `(NP VP .)`
    - Who/Where/When: look for `NP` in `VP` of `(NP VP .)`, combine with named
      entity recognition
    - "verb what" questions: look for same as above, but use "what" if there
      is no named entity associated with the phrase.
    - "did what" questions: *experimental*: Look for `NP (V NP)` or something
      other than just `V` for the `VP`, then replace the `V` with "did what".
  3. Remove constituent from sentence
  4. Invert like for normal binary questions (swap aux. verb and subject)
  5. Insert appropriate question word at beginning of sentence
  6. Note: you need to focus on direct objects: they're the only things you want
     to replace with a wh-question.

Finally, we'll have to rank the questions we've generated from the dataset. Some
heuristics:
  - good length (not too long)
  - "reliability of certain wh-question words"
  - try for good mix of the three types of questions


## Question Answering

First, it helps to figure out what kind of question we have to answer: binary or
wh-question. You can do this by looking for some specific tags, like `SQ` for
binary questions, or `SBARQ` for questions introduced by wh-questions.

- If we can't figure this out, fall back to fuzzy matching on sentences to
  determine the best answer (think: word vectors, `tf-idf` measure, etc.), print
  out answer without further processing

Convert question into declarative form (do the subject/predicate swap again)

Find best sentences in document using tf-idf measure (not sure how long this
list of best sentences can reasonably be: maybe just one).

Look if each part of the found sentence is in the question's declarative form:
if so, answer yes. Otherwise, answer no.

Wh-words are harder. Once we've found this best sentence, find all words that
match the type of the question word (named entity recognition). Then, in turn,
we remove each matched word from that sentence, and see which one matches up
with the question best now. Tiebreak with length of longest contiguous sequence
of words.

<https://www.youtube.com/watch?v=ujsDOPfgnbk>


# Team Super Fireball Unicorns

## Question Generation

Once we've parsed the sentences, remove trees that
- are too short
- have no verbs
- **have too many pronouns**
  - This one is worth looking at in conjunction with the below strategy

From here, look at simple predicate sentences. Also, generate more of these by
looking for
- appositive phrases
- etc.
  - They mention that they have a lot of hard coded rules, we can start small
    and get there

Generate no questions by "corrupting random words" in hopes of changing the
question, (in particular, swap words with antonyms using WordNet, straight up
changing numbers).

Only introduce wh-words for the subject (never for the direct object).

Ranking:
- penalize for too short/long questions
- penalize for too many negation words
- interestingly, they take a bank of questions and use them to form a grammar.
  They then use this grammar to rank the fluency of their question by checking
  the parse probability.
- try to answer the question with the answering module

Return the best $n$ questions.


## Question Answering

- Fuzzy match important words in the question against sentences in the document.
- Run a stemmer against all the words in each sentence, compute a vector of
  counts for words in that sentence.
- Find the best sentence
- For binary questions:
  - check if all the words are in the found sentence, in which case answer yes,
    otherwise no
- For wh-questions
  - NER-tag the found sentence, match the named entity type of the question with
    types in the answer, then return the smallest parse subtree containing those
    words

<https://www.youtube.com/watch?v=wPQIqiWVDl0>


# Team noahsmith

## Question Generation

Standard stuff

These guys had a lot more heuristics; it might be worth coming back to this once
we've made some headway.


## Question Answering

These guys also did coreference resolution: finding which pronouns point to
which entities in the text. They tokenized by paragraph, and ran it on the
paragraphs. The Stanford tools have something to handle coreference resolution,
but it sounds hard. Worth looking into to step the project up a notch, but not
viable for a minimum working project.

They also list a couple good heuristics for how to select the target sentence
based off of more things than just top tf-idf score.



<https://www.youtube.com/watch?v=0H9RYnh2ScU>
