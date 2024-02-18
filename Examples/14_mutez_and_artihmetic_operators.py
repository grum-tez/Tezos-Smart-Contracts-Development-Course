import smartpy as sp

@sp.module
def main():

    class ComputingTez(sp.Contract):
        def __init__(self):
            self.data.financial_value = sp.mutez(1000000)
        
        @sp.entrypoint
        def add(self, x, y):
            self.data.financial_value = utils.nat_to_mutez(x) + utils.nat_to_mutez(y)
        
        
        @sp.entrypoint
        def sub(self, x, y):
            self.data.financial_value = utils.nat_to_mutez(x) - utils.nat_to_mutez(y)
       
        @sp.entrypoint
        def multiply(self, x, y):
            sp.cast(x, sp.mutez)
            sp.cast(y, sp.nat)
            self.data.financial_value = sp.mul(x, y)
            
        @sp.entrypoint
        def divide(self, x, y):
            sp.cast(x, sp.mutez)
            sp.cast(y, sp.nat)
            self.data.financial_value = sp.fst(sp.ediv(x, y).unwrap_some())


@sp.add_test()
def test():
    sc = sp.test_scenario("Test", [sp.utils,main])
    c1 = main.ComputingTez()
    sc += c1
    c1.add(x = 5, y = 3)
    c1.sub(x = 5, y = 3)
    c1.multiply(x =  sp.tez(5), y = sp.nat(3))
    c1.divide(x =  sp.tez(5), y = sp.nat(3))
