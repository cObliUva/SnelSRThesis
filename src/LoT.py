import sys
sys.path.insert(0, 'LOTlib3')
from LOTlib3.Miscellaneous import q, random
from LOTlib3.Grammar import Grammar
from LOTlib3.DataAndObjects import FunctionData, Obj
from LOTlib3.Hypotheses.LOTHypothesis import LOTHypothesis
from LOTlib3.Hypotheses.Priors.RationalRules import RationaRulesPrior
from LOTlib3.Hypotheses.Likelihoods.BinaryLikelihood import BinaryLikelihood
from LOTlib3.Eval import primitive
from LOTlib3.Miscellaneous import qq
from LOTlib3.TopN import TopN
from LOTlib3.Samplers.MetropolisHastings import MetropolisHastingsSampler
from joblib import Parallel, delayed
import multiprocessing
from math import log
import pandas as pd

@primitive
def invert_(pat):

    # this function returns the flipped version of the input e.g., "110" becomes "001", but only if the input is not False
    if pat:
        return ''.join('1' if c == '0' else '0' for c in pat)

def createPat():
    """
    This function is used to create the binary strings with patterns that repeat themselves at least once. They are created from all versions
    of 4 and 3 bit long binary strings that are repeated 2 or three times respectively.
    """
    # initialize the lists
    bit_sets = list()
    binary_str = list()

    # create the 16 versions of three bit binary strings
    for i in range(1 << 4):
        # Convert the current number to a binary string of length n
        bit_sets.append(format(i, '0' + str(4) + 'b'))

    # repeat the 16 created 4 bit patterns.
    binary_str = [st * 2 + st[0] for st in bit_sets]

    # add patterns that are flipped versions
    binary_str = binary_str + [st + invert_(st) + st[0] for st in bit_sets]

    # initialize the lists
    binary_str3 = list()
    bit_sets3 = list()

    # create the 8 versions of three bit binary strings
    for i in range(1 << 3):
        # Convert the current number to a binary string of length n
        bit_sets3.append(format(i, '0' + str(3) + 'b'))
    
    # repeat the 16 created 4 bit patterns.
    binary_str3 = [st * 3 for st in bit_sets3]

    # add patterns that are flipped versions
    binary_str3 = binary_str3 + [st + invert_(st) + st for st in bit_sets3]

    # add 3 bit patterns to other 4 bit binary strings
    for st in binary_str3:
        if st not in binary_str:
            binary_str.append(st)

    # return the list of patterned binary strings
    return binary_str

# create a list with binary strings containing all valid patterns
bin_str = createPat()

# create primitive that takes a the ith character from the given input string x
@primitive
def get_(x, i): 
    return (x[i])

@primitive
def streak_(x, i): 
    if all(list(map(int,list(x[i:8])))):
        return x[7]
    return False

@primitive
def patternCont_(x):
    """
    This primitive checks whether x (the input) contains one of the patterned binary strings (bin_str) and returns the 
    continuation of the pattern. If x is not in bin_str it returns False.
    """

    # loop over all patterns
    for pat in bin_str:

        # check if the pattern is present in x and return its continuation
        if pat[0:8] == x:
            return pat[8]
        
    # otherwise return False
    return False

# A balance function
@primitive
def balance_(x, n): 
    if x.count("1") < n:
        return "1"
    elif x.count("0") < n:
        return "0"
    return False


@primitive
def conform_(x, n): 
    if x.count("1") < n:
        return "0"
    elif x.count("0") < n:
        return "1"
    return False

# The binding function, which takes two RULES and returns the results of the one that does not return False
@primitive
def else_(r, r2):
    if r != False:
        return r
    return r2

# a function to transform a pandas dataframe to a FunctionData object
def dfToObj(dat):
    return FunctionData(input=[dat.iloc[0]], output=dat.iloc[1], alpha=0.999)

def LoTMod(tdata, top, h0, samp):

    print("Processing participant: ", samp)

    # get the sequences and raw predictions for the current participant
    p_data = tdata.loc[tdata['participant_id'] == samp, ['sequence', 'prediction_raw']]

    # apply the transformation into data accepted by the LoT library
    data = p_data.apply(dfToObj, axis = 1)
            
    # generate the top ten best strategies
    for h in MetropolisHastingsSampler(h0, data, steps=500000):
        top << h

    # intialize lists, to extract topN hypothesis data from
    prior = []
    like = []
    post = []
    rule = []

    # extract the data
    for h in top:
        prior.append(h.prior)
        post.append(h.posterior_score)
        like.append(h.likelihood)
        rule.append(qq(h))

    # create a dataframe to concat to the final data
    mvData = pd.DataFrame({'p_id' : samp, 'posterior' : post, 'prior' : prior, 'likelihood' : like, 'rule' : rule})

    return mvData

