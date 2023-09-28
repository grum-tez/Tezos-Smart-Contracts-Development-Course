import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
        def __init__(self, initial_text):
            self.data.wall_text = initial_text
            self.data.nb_calls = 0
        
        @sp.entry_point
        def write_message(self, message):
            assert (sp.len(message) <= 30) and (sp.len(message) >= 3), "invalid length"
            self.data.wall_text += ", " + message + " forever"
            self.data.nb_calls += 1
  
@sp.add_test()
def test():
   c1 = main.EndlessWall(initial_text = "Hello")
   scenario = sp.test_scenario("Test", main)
   scenario += c1
   scenario.h3(" Testing write_message")
   c1.write_message("Ana & Jack")
   c1.write_message("Tezos")
   scenario.verify(c1.data.wall_text == "Hello, Ana & Jack forever, Tezos forever")
   scenario.verify(c1.data.nb_calls == 2)
   scenario.h3(" Testing write_message size message on limits")
   c1.write_message("this message is 31 letters long", _valid = False)
   c1.write_message("AB", _valid = False)
   #by default a transaction is valid, no need to add _valid = True after testing a call that should be a valid transaction
   c1.write_message("LLL")
   c1.write_message("this message is 30 characters ")
   scenario.verify(c1.data.nb_calls == 4)
