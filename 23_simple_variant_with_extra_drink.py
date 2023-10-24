import smartpy as sp


@sp.module
def main():
    
    drink_type:type = sp.variant(Coca = sp.unit, Fanta = sp.unit, SevenUp = sp.unit, Water = sp.unit)
    drink_type_new:type = sp.variant(Coca = sp.unit, Fanta = sp.unit, SevenUp = sp.unit, Water = sp.unit, Sprite = sp.unit)

    class FavoriteDrinks(sp.Contract):
        def __init__(self):
            self.data.favoriteDrinks = sp.big_map({})

        @sp.entrypoint
        def setFavorite(self, drink):
            sp.cast(drink, drink_type)
            self.data.favoriteDrinks[sp.sender] = drink

        @sp.onchain_view
        def favorite(self, user):
            return self.data.favoriteDrinks[user]
    
    class Restaurant(sp.Contract):
        def __init__(self, favoriteDrinksContract):
            self.data.items = []
            self.data.favoriteDrinksContract = favoriteDrinksContract

        @sp.entrypoint
        def quickDrink(self):
            drink = sp.view("favorite", self.data.favoriteDrinksContract, sp.sender, drink_type).unwrap_some()
            self.data.items.push(drink)            
        
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
            
    class RestaurantNew(sp.Contract):
        def __init__(self, favoriteDrinksContract):
            self.data.items = []
            self.data.favoriteDrinksContract = favoriteDrinksContract

        @sp.entrypoint
        def quickDrink(self):
            drink = sp.view("favorite", self.data.favoriteDrinksContract, sp.sender, drink_type).unwrap_some()
            self.data.items.push(drink)            
        
        @sp.entrypoint
        def orderDrink(self, drink):
            sp.cast(drink, drink_type_new)
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
    alice = sp.test_account("Alice")
    scenario = sp.test_scenario(main)
    cFavorites = main.FavoriteDrinks()
    scenario += cFavorites
    cFavorites.setFavorite(sp.variant("Coca", ())).run(sender = alice)   
    c1 = main.Restaurant(cFavorites.address)
    scenario += c1
    scenario.h3("J'ai faim")
    c1.orderDrink(sp.variant("Water", ()))
    c1.orderDrink(sp.variant("Coca", ())).run(valid = False)
    c1.orderDrink(sp.variant("Coca", ())).run(amount = sp.tez(1), valid = True)    
    c1.orderDrink(sp.variant("Fanta", ())).run(valid = False)
    c1.orderDrink(sp.variant("Fanta", ())).run(amount = sp.tez(2), valid = True)
    c1.quickDrink().run(sender = alice)
    
    c1 = main.RestaurantNew(cFavorites.address)

   