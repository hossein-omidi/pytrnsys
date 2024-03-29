# pylint: skip-file
# type: ignore

import pytrnsys.rsim.executeTrnsys as runTrnsys
import os

execution_instance = runTrnsys.ExecuteTrnsys("./", "System1")
execution_instance.loadDeck()
input_dict = {"ignoreOnlinePlotter": False}
execution_instance.getExecuteTrnsys(input_dict)
print(execution_instance)