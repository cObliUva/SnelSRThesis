import pandas as pd
import numpy as np
import statistics as stat
import re

# get the results from both model version for each experiment
bestRules_1B = pd.read_csv("../Data/BestRules1B.csv", dtype={"sequence": str, "p_pred": str, "m_pred": str})
bestRules_2B = pd.read_csv("../Data/BestRules2B.csv", dtype={"sequence": str, "p_pred": str, "m_pred": str})

# This follow part contains the rule importance code, which extracts the importance of a rule depending how early it is in the rule.
def extract_rules(s):
    """
    Extract rule names ending in '_' from a function-like string.
    """
    pattern = re.compile(r'(\w+_)\(')
    return pattern.findall(s)

def rule_importance(strings, rule_name):
    """
    Compute the importance of a rule, for a given string. If the rule is present in the string, give it a score of 1 to 0, with x > 0, 
    and 0 if it does not appear in the string. Note that x depends on the number of rules within a string, as shorter strategies rely more on
    its individual rules than longer strategies. Furthmore, the importance can be quantified more thuroughly by checking how often it is 
    responsible for a prediction, but is much more extensive to compute.
    """
    results = []

    # loop over all given strings
    for s in strings:

        # extract the rules into seperate items in a list
        rules = extract_rules(s)

        rules = [rule for rule in rules if rule != "else_"]
        
        # get the index of of the specified rule in the list of rules, and rate its importance based on the position.
        try: importance = pow(0.7, rules.index(rule_name))

        # if it is not present in the list, and returns an error, make the importance 0
        except ValueError:
            importance = 0

        # add the importance to the results
        results.append(importance)

    return results


# get only the participant id's and their rule, and drop duplicates
BR2B = bestRules_2B.loc[:, ['p_id', 'rule']].drop_duplicates()
BR1B = bestRules_1B.loc[:, ['p_id', 'rule']].drop_duplicates()

# add an extra column to indicate the experiment
BR2B['experiment'] = '2B'
BR1B['experiment'] = '1B'

# compute the rule importance of balance and conform, and add the results in an extra column
BR2B['balance'] = rule_importance(BR2B['rule'], 'balance_')
BR1B['balance'] = rule_importance(BR1B['rule'], 'balance_')
BR1B['conform'] = rule_importance(BR1B['rule'], 'conform_')
BR2B['conform'] = rule_importance(BR2B['rule'], 'conform_')

# add the two dataframes together
ruleIntPlot = pd.concat([BR2B, BR1B])

# save data to plot for rule interpretation
ruleIntPlot.to_csv("../Data/ruleIntPlotData.csv", index=False)