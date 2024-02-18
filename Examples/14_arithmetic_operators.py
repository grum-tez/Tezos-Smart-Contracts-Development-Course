import smartpy as sp

@sp.module
def main():

    class Calculator(sp.Contract):
        def __init__(self):
            self.data.int_value = sp.int(1)
            self.data.nat_value = sp.nat(0)
        
        @sp.entrypoint
        def add(self, x, y):
            self.data.int_value = x + y
            #if both operands not the same type use sp.to_int(nat_value) or sp.add(x,y)
        
        @sp.entrypoint
        def sub(self, x, y):
            sp.cast(x, sp.int)
            self.data.int_value = x - y
        
        @sp.entrypoint
        def multiply(self, x, y):
            self.data.int_value = x * y
            #if both operands not the same type use sp.to_int(nat_value) or sp.mul(x,y)
    
        @sp.entrypoint
        def negation(self, x):
            self.data.int_value = -x 
            
        @sp.entrypoint
        def divide(self, x, y):
            sp.cast(x, sp.nat)
            sp.cast(y, sp.nat)
            self.data.nat_value = x / y
            #if both operands not the same type use sp.to_int(nat_value) or sp.ediv(x,y)
    
        @sp.entrypoint
        def modulo(self, x, y):
            self.data.nat_value = sp.mod(x, y)
        
        @sp.entrypoint
        def shorthand(self, x):
            self.data.int_value += x
            #self.data.value -= x
            #self.data.value *= x



@sp.add_test()
def test():
    sc = sp.test_scenario("Test", main)
    c1 = main.Calculator()
    sc += c1
    c1.add(x = 5, y = 3)
    c1.sub(x = 5, y = 3)
    c1.multiply(x =  5, y = 3)
    c1.negation(3)
    c1.divide(x = 5, y = 3)
    c1.modulo(x = 8, y = 3)
    c1.shorthand(3)
