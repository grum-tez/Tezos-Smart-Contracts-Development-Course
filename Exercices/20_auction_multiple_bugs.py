import smartpy as sp

@sp.module
def main():

    class Auction(sp.Contract):
        def __init__(self):
            self.data.tokens = {}
            self.data.token_id = 1
            self.data.auctions = {}

        @sp.entrypoint
        def mint(self, metadata):
            sp.cast(metadata, sp.string)
            assert sp.amount == sp.tez(1)
            self.data.tokens[self.data.token_id] = sp.record(metadata = metadata, owner = sp.sender)
            self.data.token_id += 1
        
        @sp.entrypoint
        def open_auction(self, token_id, deadline):
            sp.cast(deadline, sp.timestamp)
            self.data.auctions[token_id] = sp.record(seller = sp.sender,
                                                deadline = deadline,
                                                top_bid = sp.tez(0),
                                                top_bidder = sp.sender
                                               )
    
        @sp.entrypoint
        def bid(self, token_id):
            auction = self.data.auctions[token_id]
            assert sp.amount > auction.top_bid
            assert sp.now < auction.deadline
            sp.send(auction.top_bidder, auction.top_bid)
            auction.top_bid = sp.amount
            auction.top_bidder = sp.sender
            self.data.auctions[token_id] = auction

        @sp.entrypoint
        def claimtop_bid(self, token_id):
            auction = self.data.auctions[token_id]
            assert sp.now >= auction.deadline
            assert sp.sender == auction.seller
            sp.send(auction.seller, auction.top_bid)
            self.data.tokens[token_id].owner = auction.top_bidder

@sp.add_test()
def test():
    seller1 = sp.test_account("seller1").address
    seller2 = sp.test_account("seller2").address
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    scenario = sp.test_scenario("Test", main)
    auctionContract = main.Auction()
    scenario += auctionContract
    auctionContract.mint("Mon NFT", _sender = seller1, _amount = sp.tez(1))
    auctionContract.open_auction(token_id = 1, deadline = sp.timestamp(100), _sender = seller1)
    auctionContract.bid(1, _sender = alice, _amount = sp.tez(1), _now = sp.timestamp(1))
    auctionContract.bid(1, _sender = bob, _amount = sp.tez(2), _now = sp.timestamp(2))
    auctionContract.claimtop_bid(1, _sender = seller1, _now = sp.timestamp(101))

