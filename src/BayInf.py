import pandas as pd
import numpy as np
import statistics as stat
import random
import re
from LoT import else_, streak_, conform_, get_, patternCont_, balance_

# get the data from the 
bestRules = pd.read_csv("../Data/BestRules2B.csv", dtype={"sequence": str, "p_pred": str, "m_pred": str})

def kfoldCV(data):

    # define a k, for k-fold cross validation
    k = 6

    # get the unique participants
    ids = data['p_id'].unique()

    # set seed for reproducability
    random.seed(7331)

    # shuffle them
    random.shuffle(ids)

    # shuffle the dataframe itself, but keep the participant data grouped
    data = data.set_index('p_id').loc[ids].reset_index()

    # add the fold indicators to the dataframe
    data['fold'] = np.repeat(range(k), data.shape[0]/k)

    means = []
    
    # store the predictions with participant id and sequence as identfiers for convient merge with original dataframe
    predictions = pd.DataFrame({'p_id' : [], 'sequence' : [], 'BayFold_pred' : []})

    # loop k amount of times
    for kfold in range(k):

        # get the training data
        train = data[data['fold'] != kfold]

        # get the test data, which has k as fold
        test = data[data['fold'] == kfold]

        # create a new column called for the infered predictions
        Inf_pred = []

        # go over all the data in the test data
        for i in range(test.shape[0]):

            # get the sequence, and define it as x for the evaluation rules for the current sequence
            x = test.iloc[i]['sequence']

            # get the current rules, adding the generator filter gives a higher accuracy for experiment 2B, but lower for experiment 1B
            relRules = train[(train['sequence'] == x) & (train['correct']) & (train['generator'] == test.iloc[i]['generator'])] # & (train['generator'] == test.iloc[i]['generator'])

            # enter the prediction as the mean prediction of all relevant rules for the current sequence three 1's, and two 0's would yield '1'
            # This method results in a higher accuracy for 2B than Bayesian model Averaging, but not for 1B
            #Inf_pred.append('1' if stat.mean(relRules['m_pred'].astype(int)) >= 0.5 else '0')

            # use Bayesian model averaging to get a prediction for the current sequence
            Inf_pred.append('1' if sum((relRules['posterior'] / sum(relRules['posterior']) * relRules['m_pred'].astype(int))) >= 0.5 else '0')

        print("K fold: ", kfold)

        # add the predictions to the test dataframe
        test.insert(8,"inf_pred", Inf_pred)

        # compute the mean accuracy for this k-fold
        means.append(stat.mean(test['p_pred'] == test['inf_pred']))

        # concat the predictions
        predictions = pd.concat([predictions, pd.DataFrame({'p_id' : test['p_id'], 'sequence' : test['sequence'], 'BayFold_pred' : Inf_pred})])

        # print the mean
        print("Mean:", means[kfold])

    print("Mean accuracy of k-fold:", stat.mean(means))
    return stat.mean(means), predictions

def leaveOneOutCV(data):
    """
    This function applied Leave One Out Cross Validation (LOOCV), which is similar to k-fold but with k = n - 1, as each participant is left out
    once.
    """
    
    # initialize some lists to track mean and predictions
    means = []
    all_predictions = []

    # loop k amount of times
    for par in data['p_id'].unique():

        # create a new column called for the infered predictions
        Inf_pred = []

        # get the test data, which is the current participant
        test = data[data['p_id'] == par]

        # get the train data, which is every other participant than the current one
        train = data[data['p_id'] != par]

        # go over all the train data
        for i in range(test.shape[0]):

            # get the sequence, and define it as x for the evaluation rules for the current sequence
            x = test.iloc[i]['sequence']

            # get the current rules, adding the generator filter gives a higher accuracy for experiment 2B, but lower for experiment 1B
            relRules = train[(train['sequence'] == x) & (train['correct']) & (train['generator'] == test.iloc[i]['generator'])] # & (train['generator'] == test.iloc[i]['generator'])

            # use Bayesian model averaging to get a prediction for the current sequence
            Inf_pred.append('1' if sum((relRules['posterior'] / sum(relRules['posterior']) * relRules['m_pred'].astype(int))) >= 0.5 else '0')

        # add the predictions on the current participants data, into the test dataframe
        test.insert(8,"inf_pred", Inf_pred)

        # store the predictions
        all_predictions = all_predictions + Inf_pred

        # compute the mean accuracy
        curMean = stat.mean(test['p_pred'] == test['inf_pred'])

        # append the current mean
        means.append(curMean)

    print(len(all_predictions))
    print("Mean accuracy of LOOCV:", stat.mean(means))
    return stat.mean(means), all_predictions

# perform both cross-validation methods
kfCV_mean, kfoldpredictions = kfoldCV(bestRules)
LOOCV_mean, LOOCVpredictions = leaveOneOutCV(bestRules)

# store the results of both validation methods
bestRules = pd.merge(bestRules, kfoldpredictions, on=['p_id', 'sequence'], how='inner')
bestRules.insert(9,"BayLOOCV_pred", LOOCVpredictions)

# save the data
bestRules.to_csv("../Data/CVResults2B.csv", index=False)

# Used to check the generalizability of each rule on all other rules
def singleRuleValidation(data):
    """
    This fucntion applies the rule of every participant to every other participants data to test their accuracy.
    """
    means = pd.DataFrame({'p_id' : [], 'rule' : [], 'mean' : []})

    # loop k amount of times
    for par in data['p_id'].unique():

        # create a new column called for the infered predictions
        Inf_pred = []

        test = data[data['p_id'] == par]

        train = data[data['p_id'] != par]

        # go over all the data minus one
        for i in range(train.shape[0]):

            # get the sequence, and define it as x for the evaluation rules for the current sequence
            x = train.iloc[i]['sequence']

            # evaluate the rule of the current participant, if the rule did not already make a prediction for that sequence.
            if x in test['sequence']:
                Inf_pred.append(test[test['sequence'] == par]['m_pred'])
            else: Inf_pred.append(eval(test[test['p_id'] == par]['rule'].iloc[0]))

        # add the predictions of the train data to the test dataframe
        train.insert(8,"inf_pred", Inf_pred)

        curMean = stat.mean(train['p_pred'] == train['inf_pred'])
        print("Participant: ", par, "Mean: ", curMean)

        # compute the mean accuracy for this k-fold
        means = pd.concat([means, pd.DataFrame({'p_id' : par, 'rule' : test['rule'].unique(), 'mean' : curMean})])

    print("Mean accuracy of Single Rule Validation:", stat.mean(means['mean']))
    print(means)
