import smartpy as sp


@sp.module
def main():
    
    status_type:type = sp.variant(
        Available = sp.unit,
        Absent = sp.unit,
        Away = sp.timestamp,
        Call = sp.string,
        Meeting = sp.record(floor = sp.nat, room = sp.string)
    )

    event_type:type = sp.variant(
        Call = sp.string,
        Meeting = sp.record(floor = sp.nat, room = sp.string)
    )

    class EmployeeStatus(sp.Contract):
        def __init__(self, owner, boss):
            self.data.status = sp.variant.Available()
            self.data.owner = owner
            self.data.boss = boss

        @sp.entrypoint
        def setStatus(self, status):
            sp.cast(status, status_type)
            assert sp.sender == self.data.owner
            self.data.status = status

        @sp.entrypoint
        def invite(self, event):
            sp.cast(event, event_type)
            assert sp.sender == self.data.boss
            canInterrupt = True
            with sp.match(self.data.status):
                with sp.case.Available:
                    pass
                with sp.case.Absent:
                    canInterrupt = False
                with sp.case.Call:
                    canInterrupt = False
                with sp.case.Meeting:
                    canInterrupt = False
                with sp.case.Away as deadline:
                    canInterrupt = sp.now >= deadline
            assert canInterrupt
            with sp.match(event):
                with sp.case.Call as url:
                    self.data.status = sp.variant.Call(url)
                with sp.case.Meeting as meetingInfo:
                    self.data.status = sp.variant.Meeting(meetingInfo)
                    
        
        @sp.onchain_view
        def status(self):
            return self.data.status
    
@sp.add_test()
def test():
    alice = sp.test_account("Alice")
    bob = sp.test_account("Bob")
    eve = sp.test_account("Eve")
    scenario = sp.test_scenario("Test", main)
    cStatus = main.EmployeeStatus(alice.address, bob.address)
    scenario += cStatus
    cStatus.setStatus(sp.variant("Away", sp.timestamp(1000)), _sender = alice) 
    cStatus.invite(sp.variant("Call", "https://call.com/12345"), _sender = bob, _valid = False)
    cStatus.invite(sp.variant("Call", "https://call.com/12345"), _sender = bob, _now = sp.timestamp(1100), _valid = True)
