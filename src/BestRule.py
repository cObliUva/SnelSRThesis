import pandas as pd
import re
import statistics as stat
import math
from LoT import else_, streak_, conform_, get_, patternCont_, balance_, bin_str

def predictOutcome(results):
    """
    This function takes the results and adds a new column to it with the prediction that the found rule would make for each sequence. It also
    creates adds a second column that indicates whether the participants prediction and models prediction are the same.
    """
    # keep track of the predictions
    pred = []

    # go over each row
    for i in range(results.shape[0]):

        # define the sequence as x for the rule
        x = results['sequence'].iloc[i]

        # evaluate the rule on the current sequence and store the result
        pred.append(eval(results['rule'].iloc[i]))

    # load in the models predictions
    results['m_pred'] = pred

    # add a column to indicate whether the participants answer is congruent with our models prediction
    results['correct'] = results['m_pred'] == results['p_pred']

    return results


def bestRule(results):
    """
    This function gets the best rules from the given results, it does so by creating a new dataframe which contains only the 
    p_id, rule, mean, and posterior, sorting that dataframe by mean and then posterior and then grabbing the first occurance of every participant.
    Note that this is actually a bit unneccesary as simply grabbing the top posterior score would be better after the change to the likelihood 
    function in LoT.py which weighs the likelihood heavier so that the prior never becomes more important than the likelihood. 
    """

    # get only the relevant columns
    bRule = results[['p_id', 'rule', 'posterior']]

    # create a empty list for the best rules
    bestRules = pd.DataFrame({'p_id' : [], 'rule' : []})

    # loop over each participant
    for p in pd.unique(bRule['p_id']):
        parDat = bRule[bRule['p_id'] == p]

        # add the single rowed dataframe of the current participant to the rest
        bestRules = pd.concat([bestRules, parDat.nlargest(1, 'posterior').drop(columns = 'posterior')])

    # get the subset the results dataframe by only retaining the best rule for each participant
    bestRules =  pd.merge(results, bestRules, on=['p_id', 'rule'], how='inner')

    return bestRules

# only run this code if the program is run with this file as the main
if __name__ == '__main__':
    print(len(bin_str))

    # load in LoT model results
    mvData = pd.read_csv("../Data/LoT1B.csv")

    # remove unnessesary string elements
    mvData['rule'] = [re.sub('"', '', rule)[10:] for rule in mvData['rule']]

    # change the unnormalized posterior to probabilities
    pmin = mvData['posterior'].min()
    mvData['posterior'] = (mvData['posterior'] - pmin) / (mvData['posterior'].max() - pmin)

    # Load in the whole Excel file
    all_data = pd.ExcelFile("../Data/PredictingOutcomes_ParticipantPredictions.xlsx")

    # extract the worksheet of the study, and ensure the type of the sequence and prediction is a string
    study_data = pd.read_excel(all_data, 'Study 1B', dtype={"sequence": str, "prediction_raw": str})

    # rename the participant ID column
    study_data = study_data.rename(columns = {'participant_id' : 'p_id', 'prediction_raw' : 'p_pred'})
        
    # get the relevant data columns
    rdata = study_data.loc[:, ['p_id', 'sequence', 'p_pred', 'generator']]

    # merge the dataframes
    results = pd.merge(rdata, mvData[['p_id', 'rule', 'posterior']], on = 'p_id')

    # use the found rules of each participant to predict the outcome for their sequences
    results_pred = predictOutcome(results)

    # get the best rules from the results - NOTE: This function selected a simpler rule that has a higher likelihood than a complexer rule in 1B
    BRule  = bestRule(results_pred)

    # print the total average accuracy
    print(BRule['correct'].mean())

    # print the mean accuracy of each participant
    #print(BRule.groupby(['p_id'])['correct'].mean().to_string())

    # store the data of the best rules
    #BRule.to_csv("../Data/BestRules1B.csv", index=False)