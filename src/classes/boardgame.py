from .play import Play


class Boardgame:
    def __init__(self, boardgame):
        for key in boardgame.keys():
            setattr(self, key, boardgame[key])

    def getPlays(self):
        try:
            return getattr(self, 'plays')
        except:
            return []

    # def getTotalPlays(self):
    #     return sum([Play(play).quantity for play in self.getPlays()])

    def getItemValue(self):
        return self.numPlays / self.averagePriceNew if self.averagePriceNew != None else -1

    def getRatingDiff(self):
        return None if self.userRating is None else self.userRating - self.averageRating

    def getRank(self):
        return [x for x in self.subtypeRatings if x['name'] == 'boardgame'][0]['value']

    def getAllStatEntries(self, stat):
        return [x['value'] for x in getattr(self, stat)]
