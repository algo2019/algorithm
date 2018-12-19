import ChangeStartCash
import GetAccountCash
import GetActiveOrder
import GetAllInit
import GetPosition
import InsertOrder
import StopStrategy


def register():
    modules = [GetAllInit, GetPosition, GetActiveOrder,
               InsertOrder, GetAccountCash, StopStrategy, ChangeStartCash]
    for m in modules:
        m.call()
