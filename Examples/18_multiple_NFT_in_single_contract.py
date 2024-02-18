import smartpy as sp

@sp.module
def main():

    class MultipleNftSingleContract(sp.Contract):
        def __init__(self, owner):
            self.data.next_id = 1
            self.data.owner = owner
            self.data.tokens = sp.big_map({})
            self.data.ledger = sp.big_map({})                     
       
        @sp.entry_point
        def buy(self, token_id):
            assert self.data.tokens.contains(token_id), "no such token"
            token = self.data.tokens[token_id]
            assert sp.amount == token.price, "wrong price"
            author_fee = sp.split_tokens(token.price, 5, 100)
            sp.send(self.data.owner, sp.amount - author_fee)
            if not self.data.ledger.contains(token.author):
                self.data.ledger[token.author] = sp.tez(0)
            self.data.ledger[token.author] += author_fee
            token.owner = sp.sender
            token.price += sp.split_tokens(token.price, 10, 100)
            self.data.tokens[token_id] = token
    
        @sp.entry_point
        def mint(self, metadata):
            sp.cast(metadata, sp.string)
            self.data.tokens[self.data.next_id] = sp.record(metadata = metadata,
                                                            price = sp.tez(1),
                                                            owner = sp.sender,
                                                            author = sp.sender)
            self.data.next_id += 1
    
        @sp.entry_point
        def claim(self):
            assert self.data.ledger.contains(sp.sender), "You are not owed any tez"
            sp.send(sp.sender, self.data.ledger[sp.sender])
            del self.data.ledger[sp.sender]
    
@sp.add_test()
def test():
    author = sp.test_account('author').address
    alice = sp.test_account('alice').address
    bob = sp.test_account('bob').address
    eve = sp.test_account('eve').address
    scenario = sp.test_scenario("Test", main)
    c1 = main.MultipleNftSingleContract(alice)
    scenario += c1
    c1.mint("First NFT", _sender = author)
    c1.buy(1, _sender = bob, _amount = sp.tez(1))
    c1.claim(_sender = author)
