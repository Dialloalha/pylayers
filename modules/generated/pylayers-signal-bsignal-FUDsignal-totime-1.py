L = DLink(verbose=False)
aktk = L.eval()
L.H.cut()
T1 = L.H.totime()
T1.plot()
L.H.minphas()
T2 = L.H.totime()
T2.plot()