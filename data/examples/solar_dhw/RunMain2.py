from pytrnsys.rsim.executeTrnsys import ExecuteTrnsys

# Initialize an instance of ExecuteTrnsys with the path and name of your Trnsys deck file
deck_path = "."
deck_name = "solar_dhw"
execute_trnsys = ExecuteTrnsys(deck_path, deck_name)
execute_trnsys.loadDeck()

input_dict = {"ignoreOnlinePlotter": True}  # Assuming you want to ignore online plotters

# Execute the Trnsys simulation with the input dictionary
execute_trnsys.executeTrnsys(input_dict)