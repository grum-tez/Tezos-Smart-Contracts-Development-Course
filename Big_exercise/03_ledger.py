import smartpy as sp

@sp.module
def main():

    class Ledger(sp.Contract):
        def __init__(self, owner, total_supply):
            self.data.balances = sp.big_map({ owner : total_supply })
            self.data.allowances = sp.big_map({})
          
        @sp.entrypoint
        def transfer(self, source, destination, amount):
            if source != sp.sender:
                allowed = self.data.allowances[(source, sp.sender)]
                assert allowed >= amount
                self.data.allowances[(source, sp.sender)] = sp.as_nat(allowed - amount)
            assert self.data.balances[source] >= amount
            self.data.balances[source] = sp.as_nat(self.data.balances[source] - amount)
            if not self.data.balances.contains(destination):
                self.data.balances[destination] = sp.nat(0)
            self.data.balances[destination] += amount

        @sp.onchain_view
        def get_balance(self, user):
            sp.cast(user, sp.address)
            return self.data.balances[user]

        @sp.entrypoint
        def allow(self, operator, amount):
            if not self.data.allowances.contains((sp.sender, operator)):
                self.data.allowances[(sp.sender, operator)] = 0
            self.data.allowances[(sp.sender, operator)] += amount

    class EndlessWall(sp.Contract):
        def __init__(self, initial_text, owner, ledger):
            self.data.wall_text = initial_text
            self.data.owner = owner
            self.data.ledger = ledger
    
        @sp.entrypoint
        def write_message(self, message):
            ledger_transfer = sp.contract(sp.record(source = sp.address, destination = sp.address, amount = sp.nat),
                                          self.data.ledger,
                                          entrypoint = "transfer"
                                         ).unwrap_some()
            sp.transfer(sp.record(source = sp.sender, destination = self.data.owner, amount = 1),
                                  sp.tez(0),
                                  ledger_transfer
                                 )
            self.data.wall_text += ", " + message + " forever"

@sp.add_test()
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")

    scenario = sp.test_scenario("Test", main)
    ledger = main.Ledger(alice.address, 1000000)
    scenario += ledger

    wall = main.EndlessWall("Hello", bob.address, ledger.address)
    scenario += wall

    ledger.allow(operator = wall.address, amount = 1, _sender = alice)
    wall.write_message("Alice", _sender = alice)
    
    

