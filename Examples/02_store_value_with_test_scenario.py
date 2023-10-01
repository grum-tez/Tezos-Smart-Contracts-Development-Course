import smartpy as sp

@sp.module
def main():
    class StoreValue(sp.Contract):
        def __init__(self):
            self.data.value = 342185

@sp.add_test()
def test():
    scenario = sp.test_scenario("test", main)
    contract = main.StoreValue()
    scenario += contract
