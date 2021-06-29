from .livestockfeedlot import *
from .livestockfeedamount import *
from .livestockslaughter import *
from .livestockbyproduct import *


def build():
    LivestockFeedlotBuilder().build()
    LivestockFeedamountBuilder().build()
    LivestockSlaughterBuilder().build()
    LivestockByproductBuilder().build()
