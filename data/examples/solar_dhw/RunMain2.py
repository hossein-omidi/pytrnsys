
import pytrnsys.trnsys_util.deckTrnsys as DeckTrnsys

# Initialize an instance of DeckTrnsys with the path and name of your Trnsys deck file
deck_path = ".\"
deck_name = "System1"
deck_instance = DeckTrnsys(deck_path, deck_name)

# Load the deck file
deck_contents = deck_instance.loadDeck()

# Now you have the contents of the deck file in the deck_contents variable
# You can proceed to run your simulation using this data