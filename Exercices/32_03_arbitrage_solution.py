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
            self.data.ledger_contract_opt = None
            # tokens_owned * sp.balance = K -> should always be true

        @sp.entrypoint
        def provide_liquidity(self, deposited_tokens):
            assert sp.sender == self.data.owner
            assert self.data.K == sp.tez(0)
            self.data.K = sp.mul(sp.balance, deposited_tokens)

            self.data.tokens_owned = deposited_tokens

            self.data.ledger_contract_opt = sp.contract(param_type, self.data.ledger, entrypoint="transfer")
            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = deposited_tokens),
                        sp.tez(0),
                        self.data.ledger_contract_opt.unwrap_some()
                       )
            
        @sp.entrypoint
        def withdraw_liquidity(self):
            assert sp.sender == self.data.owner
            sp.send(sp.sender, sp.balance)
            
            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = self.data.tokens_owned), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned = sp.nat(0)
            self.data.K = sp.tez(0)

        
        @sp.entrypoint
        def sell_tokens(self, nb_tokens_sold, min_tez_requested):
            ratio = sp.ediv(self.data.K, self.data.tokens_owned + nb_tokens_sold).unwrap_some()
            tez_obtained = sp.balance - sp.fst(ratio)
            assert tez_obtained >= min_tez_requested

            sp.transfer(sp.record(source = sp.sender, destination = sp.self_address(), amount = nb_tokens_sold), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned += nb_tokens_sold
            sp.send(sp.sender, tez_obtained)

        @sp.entrypoint
        def buy_tokens(self, min_tokens_bought):
            trace("Test")
            sp.cast(min_tokens_bought, sp.nat)
            tokens_obtained = sp.as_nat(self.data.tokens_owned - sp.fst(sp.ediv(self.data.K, sp.balance).unwrap_some()))
            assert tokens_obtained >= min_tokens_bought

            sp.transfer(sp.record(source = sp.self_address(), destination = sp.sender, amount = tokens_obtained), sp.tez(0), self.data.ledger_contract_opt.unwrap_some())

            self.data.tokens_owned = sp.as_nat(self.data.tokens_owned - tokens_obtained)
            

        @sp.onchain_view
        def get_token_price(self):
            # returns what we would get if we sold one token
            ratio1 = sp.ediv(self.data.K, self.data.tokens_owned).unwrap_some()
            ratio2 = sp.ediv(self.data.K, sp.as_nat(self.data.tokens_owned - 1)).unwrap_some()
            sp.trace ("The current value of K is:")
            sp.trace(self.data.K)
            sp.trace("The pool owns this amount of tokens:")
            sp.trace(self.data.tokens_owned)
            sp.trace("The balance of the pool is:")
            sp.trace(sp.balance)
            sp.trace("The ratios before and after a potential purchase of 1 token would be:")
            sp.trace(ratio1)
            sp.trace(ratio2)
            token_price = sp.fst(ratio2) - sp.fst(ratio1)
            sp.trace("The price of the token returned is:")
            sp.trace(token_price)
            return token_price

@sp.add_test()
def test():
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    carl = sp.test_account("carl")
    scenario = sp.test_scenario("Test" , main)
    ledger = main.Ledger(owner = alice.address, total_supply = 10000000)

    scenario += ledger
    
    lp1 = main.LiquidityPool(owner = alice.address, ledger = ledger.address)
    scenario += lp1
    ledger.allow(sp.record(operator = lp1.address, amount = 1000000), _sender = alice)
    lp1.provide_liquidity(1000000, _sender = alice, _amount = sp.tez(1000))

    lp2 = main.LiquidityPool(owner = alice.address, ledger = ledger.address)
    scenario += lp2
    ledger.allow(sp.record(operator = lp2.address, amount = 1000000), _sender = alice)
    lp2.provide_liquidity(1000000, _sender = alice, _amount = sp.tez(1000))

    lp1.buy_tokens(80000, _sender = bob, _amount = sp.tez(100))

    scenario.verify(lp1.get_token_price() > sp.mutez(900))
    scenario.verify(lp2.get_token_price() > sp.mutez(900))
    
    #min_nb_tokens = 46712
    #tez_spent = sp.tez(49)  # => 4.758206 profit

    min_nb_tokens = 45802
    tez_spent = sp.tez(48)  # => 4.76115 profit

    #min_nb_tokens = 44891
    #tez_spent = sp.tez(47)  # => 4.76109 profit
  
    lp2.buy_tokens(min_nb_tokens, _sender = carl, _amount = tez_spent)
    ledger.allow(sp.record(operator = lp1.address, amount = min_nb_tokens), _sender = carl)
    lp1.sell_tokens(nb_tokens_sold = min_nb_tokens, min_tez_requested = sp.tez(0), _sender = carl)

    scenario.verify(lp1.get_token_price() > sp.mutez(90))
    scenario.verify(lp2.get_token_price() > sp.mutez(90))
    