grammar = Grammar(start='START')

# Create the start conditions where they can either opt for an end-rule, or combination logic
grammar.add_rule('START', '', ['PRE_END'], 1.0)
grammar.add_rule('START', '', ['COMB'], 1.0)

# rule to add recursion to the finding algorithm
grammar.add_rule('COMB', 'else_', ['PRERULE', 'COMB'], 1.0)

# add the ending condition, so that every strategies which result in a direct answer only get situated at the end of a rule
grammar.add_rule('COMB', 'else_', ['PRERULE', 'PRE_END'], 1.0)

# add the pre-rules, so that negation is possible e.g., flipping the last bit, or simply place a bit at the end
grammar.add_rule('PRE_END', '', ['BIT'], 1.0)
grammar.add_rule('PRE_END', '', ['RULEL'], 1.0)
grammar.add_rule('PRE_END', 'invert_', ['RULEL'], 1.0)
grammar.add_rule('PRERULE', '', ['RULE'], 1.0)
grammar.add_rule('PRERULE', 'invert_', ['RULE'], 1.0)

# add rules for people who simply answer a bit, or as a last resort
grammar.add_rule('BIT', "'1'", None, 1.0)
grammar.add_rule('BIT', "'0'", None, 1.0)

# add rules to infer index for a rule
grammar.add_rule('INDEX', '0', None, 1.0)
grammar.add_rule('INDEX', '7', None, 1.0)

# add rules to find streak length   
for n in range(7):
    grammar.add_rule('STREAKL', str(n), None, 1.0)

# add rules to find best number of similar outcomes that induces balancing or conforming
for n in range(1, 5):
    grammar.add_rule('FREQ', str(n), None, 1.0)

# add the strategy rules
grammar.add_rule('RULEL', 'get_', ['x', 'INDEX'], 1.0)
grammar.add_rule('RULE', 'streak_', ['x', 'STREAKL'], 1.0)
grammar.add_rule('RULE', 'balance_', ['x', 'FREQ'], 1.0)
grammar.add_rule('RULE', 'conform_', ['x', 'FREQ'], 1.0)
grammar.add_rule('RULE', 'patternCont_', ['x'], 1.0)

# create the hypothesis which will create a rule that fit an individual input-output set.
class MyHypothesis(LOTHypothesis):
    def __init__(self, **kwargs):
            
        # note that our grammar defined above is passed to MyHypothesis here
        LOTHypothesis.__init__(self, grammar=grammar, **kwargs)
            
    # Question 2: This likelihood function works, but is definitily not accurate in terms of actual probabilities yet.
    def compute_single_likelihood(self, data):
        if self(*data.input) == data.output:
            return log((1.0-data.alpha)/100. + data.alpha)
        else:
            return log((1.0-data.alpha)/100)

if __name__ == '__main__':

    # get the relevant experiment
    experiment = sys.argv[1]

    # Load in the whole Excel file
    all_data = pd.ExcelFile("/gpfs/home6/cfermin/SnelLoTThesis/Data/PredictingOutcomes_ParticipantPredictions.xlsx")

    # extract the worksheet of study 1B, and ensure the type of the sequence and prediction is a string
    data = pd.read_excel(all_data, 'Study ' + experiment, dtype={"sequence": str, "prediction_raw": str})
    
    # creat the hypothesis and initilize the topN results storage
    tn = TopN(N=10)
    h0 = MyHypothesis()
    
    # get all the participants
    participants = pd.unique(data['participant_id'])

    # run the LoT model in parralel
    results = Parallel(n_jobs=64, backend='multiprocessing')(
        delayed(LoTMod)(data, tn, h0, p) for p in participants
    )

    # concattenate the list in results containing small individual dataframes.
    LoTData = pd.concat(results, ignore_index=True)

    # save the data in csv
    LoTData.to_csv("/gpfs/home6/cfermin/SnelLoTThesis/Data/LoT" + experiment + ".csv", index=False)

