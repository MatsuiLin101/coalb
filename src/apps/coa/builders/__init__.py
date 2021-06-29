from .livestockfeedlot import *
from .livestockfeedamount import *


def build():
    LivestockFeedlotBuilder().build()
    LivestockFeedamountBuilder().build()
    LivestockSlaughterBuilder().build()
