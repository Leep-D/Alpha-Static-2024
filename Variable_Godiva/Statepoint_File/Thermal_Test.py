import openmc, h5py
import numpy as np

n = 200


for THERMAL in [False,True]:
    if THERMAL: R_Crit = 0.995
    else: R_Crit = 8.741
    for R in np.round(np.array([0.7,0.8,0.9,1,1.1,1.2,1.3]) * R_Crit,6):
        for PO in [False,True]:
            if THERMAL: ft = 'Th'
            else: ft = 'Fa'
            ak = 'alpha'
            if PO: pd = 'prompt'
            else: pd = 'delayed'
            with h5py.File('sp.{}.{}.{}cm.{}.{}.h5'.format(n,ft,R,ak,pd)) as f:
                Mean_Life_Time = f['alpha_mode_tallies/removal_time'][()]
                print(f.filename,Mean_Life_Time)