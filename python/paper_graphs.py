import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

DATAFILES = [
    r"C:\Users\verme\Desktop\zTEMP\p2p4_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p5_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p7_edge10_azi_10.csv",
    ]
VALUES = ['4.0','5.0','6.0','7.0']
SCALEVALS = [86*2*1/((88+4)*4), 86*2*1/((88+4)*5),86*2*1/((88+4)*6), 86*2*1/((88+4)*7)]

OUTPUT_PATH = r"C:\Users\verme\Desktop\zTEMP\outputboxplots"

dfs = []
for i,DATAFILE in enumerate(DATAFILES):

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        tempdf['ytick'] = VALUES[i]
        tempdf['F3%_scaled'] = tempdf['F3%']/SCALEVALS[i]
        dfs.append(tempdf)
        print(f"{VALUES[i]} = {len(tempdf['F3%'])} values")
cdf = pd.concat(dfs)


#non scaled
fig, ax = plt.subplots()
ax.set_title('Results - F3 vs Row Spacing')
ax = sns.boxplot(x=cdf['F3%'], y=cdf['ytick'], notch=True, showfliers=False, orient="h", width=0.4, palette='Set2')
plt.xlabel('$F_3$ (%)')
plt.ylabel('Row Spacing (m)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.xaxis.grid(True)
plt.savefig(f"{OUTPUT_PATH}\\gcr_rowrow_raw_box.png",bbox_inches='tight',dpi=600)


#scaled
fig, ax = plt.subplots()
ax.set_title('Results - F3 vs Row Spacing (Scaled)')
ax = sns.boxplot(x=cdf['F3%_scaled'], y=cdf['ytick'], notch=True, showfliers=False, orient="h", width=0.4, palette='Set2')
plt.xlabel('Scaled $F_3$ ($F_3,ideal$ %)')
plt.ylabel('Row Spacing (m)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
ax.xaxis.grid(True)
plt.savefig(f"{OUTPUT_PATH}\\gcr_rowrow_scaled_box.png",bbox_inches='tight',dpi=600)




#--------------


DATAFILES = [
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_15.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_5.csv",
    ]
VALUES = ['15.0','10.0','5.0']

dfs = []
for i,DATAFILE in enumerate(DATAFILES):

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        tempdf['ytick'] = VALUES[i]
        dfs.append(tempdf)
        print(f"{VALUES[i]} = {len(tempdf['F3%'])} values")
cdf = pd.concat(dfs)


#non scaled
fig, ax = plt.subplots()
ax.set_title('Results - GCR vs Azimuth')
ax = sns.boxplot(x=cdf['F3%'], y=cdf['ytick'], notch=True, showfliers=False, orient="h", width=0.4, palette='Set2')
plt.xlabel('$F_3$ (%)')
plt.ylabel('Azimuth (deg)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.xaxis.grid(True)
plt.savefig(f"{OUTPUT_PATH}\\gcr_azimuth_box.png",bbox_inches='tight',dpi=600)



#--------------


DATAFILES = [
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge0_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge5_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_10.csv",
    ]
VALUES = ['0.0','5.0','10.0']

dfs = []
for i,DATAFILE in enumerate(DATAFILES):

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        tempdf['ytick'] = VALUES[i]
        dfs.append(tempdf)
        print(f"{VALUES[i]} = {len(tempdf['F3%'])} values")
cdf = pd.concat(dfs)


#non scaled
fig, ax = plt.subplots()
ax.set_title('Results - GCR vs Perimeter Setback')
ax = sns.boxplot(x=cdf['F3%'], y=cdf['ytick'], notch=True, showfliers=False, orient="h", width=0.4, palette='Set2')
plt.xlabel('$F_3$ (%)')
plt.ylabel('Setback (m)')
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.xaxis.grid(True)
plt.savefig(f"{OUTPUT_PATH}\\gcr_setback_box.png",bbox_inches='tight',dpi=600)
