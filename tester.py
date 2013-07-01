from emission_probs import EmissionProbEmitter #or some shit like this 


ex = EmissionProbEmitter("new.counts")

ex.calculate_word_probs()
ex.viterbi_tagger('gene.dev', 'new.key')

#print ex.word_emm_probs['_RARE_']





