class Play:
    def __init__(self, play):
        for key in play.keys():
            setattr(self, key, play[key])
