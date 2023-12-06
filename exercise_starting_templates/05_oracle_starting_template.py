import smartpy as sp

@sp.module
def main():

    class BinaryBets(sp.Contract):
        def __init__(self, oracle_address, oracle_fee):
            self.data.bets = sp.big_map({})
            self.data.next_bet_id = sp.nat(1)
            self.data.oracle_address = oracle_address
            self.data.oracle_fee = oracle_fee
    
        @sp.entrypoint
        def create_bet(self, game_id, expected_result, deadline):
            sp.cast(game_id, sp.nat)
            sp.cast(deadline, sp.timestamp)
            bet_id = self.data.next_bet_id
            self.data.bets[bet_id] = sp.record(player1 = sp.sender,
                               player2 = sp.self_address(),
                               game_id = game_id,
                               amount = sp.amount,
                               expected_result = expected_result,
                               deadline = deadline,
                               cancelled = False)            
            self.data.next_bet_id += 1

        @sp.entrypoint
        def withdraw(self, bet_id):
            bet = self.data.bets[bet_id]
            amount = bet.amount
            if sp.sender == bet.player1:
                assert bet.cancelled or bet.player2 == sp.self_address(), "can't cancel"
                bet.player1 = sp.self_address()
            else:
                assert sp.sender == bet.player2, "not your bet"
                assert bet.cancelled, "not cancelled"
                bet.player2 = sp.self_address()
                amount += self.data.oracle_fee
            bet.cancelled = True
            self.data.bets[bet_id] = bet
            sp.send(sp.sender, amount)
        
        @sp.entrypoint
        def accept_bet(self, bet_id):
            bet = self.data.bets[bet_id]
            assert sp.amount == bet.amount + self.data.oracle_fee, "wrong amount"
            assert bet.player2 == sp.self_address(), "bet already accepted"
            assert not bet.cancelled, "bet is cancelled"
            bet.player2 = sp.sender
            self.data.bets[bet_id] = bet

            # TODO: create request on Oracle

        @sp.entrypoint
        def cancel_after_deadline(self, bet_id):
            bet = self.data.bets[bet_id]

            # TODO: check that Oracle didn't get the result, and get reimbursed
            
            bet.cancelled = True
            self.data.bets[bet_id] = bet

        @sp.entrypoint
        def claim_prize(self, bet_id):
            bet = self.data.bets[bet_id]
            assert not bet.cancelled


            # TODO: fetch result from oracle into result variable
            
            if sp.sender == bet.player1:
                assert bet.expected_result == result, "you lost"
            else:
                assert sp.sender == bet.player2, "not your bet"
                assert bet.expected_result != result, "you lost"
            sp.send(sp.sender, sp.split_tokens(bet.amount, 2, 1))
            del self.data.bets[bet_id]

        @sp.entrypoint
        def default(self):
            pass
            
    class BinaryGameOracle(sp.Contract):
        def __init__(self, admin, source_public_key):
            # TODO
    
@sp.add_test()
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    data_source = sp.test_account("Data_source")

    scenario = sp.test_scenario("Testing", main)
    oracle = main.BinaryGameOracle(alice.address, data_source.public_key)
    scenario += oracle
    better = main.BinaryBets(oracle.address, sp.tez(2))
    scenario += better

    # Everything goes as planned and the Oracle sends the result where alice wins
    better.create_bet(game_id = sp.nat(1), expected_result = True, deadline = sp.timestamp(1000), _sender = alice, _amount = sp.tez(5))
    # Bob tries to pay the wrong amount
    better.accept_bet(1, _sender = bob, _amount = sp.tez(5), _valid = False, _exception = "wrong amount")
    better.accept_bet(1, _sender = bob, _amount = sp.tez(7))
    # Try to claim prize before the result is available
    better.claim_prize(sp.nat(1), _sender = alice, _valid = False)

    # TODO: send True result to the Oracle
    
    # Bob tries to falsely claim the prize
    better.claim_prize(sp.nat(1), _sender = bob, _valid = False)
    better.claim_prize(sp.nat(1), _sender = alice)

    # Cancel after deadline if Oracle didn't obtain the data
    better.create_bet(game_id = sp.nat(2), expected_result = True, deadline = sp.timestamp(1000), _sender = alice, _amount = sp.tez(5))
    better.accept_bet(2, _sender = bob, _amount = sp.tez(7))
    # alice tries to withdraw after bob accepts
    better.withdraw(2, _sender = alice, _valid = False, _exception = "can't cancel")
    # bob tries to withdraw after bob accepts
    better.withdraw(2, _sender = bob, _valid = False, _exception = "not cancelled")
    better.cancel_after_deadline(2, _now = sp.timestamp(1000), _valid = False, _exception = "deadline not passed")
    better.cancel_after_deadline(2, _now = sp.timestamp(1001))
    # eve tries to withdraw
    better.withdraw(2, _sender = eve, _valid = False, _exception = "not your bet")
    better.withdraw(2, _sender = bob)
    better.withdraw(2, _sender = alice)

    # Everything goes as planned and the Oracle sends the result where Bob wins
    better.create_bet(game_id = sp.nat(3), expected_result = True, deadline = sp.timestamp(2000), _sender = alice, _amount = sp.tez(5))
    better.accept_bet(3, _sender = bob, _amount = sp.tez(7))

    # TODO: send False result to the Oracle
    
    # Alice tries to falsely claim the prize
    better.claim_prize(sp.nat(3), _sender = alice, _valid = False)
    better.claim_prize(sp.nat(3), _sender = bob)

