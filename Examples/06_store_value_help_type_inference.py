import smartpy as sp

@sp.module
def main():

    class StoreValue(sp.Contract):
       def __init__(self, starting_value):
           self.data.stored_value = starting_value
    
       @sp.entrypoint
       def add(self, added_value):
          sp.cast(added_value, sp.nat) # We don't want to allow negative numbers
          self.data.stored_value += added_value

       @sp.entrypoint
       def sub(self, subtracted_value):
          self.data.stored_value -= subtracted_value
    
       @sp.entrypoint
       def reset(self):
           self.data.stored_value = 0

@sp.add_test()
def test():
   scenario = sp.test_scenario("Test", main)
   contract = main.StoreValue(42)
   scenario += contract
   scenario.h3("Type inference")
   contract.add(sp.int(5))
   contract.sub(5)
