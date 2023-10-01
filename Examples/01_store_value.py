import SmartPy as sp

@sp.module
def main():
    class StoreValue(sp.Contract):
        def __init__(self):
            self.data.value = 342185
