class DataStore():

    def __init__(self) -> None:
        self.text = ''
    
    def setText(self, context):
        self.text = context
    
    def getText(self):
        return self.text