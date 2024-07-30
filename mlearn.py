import matplotlib.pyplot as plt
import numpy as np
xaxis=np.array([0,5,16])
yaxis=np.array([0,50,7])
# plt.plot(xaxis,yaxis,marker="*")
# plt.plot(xaxis,yaxis,"o--r",ms=10,mec = 'b',mfc = 'w')
plt.plot(xaxis,yaxis,ls="dotted")
#marker|line|color
   #--markers--and---lines---
# '-'	Solid line
# ':'	Dotted line
# '--'	Dashed line
# '-.'	Dashed/dotted line

        #---linestyle---
# linestyle can be written as ls.
#
# dotted can be written as :.
#
# dashed can be written as --.
plt.show()