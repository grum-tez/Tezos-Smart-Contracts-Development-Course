import smartpy as sp

@sp.module
def main():

    class SingleBasicNFT(sp.Contract):
      def __init__(self, first_owner):
          self.data.owner = first_owner
          self.data.metadata = "My first NFT"
    
      @sp.entry_point
      def transfer(self, new_owner):
          assert sp.sender == self.data.owner, "not your property"
          self.data.owner = new_owner

@sp.add_test()
def test():
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address
    c1 = main.SingleBasicNFT(alice)
    scenario = sp.test_scenario("Test", main)
    scenario += c1
    scenario.h3("Testing transfer entrypoint")
    c1.transfer(bob, _sender = alice)
    scenario.verify(c1.data.owner == bob)
    scenario.verify(c1.data.metadata == "My first NFT")
    c1.transfer(eve, _sender = bob)
    scenario.verify(c1.data.owner == eve)
    c1.transfer(alice, _sender = eve)
    scenario.verify(c1.data.owner == alice)
