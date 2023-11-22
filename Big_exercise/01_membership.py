import smartpy as sp

@sp.module
def main():
    class Membership(sp.Contract):
        def __init__(self, membership_threshold):
            self.data.membership_threshold = membership_threshold
            self.data.members = sp.set()

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.membership_threshold
            assert len(self.data.members) < 100
            self.data.members.add(sp.sender)
            sp.send(sp.sender, sp.amount)

        @sp.onchain_view
        def is_member(self, user):
            sp.cast(user, sp.address)
            return self.data.members.contains(user)

        @sp.entrypoint
        def leave(self):
            self.data.members.remove(sp.sender)
        

@sp.add_test()
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    carl = sp.test_account("Carl")
    
    scenario = sp.test_scenario("Test", main)

    # Init NftMarketplace
    rich_community = main.Membership(sp.tez(1000))

    scenario += rich_community

    rich_community.join(_sender = alice, _amount = sp.tez(1000))
    rich_community.join(_sender = bob, _amount = sp.tez(9999), _valid = False)
    rich_community.join(_sender = bob, _amount = sp.tez(1000), _valid = True)
    scenario.verify(rich_community.is_member(alice.address))
    scenario.verify(~rich_community.is_member(carl.address))
    rich_community.leave(_sender = bob)
    scenario.verify(~rich_community.is_member(bob.address))
    
