import smartpy as sp

@sp.module
def main():
    class TrulyEndlessWall(sp.Contract):
        def __init__(self, owner):
            self.data.messages = sp.big_map({})
            sp.cast(self.data.messages, sp.big_map[sp.address, sp.record(text = sp.string,
                                                                         timestamp = sp.timestamp)])
     
        @sp.entrypoint
        def write_message(self, text):
           data = sp.record(text = "", timestamp = sp.now)
           if self.data.messages.contains(sp.sender):
               data = self.data.messages[sp.sender]
               data.text += "," + text
           else:
               data.text = text
           data.timestamp = sp.now
           self.data.messages[sp.sender] = data
    
       
@sp.add_test()
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    scenario = sp.test_scenario("Test", main)
    c1 = main.TrulyEndlessWall(alice)
    scenario += c1
    c1.write_message(text="bob's message 1", _sender= bob)
    c1.write_message(text="bob's message 2"import smartpy as sp

@sp.module
def main():
    class TrulyEndlessWall(sp.Contract):
        def __init__(self, owner):
            self.data.messages = sp.big_map({})
            sp.cast(self.data.messages, sp.big_map[sp.address, sp.record(text = sp.string, timestamp = sp.timestamp)])
     
        @sp.entrypoint
        def write_message(self, text):
           data = sp.record(text = "", timestamp = sp.now)
           if self.data.messages.contains(sp.sender):
               data = self.data.messages[sp.sender]
               data.text += "," + text
           else:
               data.text = text
           data.timestamp = sp.now
           self.data.messages[sp.sender] = data
    
       
@sp.add_test()
def test():
    alice = sp.test_account("Alice").address
    bob = sp.test_account("Bob").address
    eve = sp.test_account("Eve").address
    scenario = sp.test_scenario("Test", main)
    c1 = main.TrulyEndlessWall(alice)
    scenario += c1
    c1.write_message(text="bob's message 1", timestamp=sp.timestamp(20), _sender= bob)
    c1.write_message(text="bob's message 2", timestamp=sp.timestamp(30), _sender= bob)
