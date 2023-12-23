import smartpy as sp

@sp.module
def main():

    class Auction(sp.Contract):
        def __init__(self):
            self.data.items = {}
            self.data.tokens = {}
            self.data.token_id = 1

        @sp.entrypoint
        def mint(self, metadata):
            self.data.tokens[self.data.token_id] = sp.record(metadata = metadata, owner = sp.sender)
            self.data.token_id += 1
        
        @sp.entrypoint
        def open_auction(self, item_id, deadline):
            self.data.items[item_id] = sp.record(seller = sp.sender,
                                                deadline = deadline,
                                                top_bid = sp.tez(0),
                                                top_bidder = sp.sender
                                               )
    
        @sp.entrypoint
        def bid(self, item_id):
            item = self.data.items[item_id]
            assert sp.amount > item.top_bid
            assert sp.now < item.deadline
            sp.send(item.top_bidder, item.top_bid) # Bug 4
            item.top_bid = sp.amount
            item.top_bidder = sp.sender
            self.data.items[item_id] = item

        @sp.entrypoint
        def claimtop_bid(self, item_id):
            item = self.data.items[item_id]
            assert sp.now >= item.deadline
            assert sp.sender == item.seller # Potential bug 6 if missing
            sp.send(item.seller, item.top_bid) # Bug 5
            self.data.tokens[item_id].owner = item.top_bidder # Bug 7

@sp.add_test()
def test():
    seller1 = sp.test_account("seller1").address
    seller2 = sp.test_account("seller2").address
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    scenario = sp.test_scenario("Test", main)
    auctionContract = main.Auction()
    scenario += auctionContract
    auctionContract.mint("Mon NFT").run(sender = seller1)
    auctionContract.open_auction(item_id = 1, seller = seller1, deadline = sp.timestamp(100))
    auctionContract.bid(1, _sender = alice, _amount = sp.tez(1), _now = sp.timestamp(1))
    auctionContract.bid(1, _sender = bob, _amount = sp.tez(2), _now = sp.timestamp(2))
    auctionContract.claimtop_bid(1, _sender = seller1, _now = sp.timestamp(101))

