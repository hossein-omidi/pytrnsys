import pytrnsys.trnsys_util.readTrnsysFiles as readDck
import pytrnsys.rsim.executeTrnsys as exeTrnsys

# Path to TRNSYS deck file (*.dck)
dck_file_path = r"."  # Update with the actual path to your TRNSYS deck file

# Path to TRNSYS executable
trnsys_exe_path = "C:\\TRNSYS18\\Exe\\TrnEXE64.exe"

# Read TRNSYS deck file
dck_data = readDck.ReadTrnsysFiles(dck_file_path)

# Initialize ExecuteTrnsys object with the required positional arguments
trnsys_simulator = exeTrnsys.ExecuteTrnsys("C:\\Users\\ecer\\PycharmProjects\\pytrnsys_hossein\\data\\examples\\Assistant2_example", "Assistant2")

# # Set TRNSYS executable path
trnsys_simulator.setTrnsysExePath(trnsys_exe_path)

# # Load TRNSYS deck
trnsys_simulator.loadDeck()
inputDict = {"ignoreOnlinePlotter": True}

# Execute TRNSYS simulation
trnsys_simulator.executeTrnsys(inputDict)

