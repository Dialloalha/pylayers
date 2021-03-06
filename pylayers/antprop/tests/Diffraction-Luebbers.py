
# coding: utf-8

# In[1]:

from pylayers.simul.link import *


# In[2]:

DL=DLink(L=Layout('Luebbers.ini'),graph='tvi')


# In[3]:

# get_ipython().magic(u'matplotlib inline')
# DL.L.showG('i')


# In[7]:

DL.a = np.array(([25,21.67,2.]))
# DL.a = np.array(([37.5,52.2,2.]))
DL.b = np.array(([12.5,30.,2.]))
DL.fGHz=np.array(([0.9,1.0]))

DL.Aa=Antenna(typ='Omni',fGHz=DL.fGHz)
DL.Ab=Antenna(typ='Omni',fGHz=DL.fGHz)
# In[8]:

plt.ion()

# In[9]:

DL.eval(diffraction=True,ra_vectorized=True,applywav=False,force=True)


# In[10]:

DL.R


# In[ ]:



