from scipy.stats.stats import pearsonr
import pandas as pd
import statsmodels.formula.api as sm
import statsmodels.stats.api as sms


DATAFILES = [
    # r"C:\Users\verme\Desktop\zTEMP\sfdata_postpost6.csv",
    r"C:\Users\verme\Desktop\zTEMP\sfdata_postpost7.csv"
    ]
VALUES = ['6.0','7.0']
# SCALEVALS = [86*2*1/((88+4)*6), 86*2*1/((88+4)*7)]

dfs = []
for i,DATAFILE in enumerate(DATAFILES):
    print("\n\n***"+DATAFILE+"***")

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        tempdf["F3"] = tempdf["F3%"]
    
    print(f"{VALUES[i]} = {len(tempdf['F3%'])} values")
    
    # print(f'r2 between area & F3% = {pearsonr(tempdf["area"], tempdf["F3"])[0]}')
    # print(f'r2 between MBBR & F3% = {pearsonr(tempdf["MBBR"], tempdf["F3"])[0]}')
    # print(f'r2 between aspectratio & F3% = {pearsonr(tempdf["aspectratio"], tempdf["F3"])[0]}')

    #check confidence band
    band95 = sms.DescrStatsW(tempdf["F3"]).tconfint_mean()
    print(f'confidence band 95% = {band95[0]:.3f} to {band95[1]:.3f}')
    print(f'95% confidence bandwidth  = {band95[1] - band95[0]:.3f}%')


import numpy as np
result = sm.ols(formula="F3 ~ aspectratio + np.log(MBBR)", data=tempdf).fit()

# print(result.params)
# print(result.summary())

