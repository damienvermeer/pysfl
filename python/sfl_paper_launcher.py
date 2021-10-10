ncores = 6
n_tests = 1000
from subprocess import Popen, CREATE_NEW_CONSOLE

import numpy as np
testids = range(n_tests)
tasks = np.array_split(testids, ncores)

for x in tasks:
    strcall = 'python ' + '\"' + r'C:\Users\verme\GIT\sfl\python\sfl_paper.py'+f'\" --start {min(x)} --end {max(x)}'
    print(strcall)
    Popen(strcall, creationflags=CREATE_NEW_CONSOLE)