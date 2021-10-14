from scipy.stats.stats import pearsonr
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.api as sms


DATAFILES = [
    # r"C:\Users\verme\Desktop\zTEMP\p2p6_edge5_azi_10.csv",
    # r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_10.csv",
    # r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_15.csv",
    # r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_5.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p4_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p5_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p6_edge10_azi_10.csv",
    r"C:\Users\verme\Desktop\zTEMP\p2p7_edge10_azi_10.csv",
    ]
# VALUES = ['6.0','7.0']
ROWLENGTHS = [4,5,6,7]
# SCALEVALS = [86*2*1/((88+4)*6), 86*2*1/((88+4)*7)]

gcr_array = []
otherparam = []
rowlengths = []
for i,DATAFILE in enumerate(DATAFILES):
    print("***"+DATAFILE+"***")

    with open(DATAFILE) as f:
        tempdf = pd.read_csv(f, delimiter=",")
        # for x in tempdf["aspectratio"].tolist():
        #     otherparam.append(x)
        for x in tempdf["F3%"].tolist():
            gcr_array.append(x)
            rowlengths.append(ROWLENGTHS[i])

    
    # print(f"{VALUES[i]} = {len(tempdf['F3%'])} values")
    
    # print(f'r2 between area & F3% = {pearsonr(tempdf["area"], tempdf["F3"])[0]}')
    # print(f'r2 between MBBR & F3% = {pearsonr(tempdf["MBBR"], tempdf["F3"])[0]}')
    # print(f'r2 between aspectratio & F3% = {pearsonr(tempdf["aspectratio"], tempdf["F3"])[0]}')

    #check confidence band
    # band95 = sms.DescrStatsW(tempdf["F3"]).tconfint_mean()
    # print(f'confidence band 95% = {band95[0]:.3f} to {band95[1]:.3f}')
    # print(f'95% confidence bandwidth  = {band95[1] - band95[0]:.3f}%')


    # import numpy as np
    # result = sm.ols(formula="F3 ~ area", data=tempdf).fit()
    # print(result.params)
    # print(result.summary())

    # result = sm.ols(formula="F3 ~ aspectratio", data=tempdf).fit()
    # print(result.params)
#     # print(result.summary())

# result = sm.OLS(gcr_array, sm.add_constant(otherparam)).fit()
# print(result.params)
# print(result.summary())


# results = sms.DescrStatsW(gcr_array).tconfint_mean()
# print(results)

import numpy as np
# print(np.mean(gcr_array))

# print('rmse')
# from sklearn.metrics import mean_squared_error
# rms = mean_squared_error(gcr_array, [24.24]*len(gcr_array), squared=False)
# print(rms)

# print('sdev')
# import statistics
# sd = statistics.stdev(gcr_array)
# print(sd)


print('smols_dev')
model = sm.OLS(gcr_array,sm.add_constant(np.log(rowlengths)))
result = model.fit()
print(result.params)
print(result.summary())


# from statsmodels.graphics.regressionplots import abline_plot
# import matplotlib.pyplot as plt
# import seaborn as sns
# fig, ax = plt.subplots()
# sns.scatterplot(x=gcr_array, y=rowlengths, hue=gcr_array, alpha=0.75, legend=None, palette="crest")#hue_order=sorted([float(x/max(gcr_array)) for x in gcr_array]))
xv = np.linspace(4.0,7.0,len(gcr_array))
# plt.plot(np.log(xv)*result.params[1]+result.params[0], xv, color='r', ls='-', alpha=0.75)
import sklearn.metrics
print('sklearn')
print(sklearn.metrics.r2_score(gcr_array, np.log(xv)*result.params[1]+result.params[0]))


# ax.set_title('Relationship between GCR & Row Spacing')
# plt.legend([f'GCR = ${result.params[0]:.2f} {result.params[1]:.2f}\cdot \log(R)$'])
# plt.xlabel('GCR (%)')
# plt.ylabel('Row Spacing (m)')
# import matplotlib.ticker as ticker
# ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
# ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
# ax.xaxis.grid(color='black', linestyle='dashed', alpha=0.25)
# ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
# ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
# ax.yaxis.grid(color='black', linestyle='dashed', alpha=0.25)
# ax.invert_yaxis()
# OUTPUT_PATH = r"C:\Users\verme\Desktop\zTEMP\outputboxplots"
# plt.savefig(f"{OUTPUT_PATH}\\gcr_rowrow_relationship.png",bbox_inches='tight',dpi=600)



# #module capacity
# fig, ax = plt.subplots()
# xv = np.arange(2009, 2021, 1)
# yv = [290,295,305,320,325,330,340,350,360,410,535,600]
# plt.plot(xv, yv, '-o', alpha=0.75, color='red', linewidth=3)
# ax.set_title('Increase in PV module power (2009-2021)')
# plt.xlabel('Year')
# plt.ylabel('PV Module Output Power (W @ STC)')
# import matplotlib.ticker as ticker
# ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
# ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
# ax.xaxis.grid(color='black', linestyle='dashed', alpha=0.25)
# ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
# ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))
# ax.yaxis.grid(color='black', linestyle='dashed', alpha=0.25)
# for i, txt in enumerate(yv):
#     if txt == yv[-1]: ax.annotate(txt, (xv[i]-0.8, yv[i]))
#     else: ax.annotate(txt, (xv[i]-0.5, yv[i]+10))
    
# OUTPUT_PATH = r"C:\Users\verme\Desktop\zTEMP\outputboxplots"
# plt.savefig(f"{OUTPUT_PATH}\\module_increase.png",bbox_inches='tight',dpi=600)