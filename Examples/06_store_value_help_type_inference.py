import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self):
           self.data.stored_value = sp.nat(42)
    
       @sp.entrypoint
       def add(self, added_value):
          sp.cast(added_value, sp.nat)
          self.data.stored_value += added_value
    
       @sp.entrypoint
       def reset(self):
           self.data.stored_value = 0

@sp.add_test()
def test():
   scenario = sp.test_scenario("Test", main)
   contract = main.StoreValue()
   scenario += contract
   scenario.h3("Helping with type inference")
   contract.add(sp.nat(5))
