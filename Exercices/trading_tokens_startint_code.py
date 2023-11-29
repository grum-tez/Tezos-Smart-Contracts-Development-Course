import smartpy as sp

@sp.module
def main():
    param_type:type = sp.record(source = sp.address, destination = sp.address, amount = sp.nat)

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

    class LiquidityPool(sp.Contract):
        def __init__(self, owner, ledger):
            self.data.ledger = ledger
            self.data.owner = owner
            self.data.K = sp.tez(0)
            self.data.tokens_owned = sp.nat(0)
            # tokens_owned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, deposited_tokens):
            # TODO: Store deposited_tokens
            # TODO: Compute the value of K
            # TODO: Transfer deposited_tokens tokens to oneself, through the ledger
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            # TODO: Check that the owner is calling
            # TODO: Send all tez and tokens liquidity back to owner
        
        @sp.entrypoint
        def sell_tokens(self, nb_tokens_sold, min_tez_requested):
            # TODO: Compute how many tez these tokens are worth
            # TODO: Check that it is at least min_tez_requested
            # TODO: Transfer the tokens and tez accordingly

        @sp.entrypoint
        def buy_tokens(self, min_tokens_bought):
            # TODO: Compute how many tokens the amount sent buys
        	# TODO: If >= min_tokens_bought, transfer the tokens accordingly
            

        @sp.onchain_view
        def get_token_price(self):
            # TODO: Return what we would get if we sold one token


@sp.add_test()
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    carl = sp.test_account("carl")
    scenario = sp.test_scenario("Test" , main)
    ledger = main.Ledger(owner = alice.address, total_supply = 1000000)

    scenario += ledger

    
    liquidity_pool = main.LiquidityPool(owner = alice.address, ledger = ledger.address)
    scenario += liquidity_pool

    # TODO: alice deposits initial tez and tokens

    # TODO: bob buys some tokens
    
    # TODO: carl buys some tokens

    # TODO: bob sells his tokens and profits!
