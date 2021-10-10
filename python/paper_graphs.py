import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

DATAFILES = [r"C:\Users\verme\Desktop\n10000_output.csv",r"C:\Users\verme\Desktop\n10000_output - Copy.csv"]
VALUES = ['new','old']
fig, ax = plt.subplots()
dfs = []
for i,DATAFILE in enumerate(DATAFILES):

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        tempdf['ytick'] = VALUES[i]
        dfs.append(tempdf)

cdf = pd.concat(dfs)
ax.set_title('Results - F3 vs Row Spacing')
ax = sns.boxplot(x=cdf['F3%'], y=cdf['ytick'], notch=True, showfliers=False, orient="h", width=0.4, palette='Set2')
plt.xlabel('$F_3$ (%)')
plt.ylabel('Row Spacing (m)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.xaxis.grid(True)
plt.show()