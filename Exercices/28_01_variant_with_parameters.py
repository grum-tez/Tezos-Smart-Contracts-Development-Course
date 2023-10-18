import smartpy as sp


@sp.module
def main():


    food_type:type = sp.variant(
        Hamburger = sp.record(sauce_type = sp.string, 
                              sauce_quantity = sp.nat, 
                              side = sp.variant(Fries = sp.unit, Potatoes = sp.unit)
                             ),
        Icecream = sp.record(flavour = sp.string, extra_topping = sp.bool),
        Drink = sp.string,
        Brownie = sp.unit
    )


    class OrderMenu(sp.Contract):
        def __init__(self):
            self.data.items = []
            self.data.food_order = None

        @sp.entrypoint
        def place_food_order(self, food):
            sp.cast(food, food_type)
            price = sp.tez(0)
            with sp.match(food):
                with sp.case.Hamburger as composition:
                    price = sp.tez(8)
                    hamburger_side = composition.side
                    if hamburger_side.is_variant.Fries():
                        price += sp.tez(0)
                    if hamburger_side.is_variant.Potatoes():
                        price += sp.tez(1)
                    #with sp.match(hamburger_side):
                    #    with sp.case.Fries:
                    #        price = sp.tez(5)
                    #    with sp.case.Potatoes:
                    #        price = sp.tez(5)
                    #if hamburger_side == sp.variant.Fries():
                    #    price += sp.tez(0)
                    #if hamburger_side == sp.variant.Potatoes():
                    #    price += sp.tez(0)
                        
                with sp.case.Icecream as composition:
                    price = sp.tez(4)
                    if composition.extra_topping:
                        price += sp.tez(2) 
                with sp.case.Drink:
                    price = sp.tez(3)
                with sp.case.Brownie:
                    price = sp.tez(5)
            assert sp.amount == price
            self.data.items.push(food)
            


        @sp.onchain_view
        def get_food_order(self):
            return self.data.food_order


@sp.add_test(name = "OrderMenu")
def test():
    scenario = sp.test_scenario(main)
    cMenu = main.OrderMenu()
    scenario += cMenu
        
    scenario.h3("Hamburger with Fries")
    cMenu.place_food_order(sp.variant("Hamburger", sp.record(
        sauce_type = "Mayonnaise", 
        sauce_quantity = 2,
        side = sp.variant("Fries", ())
    ))).run(sender=sp.address("tz1TestAddress"), amount=sp.tez(8))
        
    scenario += cMenu
    scenario.h3("Vanilla ice cream with extra toppings")
    cMenu.place_food_order(sp.variant("Icecream", sp.record(
        flavour = "Vanilla", 
        extra_topping = True
    ))).run(sender=sp.address("tz1TestAddress"), amount=sp.tez(6))
        
    scenario += cMenu
    scenario.h3("Buy a coca")
    cMenu.place_food_order(sp.variant("Drink", "Coca")).run(sender=sp.address("tz1TestAddress"), amount=sp.tez(3))

    scenario += cMenu
    scenario.h3("Brownie")
    cMenu.place_food_order(sp.variant("Brownie", ())).run(sender=sp.address("tz1TestAddress"), amount=sp.tez(5))
