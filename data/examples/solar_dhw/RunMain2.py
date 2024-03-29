# Import the ExecuteTrnsys class from the provided script
from pytrnsys.rsim.executeTrnsys import ExecuteTrnsys

# Path to the directory containing the TRNSYS deck file
deck_path = "."

# Name of the TRNSYS deck file (without the extension)
deck_name = "solar_dhw"

# Initialize an instance of ExecuteTrnsys class
trnsys_executor = ExecuteTrnsys(deck_path, deck_name)

# Load the TRNSYS deck file
trnsys_executor.loadDeck()

# Execute TRNSYS simulation
trnsys_executor.executeTrnsys()

# After execution, you can perform any post-processing steps here
# For example, moving or copying output files to another directory
# trnsys_executor.moveFileFromSource()
# trnsys_executor.copyFileFromSource("output_file_name.txt")