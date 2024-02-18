import smartpy as sp

@sp.module
def main():

    class MultipleNftSingleContract(sp.Contract):
        def __init__(self, owner):
            self.data.owner = owner
            self.data.next_id = 1
            self.data.tokens = sp.big_map({})
    
        @sp.entrypoint
        def buy(self, token_id):
            assert self.data.tokens.contains(token_id)
            token = self.data.tokens[token_id]
            assert sp.amount == token.price
            author_fee = sp.split_tokens(token.price, 5, 100)
            sp.send(self.data.owner, sp.amount - author_fee)
            sp.send(token.author, author_fee)
            token.owner = sp.sender
            token.price += sp.split_tokens(token.price, 10, 100)
            self.data.tokens[token_id] = token
    
        @sp.entrypoint
        def mint(self, metadata):
            sp.cast(metadata, sp.string)
            self.data.tokens[self.data.next_id] = sp.record(metadata = metadata,
                                                            price = sp.tez(1),
                                                            owner = sp.sender,
                                                            author = sp.sender)
            self.data.next_id += 1

@sp.add_test()
def test():
    author = sp.test_account("author").address
    alice = sp.test_account("alice").address
    bob = sp.test_account("bob").address
    eve = sp.test_account("eve").address
    scenario = sp.test_scenario("Test", main)
    c1 = main.MultipleNftSingleContract(author)
    scenario += c1
    c1.mint("second contract", _sender = alice)
    c1.buy(1, _sender = bob, _amount = sp.tez(1))
    scenario.verify(c1.balance == sp.tez(0))

