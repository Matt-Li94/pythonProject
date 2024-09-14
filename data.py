import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display


data_train_set = pd.read_csv("./data/原始数据_深圳2_副本2.csv")
data_train_set.head()

#

d = data_train_set.corr()
display(d)

plt.subplots(figsize = (12,12))
sns.heatmap(d,annot = True,vmax = 1,square = True,cmap = "Reds")
plt.title('Correlation coefficient map for Shenzhen')
plt.show()