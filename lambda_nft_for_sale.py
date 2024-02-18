import smartpy as sp

@sp.module
def main():

    def newPrice(oldPrice):
        return oldPrice + sp.split_tokens(oldPrice, 10, 100) 

    def newPrice2(oldPrice):
        return oldPrice + sp.tez(1)
    
    class NftForSale(sp.Contract):
        def __init__(self, owner, metadata, price, author_rate, author):
            self.data.owner = owner
            self.data.metadata = metadata
            self.data.price = price
            self.data.author_rate = sp.nat(5)
            self.data.author = author
            self.data.priceUpdateRule = newPrice
               
        @sp.entrypoint
        def buy(self):
           assert sp.amount == self.data.price
           owner_share = sp.split_tokens(self.data.price, abs(100 - self.data.author_rate), 100)
           sp.send(self.data.owner, owner_share)
           self.data.price = self.data.priceUpdateRule(self.data.price)
           self.data.owner = sp.sender
    
        @sp.entrypoint
        def claim_author_rate(self):
            assert sp.sender == self.data.author, " not your money "
            sp.send(self.data.author, sp.balance)

        @sp.entrypoint
        def changeRule(self, newRule):
            assert sp.sender == self.data.author
            self.data.priceUpdateRule = newRule

@sp.add_test()
def test():
       alice = sp.test_account("alice").address
       bob = sp.test_account("bob").address
       eve = sp.test_account("eve").address
       author = sp.test_account("author").address
       scenario = sp.test_scenario("Test", main)
       c1 = main.NftForSale(owner = alice, metadata = "My nft", 
           price=sp.mutez(5000000), author=author, author_rate = sp.mutez(1000000))
       scenario +=c1
       scenario.verify(c1.data.price == sp.mutez(5000000) )
       scenario.h3(" Testing increasing price")
       c1.buy(_sender = bob, _amount = sp.mutez(5000000))
       scenario.verify(c1.data.price == sp.mutez(5500000) )
       scenario.verify(c1.balance == sp.mutez(250000) )
       c1.buy(_sender = eve, _amount = sp.mutez(5500000))
       c1.buy(_sender = alice, _amount = sp.mutez(6000000), _valid = False)
       scenario.verify(c1.data.price == sp.mutez(6050000))

       scenario.h3("Test contract upgrade")
       c1.changeRule(main.newPrice2, _sender = alice, _valid = False)
       c1.changeRule(main.newPrice2, _sender = author)
       c1.buy(_sender = eve, _amount = sp.mutez(6050000))
       scenario.verify(c1.data.price == sp.mutez(7050000))

       scenario.h3("Testing author fee claim")
       c1.claim_author_rate(_sender = alice, _valid = False)
       c1.claim_author_rate(_sender = author)
