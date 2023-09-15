import smartpy as sp

@sp.module
def main():

    class Auction(sp.Contract):
        def __init__(self, admin):
            self.data.items = sp.big_map({})
            self.data.tokens = sp.big_map({})
            self.data.token_id = 1
            self.data.admin = admin
            self.data.tez_to_claim = sp.big_map({})


        @sp.entrypoint
        def claim_tez(self):
            sp.send(sp.sender, self.data.tez_to_claim[sp.sender])
            del self.data.tez_to_claim[sp.sender]



        @sp.entrypoint
        def mint(self, metadata):
            assert sp.amount == sp.tez(1)
            if not self.data.tez_to_claim.contains(self.data.admin):
                self.data.tez_to_claim[self.data.admin] = sp.tez(0)
            self.data.tez_to_claim[self.data.admin] += sp.amount
            self.data.tokens[self.data.token_id] = sp.record(metadata = metadata, owner = sp.sender)
            self.data.token_id += 1
        
        @sp.entrypoint
        def openAuction(self, item_id, deadline):
            assert sp.sender == self.data.tokens[item_id].owner
            assert not self.data.items.contains(item_id)
            self.data.items[item_id] = sp.record( deadline = deadline,
                                                topBid = sp.tez(0),
                                                topBidder = sp.sender
                                               )
    
        @sp.entrypoint
        def bid(self, item_id):
            item = self.data.items[item_id]
            assert sp.amount > item.topBid
            assert sp.now < item.deadline
            if not self.data.tez_to_claim.contains(item.topBidder):
                self.data.tez_to_claim[item.topBidder] = sp.tez(0)
            self.data.tez_to_claim[item.topBidder] += item.topBid
            item.topBid = sp.amount
            item.topBidder = sp.sender
            self.data.items[item_id] = item

        @sp.entrypoint
        def claim_top_bid(self, item_id):
            item = self.data.items[item_id]
            token = self.data.tokens[item_id]
            assert sp.now >= item.deadline
            assert sp.sender == token.owner or sp.sender == item.topBidder
            del self.data.items[item_id]
            sp.send(token.owner, item.topBid)
            self.data.tokens[item_id].owner = item.topBidder

@sp.add_test(name="Testing extortion attack")
def test():
    seller1 = sp.test_account("seller1").address
    seller2 = sp.test_account("seller2").address
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    scenario = sp.test_scenario(main)
    auctionContract = main.Auction(alice)
    scenario += auctionContract
    auctionContract.mint("Mon NFT").run(sender = seller1, amount = sp.tez(1))
    auctionContract.openAuction(item_id = 1, deadline = sp.timestamp(100)).run(sender=seller1)
    auctionContract.bid(1).run(sender = alice, amount = sp.tez(1), now = sp.timestamp(1))
    auctionContract.bid(1).run(sender = bob, amount = sp.tez(2), now = sp.timestamp(2))
    auctionContract.claim_top_bid(1).run(sender = seller1, now = sp.timestamp(101))
