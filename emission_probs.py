"""Class that stores the number of counts for each word, and for each 
unigram, bigram and trigram tag pattern. It also calculates and stores 
the emission probability of a word given a tag."""

class EmissionProbEmitter(object):

    def __init__(self, source_file=None):
        if source_file is None:
            self.srcname = self.get_sourcename()
        else:
            self.srcname = source_file
        self.counted = False
        self.prob_computed = False
        self.word_emm_probs = {}
        self.word_counts = {}
        self.unigram_counts = {}
        self.bigram_counts = {}
        self.trigram_counts = {}
     
    def get_sourcename(self):
    
        """ FUNCTION: get_sourcename 
            ARGUMETNS: self
            Gets user input for the filename of the source file (should 
            be of the same form as gene.counts). Checks for valid file and 
            if invalid prompts again"""

        valid_file = False
        while not valid_file:
            print "Please supply a valid filename for the source file."
            file_name = raw_input('> ')
            try:
                valid_file = file(file_name)
            except IOError:
                pass
        return file_name

    def get_counts_from_file(self):
     
        """"FUNCTION: get_coutns_from_file
            ARGUMETNS: self

            Generates the dictionaries word_counts, unigram_counts bigram_counts
            and trigram_counts, if not already generated. Calls get_sourcename if 
            necessary"""

        if self.counted:
            print "Already counted"
        else:
            #Mark self as counted
            self.counted = True
            #Attempd to oepn file
            src = open(self.srcname)

            #Step through file and identify record type
            for line in src:

                parts = line.split(' ')
                #Count for a single word-tag combo
                if parts[1] == 'WORDTAG':
                    count = parts[0]
                    tagtype = parts[2]
                    name = parts[3].strip() #Get rid of trailing '\n'
                    #Check to see if word has already been recorded
                    if name in self.word_counts:
                        (self.word_counts[name])[tagtype] = count
                    #If not create a new dict, otherwise add to existant dict
                    else:
                        self.word_counts[name] = {tagtype:count}
                #Unigram, bigram, or trigram count
                else:
                    count = parts[0]
                    seqtype = parts[1]
                    parts[-1] = parts[-1].strip() #Git rid of trailing '\n'
                    args = tuple(parts[2:]) #Make list into tuple

                    #Add to relevent dict. The key is a tuple with all tag types 
                    #in sequence
                    if seqtype == '1-GRAM':
                        self.unigram_counts[args] = count
                    elif seqtype == '2-GRAM':
                        self.bigram_counts[args] = count
                    else:
                        self.trigram_counts[args] = count

            src.close()
        

    def calculate_word_probs(self):
    
        """ FUCNTION: calculate_word_prob
            ARGUMETNGS: self
            
            Generates the dictionary of signle word probabilities. """

        #Check that file has been analyzed
        if not self.counted:
            self.get_counts_from_file()
        #Check for previous execution
        if self.prob_computed:
            print "Probabilities already computed"
        else:

            for word in self.word_counts:
                for tag in self.word_counts[word]:
                    count = (self.word_counts[word])[tag]
                    totalcount = self.unigram_counts[(tag,)]
                    prob = float(count)/float(totalcount)
                    
                    if word in self.word_emm_probs:
                        (self.word_emm_probs[word])[tag] = prob
                    else:
                        (self.word_emm_probs[word]) = {tag:prob}
                        
    def e(self, word, tag):
       
        """ FUNCTION: e
            ARGUMETNS: self
                       word - word ot look up emission probability of
                       tagtype - tag to be analyzes"""


        try:
            return (self.word_emm_probs[word])[tag]
        
        except KeyError:
            return 0


    def best_tag(self, word):

        tagdict = self.word_emm_probs[word]
        vals = tagdict.values()
        keys = tagdict.keys()
        maxprob = max(vals)

        for key in keys:
            if tagdict[key] == maxprob:
                return key

        return None #Or some kind of error. What if word isn't in the dict? I should handle this error at some point
       
    def basic_tagger(self, devfile, destfile):
        #best_tag
        with open(devfile) as dev:
            with open(destfile, 'w') as dest:

                dev = open(devfile)
                dest = open(destfile, 'w')

                for line in dev:
                    word = line.strip()
                    if word in self.word_emm_probs:
                        dest.write(word + ' ' + self.best_tag(word) + '\n')
                    elif word == '':
                        dest.write('\n')
                    else:
                        dest.write(word + ' ' + self.best_tag('_RARE_') + '\n')

    def q(self, tag1, tag2, tag3):

        if not self.counted:
            self.get_counts_from_file()

        bi_count = self.bigram_counts[(tag1, tag2)]
        tri_count = self.trigram_counts[(tag1, tag2, tag3)]

        return float(tri_count)/float(bi_count)


    def viterbi_tagger(self, devfile, destfile):

        possible_tags = self.unigram_counts.keys()

        dev = open(devfile)
        dest = open(destfile, 'w')

        mem = ('*', '*')

        for line in dev:
            word = line.strip()

            if word == '':
                mem = ('*', '*')
                dest.write('\n')

            else:

                maxtag = ''
                prob = 0;

                if word in self.word_counts:
                    word_eff = word
                else:
                    word_eff = '_RARE_'

                for tag in possible_tags:

                    tag = tag[0]
                    
                    if prob < self.q(mem[0], mem[1], tag) * self.e(word_eff, tag):
                        prob =  self.q(mem[0], mem[1], tag) * self.e(word_eff, tag)
                        maxtag = tag
                
                dest.write(word + ' ' + maxtag + '\n')

                mem = (mem[1], tag)
