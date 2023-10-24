import smartpy as sp


@sp.module
def main():
    
    drink_type:type = sp.variant(Coca = sp.unit, Fanta = sp.unit, SevenUp = sp.unit, Water = sp.unit)
    
    class Restaurant(sp.Contract):
        def __init__(self):
            self.data.items = []            

        @sp.entrypoint
        def orderDrink(self, drink):
            sp.cast(drink, drink_type)
            price = sp.tez(0)
            with sp.match(drink):
                with sp.case.Coca:
                    price = sp.tez(1)
                with sp.case.Fanta:
                    price = sp.tez(2)
                with sp.case.Water:
                    price = sp.tez(0)
                # etc.
            assert sp.amount == price
            self.data.items.push(drink)
            

@sp.add_test(name = "Restaurant Time")
def test():
    c1 = main.Restaurant()
    scenario = sp.test_scenario(main)
    scenario += c1
    scenario.h3("J'ai faim")
    c1.orderDrink(sp.variant("Water", ()))
    c1.orderDrink(sp.variant("Coca", ())).run(valid = False)
    c1.orderDrink(sp.variant("Coca", ())).run(amount = sp.tez(1), valid = True)    
    c1.orderDrink(sp.variant("Fanta", ())).run(valid = False)
    c1.orderDrink(sp.variant("Fanta", ())).run(amount = sp.tez(2), valid = True)
