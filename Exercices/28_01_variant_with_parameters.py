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


@sp.add_test()
def test():
    scenario = sp.test_scenario("Test", main)
    cMenu = main.OrderMenu()
    scenario += cMenu
        
    scenario.h3("Hamburger with Fries")
    cMenu.place_food_order(sp.variant("Hamburger", sp.record(
        sauce_type = "Mayonnaise", 
        sauce_quantity = 2,
        side = sp.variant("Fries", ())
    )), _sender=sp.address("tz1TestAddress"), _amount = sp.tez(8))
        
    cMenu2 = main.OrderMenu()
    scenario += cMenu2
    scenario.h3("Vanilla ice cream with extra toppings")
    cMenu2.place_food_order(sp.variant("Icecream", sp.record(
        flavour = "Vanilla", 
        extra_topping = True
    )), _sender=sp.address("tz1TestAddress"), _amount=sp.tez(6))
        
    cMenu3 = main.OrderMenu()
    scenario += cMenu3
    scenario.h3("Buy a coca")
    cMenu3.place_food_order(sp.variant("Drink", "Coca"), _sender = sp.address("tz1TestAddress"), _amount = sp.tez(3))

    cMenu4 = main.OrderMenu()
    scenario += cMenu4
    scenario.h3("Brownie")
    cMenu4.place_food_order(sp.variant("Brownie", ()), _sender = sp.address("tz1TestAddress"), _amount=sp.tez(5))
