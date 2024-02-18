import smartpy as sp

@sp.module
def main():
    @sp.effects(with_operations=True)
    def transfer_proposal():
        sp.send(sp.address("tz142114b421"), sp.tez(100))

    class Multisig(sp.Contract):
       def __init__(self, participants, required_votes):
           sp.cast(participants, sp.map[sp.address, sp.bool])
           self.data.participants = participants
           self.data.proposals = sp.big_map({})
           self.data.required_votes = required_votes
           self.data.next_id = 0

       @sp.entrypoint
       def propose(self, code, deadline):
           sp.cast(code, sp.lambda_(sp.unit, sp.unit, with_operations=True))
           sp.cast(deadline, sp.timestamp)
           assert self.data.participants.contains(sp.sender)
           self.data.proposals[self.data.next_id] =  sp.record(
               code = code,
               deadline = deadline,
               nb_approved = 0,
               has_voted = {}
           )
           self.data.next_id += 1
           
       @sp.entrypoint
       def vote(self, proposal_id):
           proposal = self.data.proposals[proposal_id]
           assert sp.now < proposal.deadline
           assert self.data.participants.contains(sp.sender)
           assert not proposal.has_voted.contains(sp.sender)
           proposal.has_voted[sp.sender] = True
           proposal.nb_approved += 1
           self.data.proposals[proposal_id] = proposal
           if proposal.nb_approved == self.data.required_votes:
               proposal.code()

@sp.add_test()
def test():
    alice=sp.test_account("Alice")
    bob=sp.test_account("Bob")
    eve=sp.test_account("Eve")
    sc = sp.test_scenario("Test", main)
    multi_sig = main.Multisig(participants = {
        alice.address: True,
        bob.address: True
    }, required_votes = 2)
    sc += multi_sig
    multi_sig.propose(code = main.transfer_proposal, deadline = sp.timestamp(100), _sender = alice, _amount = sp.tez(200))
    multi_sig.vote(0, _sender = alice)
    multi_sig.vote(0, _sender = bob)
    
    
