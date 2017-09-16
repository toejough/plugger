class Base:
    def bar(self):
        return 'base bar'

class Bar(Base):
    def bar(self): return 'bar'


import plugger

def main():
    bars = plugger.Plugger('foo').resolve_any(Base)
    for bar in bars:
        print(bar.bar())
