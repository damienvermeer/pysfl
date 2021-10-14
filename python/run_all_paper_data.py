

switches = [
    '--fname p2p7_edge10_azi_10 --p2p 7.0 --edgeoffset 10.0 --azimuthtol 10',
    '--fname p2p6_edge10_azi_10 --p2p 6.0 --edgeoffset 10.0 --azimuthtol 10',
    '--fname p2p5_edge10_azi_10 --p2p 5.0 --edgeoffset 10.0 --azimuthtol 10',
    '--fname p2p4_edge10_azi_10 --p2p 4.0 --edgeoffset 10.0 --azimuthtol 10',
    '--fname p2p6_edge5_azi_10 --p2p 6.0 --edgeoffset 5.0 --azimuthtol 10',
    '--fname p2p6_edge0_azi_10 --p2p 6.0 --edgeoffset 0.0 --azimuthtol 10',
    '--fname p2p6_edge10_azi_5 --p2p 6.0 --edgeoffset 10.0 --azimuthtol 5',
    '--fname p2p6_edge10_azi_15 --p2p 6.0 --edgeoffset 10.0 --azimuthtol 15',
]


ncores = 8
n_tests = 500
from subprocess import Popen, CREATE_NEW_CONSOLE

import numpy as np
testids = range(n_tests)
tasks = np.array_split(testids, ncores)

for switch in switches:
    processes = []
    for x in tasks:
        strcall = 'python ' + '\"' + r"C:\Users\verme\GIT\sfl\python\sfl_paper.py"+f'\" --start {min(x)} --end {max(x)} '+ switch
        print(strcall)
        processes.append(Popen(strcall, creationflags=CREATE_NEW_CONSOLE))
    exit_codes = [p.wait() for p in processes]
        