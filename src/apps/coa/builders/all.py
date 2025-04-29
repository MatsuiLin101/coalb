import traceback

from apps.coa.builders.cropcost import CropCostBuilder
from apps.coa.builders.cropprice import CropPriceOriginBuilder
from apps.coa.builders.cropproduce import CropProduceTotalBuilder
from apps.coa.builders.livestockbyproduct import LivestockByproductBuilder
from apps.coa.builders.livestockfeedamount import LivestockFeedAmountBuilder
from apps.coa.builders.livestockfeedlot import LivestockFeedlotBuilder
from apps.coa.builders.livestockslaughter import LivestockSlaughterBuilder
from apps.coa.builders.producevalue import TotalValueBuilder

builders = [
    CropCostBuilder,
    CropPriceOriginBuilder,
    CropProduceTotalBuilder,
    LivestockByproductBuilder,
    LivestockFeedAmountBuilder,
    LivestockFeedlotBuilder,
    LivestockSlaughterBuilder,
    TotalValueBuilder,
]

# Function to execute the build process for all builder classes
def execute_builders():
    """
from apps.coa.builders.all import execute_builders
execute_builders()
    """
    for builder_class in builders:
        try:
            print(f'Building {builder_class.__name__}...')
            builder = builder_class()
            builder.build(build_local=True)
            print(f'Finished building {builder_class.__name__}')
        except Exception:
            print(traceback.format_exc())
            continue
