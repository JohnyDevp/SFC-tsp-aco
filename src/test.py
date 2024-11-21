class Parent:
    __world = None
    def __init__(self):
        print("Parent.__init__")
    def _parentcall(self):
        print("Parent.__my")

class Child(Parent):
    def __init__(self):
        super().__init__()
        print("Child.__init__")
    def callparent(self):
        super()._parentcall()
        print(super().__world)
        print("Calling parent... ",end="")

if __name__ == "__main__":
    c = Child()
    # c._Parent_parentcall()
    c.callparent()