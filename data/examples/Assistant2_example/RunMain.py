# pylint: skip-file
# type: ignore

import pytrnsys.rsim.executeTrnsys as runTrnsys
import os

execution_instance = runTrnsys.ExecuteTrnsys(".", "solar_dhw")
execution_instance.loadDeck()
input_dict = {"ignoreOnlinePlotter": False}
execution_instance.getExecuteTrnsys(input_dict)
execution_instance.moveFileFromSource()
execution_instance.copyFileFromSource("output_file_name.txt")
execution_instance.executeTrnsys()