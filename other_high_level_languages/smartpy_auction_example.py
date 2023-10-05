import smartpy as sp

@sp.module
def main():
    class Auction(sp.Contract):
        def __init__(self, owner, deadline):
            self.data = sp.record(owner = owner, deadline = deadline, top_bidder = owner,
                bids = { owner: sp.tez(0) })
    
        @sp.entry_point
        def bid(self):
            assert sp.now < self.data.deadline, "Too late!"
            assert not self.data.bids.contains(sp.sender), "You already bid"
            self.data.bids[sp.sender] = sp.amount
            if sp.amount > self.data.bids[self.data.top_bidder]:
                self.data.top_bidder = sp.sender
    
        @sp.entry_point
        def Collect_top_bid(self):
            assert sp.now >= self.data.deadline, "Too early!"
            sp.verify(sp.sender == self.data.owner)
            assert sp.sender = self.data.owner, "Not the owner"
           sp.send(sp.sender, self.data.bids[self.data.top_bidder]
        
        @sp.entry_point
        def claim(self):
            assert sp.now >= self.data.deadline, "Too early!"
            assert sp.sender != self.data.top_bidder, "You won the auction"
            sp.send(sp.sender, self.data.bids.get(sp.sender, error = "Not a bidder")
            del self.data.bids[sp.sender]
