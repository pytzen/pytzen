import pytzen as zen
from dataclasses import dataclass

@dataclass
class Test(zen.ProtoType):

    some_attribute: str = 'some_value'

    def testing(self):
        print(self.config.some_input)
        self.log('testing')
        self.store('some_attribute', self.some_attribute)

if __name__=='__main__':
    
    instance = Test()
    instance.testing()
    instance.close()