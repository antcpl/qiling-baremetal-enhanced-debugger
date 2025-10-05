#!/bin/bash
AFL_SKIP_CPUFREQ=1 /path_to/AFLplusplus/afl-fuzz -t 3000 -P explore -D -g 9 -G 9 -x ./protocol.dict -m none -i afl_inputs -o afl_outputs -U -- python3 ./fuzz.py @@

# -g low limit of the generated input size
# -G hih limit of the generated input size 
# -x specify the dictionary holding valid commands to start mutations from 
# -t specify the timeout limit 