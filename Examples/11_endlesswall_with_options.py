import smartpy as sp

@sp.module
def main():

    class EndlessWall(sp.Contract):
       def __init__(self, initial_text, owner):
           self.data.wall_text = initial_text
           self.data.nb_calls = 0
           self.data.last_sender = None
    
       @sp.entrypoint
       def write_message(self, message):
           assert (sp.len(message) <= 30) and (sp.len(message) >= 3), "invalid message size"
           assert self.data.last_sender != sp.Some(sp.sender), "Do not spam the wall"
           self.data.wall_text += ", " + message + " forever"
           self.data.nb_calls += 1
           self.data.last_sender = sp.Some(sp.sender)  
  
@sp.add_test()
def test():
   alice=sp.test_account("Alice").address
   bob=sp.test_account("Bob").address
   eve=sp.test_account("Eve").address
   scenario = sp.test_scenario("Test", main)
   c1 = main.EndlessWall(initial_text = "Axel on Tezos forever", owner = alice)
   scenario += c1
   c1.write_message("Ana & Jack", _sender = eve)
   c1.write_message("freeCodeCamp", _sender = bob)
   scenario.verify(c1.data.wall_text == "Axel on Tezos forever, Ana & Jack forever, freeCodeCamp forever")
   c1.write_message("freeCodeCamp", _sender = bob, _valid = False, _exception = "Do not spam the wall")
   c1.write_message("this message is 31 letters long", _sender = alice, _valid = False)
   #by default a transaction is valid, no need to add .run(valid = True) after testing a valid call
   c1.write_message("LLL", _sender = alice)
   c1.write_message("this message is 30 characters ", _sender = eve)
   scenario.verify(c1.data.nb_calls == 4)
    
