from ..repository import StockRepository


def datastore(write=False):
    """
    Returns a hangar dataset object (checkout object). The rationale here
    is to keep the datastore APIs similar to what hangar already has

    :param write: bool, write enabled checkout or not
    """
    repo = StockRepository()
    co = repo.checkout(write=write)
    return co.arraysets




