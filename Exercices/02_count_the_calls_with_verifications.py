import smartpy as sp

@sp.module
def main():

    class CountTheCalls(sp.Contract):
       def __init__(self):
           self.data.nb_calls = 0
    
       @sp.entrypoint
       def make_call(self):
           self.data.nb_calls += 1

@sp.add_test()
def test():
   scenario = sp.test_scenario("Test", main)
   contract = main.CountTheCalls()
   scenario += contract
   scenario.verify(contract.data.nb_calls == 0)
   scenario.h2("Checking that calling make_call increments nb_calls")
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 1)
   contract.make_call()
   scenario.verify(contract.data.nb_calls == 2)
