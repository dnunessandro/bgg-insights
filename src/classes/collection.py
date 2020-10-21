from statistics import mean, median
from scipy.stats import pearsonr, spearmanr
from datetime import datetime
from copy import copy
from .boardgame import Boardgame
from .insight import Insight
from ..utils import getBestCurveFit, getHighestCountKeys
from collections import Counter

LAST_LOGGED_PLAY_THRESH = 180


class Collection:

    def __init__(self, collection):
        for key in collection.keys():
            setattr(self, key, collection[key])
        setattr(self, 'items', [Boardgame(x) for x in collection['items']])

    def getStatHist(self, stat):
        allStatEntries = []
        for item in self.items:
            for e in item.getAllStatEntries(stat):
                allStatEntries.append(e)
        return Counter(allStatEntries)

    def getStatGames(self, stat, statEntry):
        statGames = []
        for item in self.items:
            itemStatList = item.getAllStatEntries(stat)
            statFlag = False
            for e in itemStatList:
                if statEntry.lower() in e.lower():
                    statFlag = True
            if statFlag == True:
                statGames.append(
                    {'id': item.id, 'name': item.name, 'image': item.image})
        return statGames

    def getLastLoggedPlayDiff(self):
        if hasattr(self, 'lastLoggedPlay') and self.lastLoggedPlay != None:
            lastLoggedPlay = datetime.strptime(
                self.lastLoggedPlay.split('T')[0], "%Y-%m-%d")
            return abs((datetime.now() - lastLoggedPlay).days)
        else:
            return 1000000000000

    def getTotalItems(self):
        return self.totalItems

    def getTotalPlaysEachItem(self):
        return [item.numPlays for item in self.items]

    def getMostPlayed(self):
        if(self.checkIfAnyRecordedPlays()):
            plays = self.getTotalPlaysEachItem()
            indexMaxPlays = [i for i, x in enumerate(plays) if x == max(plays)]
            return [self.items[x] for x in indexMaxPlays]
        else:
            return []

    def getMostTimePlayed(self):
        if(self.checkIfAnyRecordedPlays()):
            plays = self.getTotalPlaysEachItem()
            playTimes = [x.playTime for x in self.items]
            timePlayed = [a*b/60 for a, b in zip(plays, playTimes)]
            indexMaxPlays = [i for i, x in enumerate(
                timePlayed) if x == max(timePlayed)]
            return [self.items[x] for x in indexMaxPlays]
        else:
            return []

    def getLeastPlayed(self):
        if(self.checkIfAnyRecordedPlays()):
            plays = self.getTotalPlaysEachItem()
            indexMinPlays = [i for i, x in enumerate(
                plays) if x == max(min(plays), 1)]
            return [self.items[x] for x in indexMinPlays]
        else:
            return []

    def getLeastTimePlayed(self):
        if(self.checkIfAnyRecordedPlays()):
            plays = self.getTotalPlaysEachItem()
            playTimes = [x.playTime for x in self.items]
            timePlayed = [a*b/60 for a, b in zip(plays, playTimes)]
            minTimePlayed = min([x for x in timePlayed if x > 0])
            indexMinPlays = [i for i, x in enumerate(
                timePlayed) if x == minTimePlayed]
            return [self.items[x] for x in indexMinPlays]
        else:
            return []

    def getAvgPlays(self):
        if not self.checkIfAnyRecordedPlays():
            return -1
        plays = self.getTotalPlaysEachItem()
        return mean(plays)

    def getAvgTimePlayed(self):
        if not self.checkIfAnyRecordedPlays():
            return -1
        plays = self.getTotalPlaysEachItem()
        playTimes = [x.playTime for x in self.items]
        timePlayed = [a*b/60 for a, b in zip(plays, playTimes)]
        return mean(timePlayed)

    def getNotPlayedItems(self):
        totalPlaysEachItem = self.getTotalPlaysEachItem()
        indexNoPlays = [i for i, x in enumerate(totalPlaysEachItem) if x == 0]
        notPlayedItems = [self.items[x] for x in indexNoPlays]
        return notPlayedItems

    def checkIfAnyRecordedPlays(self):
        plays = self.getTotalPlaysEachItem()
        for play in plays:
            if(play != 0):
                return True
            else:
                return False

    def checkIfAnyUserRatings(self):
        ratings = [x.userRating for x in self.items]
        for rating in ratings:
            if(rating != None):
                return True
            else:
                return False

    def checkIfAnyBggRatings(self):
        ratings = [x.bayesAverageRating for x in self.items]
        for rating in ratings:
            if(rating != None):
                return True
            else:
                return False

    def checkIfAnyAvgRatings(self):
        ratings = [x.averageRating for x in self.items]
        for rating in ratings:
            if(rating != None):
                return True
            else:
                return False

    def checkIfAnyYear(self):
        years = [x.yearPublished for x in self.items]
        for year in years:
            if(year != None):
                return True
            else:
                return False

    def checkIfAnyMaxPlayers(self):
        players = [x.maxPlayers for x in self.items]
        for player in players:
            if(player != None):
                return True
            else:
                return False

    def checkIfAnyMinPlayers(self):
        players = [x.minPlayers for x in self.items]
        for player in players:
            if(player != None):
                return True
            else:
                return False

    def checkIfAnyRecommendedPlayers(self):
        players = [x.recommendedPlayers for x in self.items]
        for player in players:
            if(player != None):
                return True
            else:
                return False

    def checkIfAnyPrices(self):
        prices = [x.medianPrice for x in self.items]
        for price in prices:
            if(price != None):
                return True
            else:
                return False

    def checkIfAnyRanks(self):
        ranks = self.getAllRanks()
        for rank in ranks:
            if(rank != None):
                return True
            else:
                return False

    def checkIfAnyWeights(self):
        weights = [
            x.averageWeight for x in self.items if x.averageWeight is not None]

        if len(weights) != 0:
            return True
        else:
            return False

    def getItemsValue(self):
        return [x.getItemValue() for x in self.items]

    def getMostExpensive(self):
        itemPrices = [
            x.medianPrice for x in self.items if x.medianPrice != None]
        itemsNotNone = [x for x in self.items if x.medianPrice != None]
        maxIndex = itemPrices.index(max(itemPrices))
        return itemsNotNone[maxIndex]

    def getLeastExpensive(self):
        itemPrices = [
            x.medianPrice for x in self.items if x.medianPrice != None]
        itemsNotNone = [x for x in self.items if x.medianPrice != None]
        minIndex = itemPrices.index(min(itemPrices))
        return itemsNotNone[minIndex]

    def getBestValue(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        itemsValue = self.getItemsValue()
        return max(itemsValue)

    def getBestValueItem(self):
        if not self.checkIfAnyRecordedPlays():
            return self.getLeastExpensive()

        bestValue = self.getBestValue()
        itemsValue = self.getItemsValue()
        bestValueIndex = itemsValue.index(bestValue)
        return self.items[bestValueIndex]

    def getWorstValue(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        if 0 in self.getTotalPlaysEachItem():
            return 0
        itemsValue = self.getItemsValue()
        return min(itemsValue)

    def getWorstValueItem(self):
        if not self.checkIfAnyRecordedPlays():
            return self.getMostExpensive()

        if 0 in self.getTotalPlaysEachItem():
            reducedCollection = copy(self)
            reducedCollection.items = [
                x for x in self.items if x.numPlays == 0]
            return reducedCollection.getMostExpensive()

        itemsValue = self.getItemsValue()
        minValue = min(itemsValue)
        minValueIndex = itemsValue.index(minValue)
        return self.items[minValueIndex]

    def getAvgValue(self):
        if not self.checkIfAnyRecordedPlays():
            return -1
        values = [x for x in self.getItemsValue() if x != -1]
        return mean(values)

    def getMaxWeightItem(self):
        weights = [
            x.averageWeight for x in self.items if x.averageWeight is not None]
        itemsNotNone = [x for x in self.items if x.averageWeight is not None]
        maxWeight = max(weights)
        maxWeightIndex = weights.index(maxWeight)
        return itemsNotNone[maxWeightIndex]

    def getMinWeightItem(self):
        weights = [
            x.averageWeight for x in self.items if x.averageWeight is not None]
        itemsNotNone = [x for x in self.items if x.averageWeight is not None]
        minWeight = min(weights)
        minWeightIndex = weights.index(minWeight)
        return itemsNotNone[minWeightIndex]

    def getAvgWeight(self):
        weights = [x.averageWeight
                   for x in self.items if x.averageWeight is not None]
        return mean(weights)

    def getHighestRatedItems(self):
        if not self.checkIfAnyUserRatings():
            return []
        nonNoneRatings = [x.userRating
                          for x in self.items if x.userRating != None]
        nonNoneRatedItems = [
            item for item in self.items if item.userRating != None]
        maxRatingIndexes = [i for i, x in enumerate(
            nonNoneRatings) if x == max(nonNoneRatings)]
        return [nonNoneRatedItems[index] for index in maxRatingIndexes]

    def getLowestRatedItems(self):
        if not self.checkIfAnyUserRatings():
            return []
        nonNoneRatings = [x.userRating
                          for x in self.items if x.userRating != None]
        nonNoneRatedItems = [
            item for item in self.items if item.userRating != None]
        minRatingIndexes = [i for i, x in enumerate(
            nonNoneRatings) if x == min(nonNoneRatings)]
        return [nonNoneRatedItems[index] for index in minRatingIndexes]

    def getAvgRating(self):
        ratings = [x.userRating
                   for x in self.items if x.userRating != None]
        return mean(ratings)

    def getHighestBggRating(self):
        BggRatings = [x.bayesAverageRating for x in self.items]
        maxBggRating = max(BggRatings)
        maxBggRatingIndex = BggRatings.index(maxBggRating)
        return self.items[maxBggRatingIndex]

    def getLowestBggRating(self):
        BggRatings = [x.bayesAverageRating for x in self.items if x != 0]
        nonZeroRatingItems = [
            item for item in self.items if item.bayesAverageRating != 0]
        minBggRating = min(BggRatings)
        minBggRatingIndex = BggRatings.index(minBggRating)
        return nonZeroRatingItems[minBggRatingIndex]

    def getAvgBggRating(self):
        bggRatings = [x.bayesAverageRating for x in self.items]
        return mean(bggRatings)

    def getHighestAvgRating(self):
        avgRatings = [x.averageRating for x in self.items]
        maxAvgRating = max(avgRatings)
        maxAvgRatingIndex = avgRatings.index(maxAvgRating)
        return self.items[maxAvgRatingIndex]

    def getAvgAvgRating(self):
        avgRatings = [x.averageRating for x in self.items]
        return mean(avgRatings)

    def getLowestAvgRating(self):
        avgRatings = [x.averageRating for x in self.items]
        minAvgRating = min(avgRatings)
        minAvgRatingIndex = avgRatings.index(minAvgRating)
        return self.items[minAvgRatingIndex]

    def getRatingDiffEachItem(self):
        return [x.getRatingDiff() for x in self.items]

    def getAvgRatingDiff(self):
        ratingDiffs = self.getRatingDiffEachItem()
        ratingDiffsNotNone = [x for x in ratingDiffs if x is not None]
        if ratingDiffsNotNone == []:
            return None
        return mean(ratingDiffsNotNone)

    def getLargestRatingDiffItem(self):
        ratingDiffs = self.getRatingDiffEachItem()
        ratingDiffsNotNone = [abs(x) for x in ratingDiffs if x is not None]
        if ratingDiffsNotNone == []:
            return []
        maxDiff = max(ratingDiffsNotNone)
        maxDiffIndex = ratingDiffsNotNone.index(maxDiff)
        itemsNotNone = [x for x in self.items if
                        x.getRatingDiff() is not None]
        return itemsNotNone[maxDiffIndex]

    def getLargestPosRatingDiffItem(self):
        ratingDiffs = self.getRatingDiffEachItem()
        ratingDiffsNotNone = [abs(x)
                              for x in ratingDiffs if (x is not None and x > 0)]
        if ratingDiffsNotNone == []:
            return []
        maxDiff = max(ratingDiffsNotNone)
        maxDiffIndex = ratingDiffsNotNone.index(maxDiff)
        itemsNotNone = [x for x in self.items if (
            x.getRatingDiff() is not None and x.getRatingDiff() > 0)]
        return itemsNotNone[maxDiffIndex]

    def getLargestNegRatingDiffItem(self):
        ratingDiffs = self.getRatingDiffEachItem()
        ratingDiffsNotNone = [abs(x)
                              for x in ratingDiffs if (x is not None and x < 0)]
        if ratingDiffsNotNone == []:
            return []
        maxDiff = max(ratingDiffsNotNone)
        maxDiffIndex = ratingDiffsNotNone.index(maxDiff)
        itemsNotNone = [x for x in self.items if (
            x.getRatingDiff() is not None and x.getRatingDiff() < 0)]
        return itemsNotNone[maxDiffIndex]

    def getRatingAvgRatingCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        avgRatings = [x.averageRating for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneAvgRatings = [avgRatings[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneAvgRatings), 'spearmanr': spearmanr(notNoneRatings, notNoneAvgRatings)}

    def getRatingWeightCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        weights = [x.averageWeight for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None and x.averageWeight is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneWeights = [weights[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneWeights), 'spearmanr': spearmanr(notNoneRatings, notNoneWeights)}

    def getRatingRecommendedPlayersCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        recommendedPlayers = [x.recommendedPlayers for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneRecommendedPlayers = [
            recommendedPlayers[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneRecommendedPlayers), 'spearmanr': spearmanr(notNoneRatings, notNoneRecommendedPlayers)}

    def getRatingMaxPlayersCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        maxPlayers = [x.maxPlayers for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneMaxPlayers = [
            maxPlayers[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneMaxPlayers), 'spearmanr': spearmanr(notNoneRatings, notNoneMaxPlayers)}

    def getRatingPlayTimeCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        playTimes = [x.playTime for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNonePlayTimes = [playTimes[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNonePlayTimes), 'spearmanr': spearmanr(notNoneRatings, notNonePlayTimes)}

    def getRatingPlaysCorr(self):
        if not self.checkIfAnyUserRatings() or not self.checkIfAnyRecordedPlays():
            return None
        ratings = [x.userRating for x in self.items]
        plays = self.getTotalPlaysEachItem()
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None and x.numPlays != 0]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNonePlays = [plays[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNonePlays), 'spearmanr': spearmanr(notNoneRatings, notNonePlays)}

    def getRatingTimePlayedCorr(self):
        if not self.checkIfAnyUserRatings() or not self.checkIfAnyRecordedPlays():
            return None
        ratings = [x.userRating for x in self.items]
        plays = self.getTotalPlaysEachItem()
        playTimes = [x.playTime for x in self.items]
        timePlayed = [a*b/60 for a, b in zip(plays, playTimes)]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None and x.numPlays != 0 and x.playTime != 0]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneTimePlayed = [timePlayed[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneTimePlayed), 'spearmanr': spearmanr(notNoneRatings, notNoneTimePlayed)}

    def getRatingPriceCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        prices = [x.medianPrice for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None and x.medianPrice is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNonePrices = [prices[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNonePrices), 'spearmanr': spearmanr(notNoneRatings, notNonePrices)}

    def getRatingYearCorr(self):
        if not self.checkIfAnyUserRatings():
            return None
        ratings = [x.userRating for x in self.items]
        years = [x.yearPublished for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.userRating is not None and x.yearPublished is not None]

        notNoneRatings = [ratings[index] for index in notNoneIndexes]
        notNoneYears = [years[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneYears), 'spearmanr': spearmanr(notNoneRatings, notNoneYears)}

    def getPlaysWeightCorr(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        plays = self.getTotalPlaysEachItem()
        weights = [x.averageWeight for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.numPlays != 0 and x.averageWeight is not None]

        notNonePlays = [plays[index] for index in notNoneIndexes]
        notNoneWeights = [weights[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNonePlays, notNoneWeights), 'spearmanr': spearmanr(notNonePlays, notNoneWeights)}

    def getPlaysPlayTimeCorr(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        plays = [x.numPlays for x in self.items]
        playTimes = [x.playTime for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.numPlays != 0]
        notNonePlays = [plays[index] for index in notNoneIndexes]
        notNonePlayTimes = [playTimes[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNonePlays, notNonePlayTimes), 'spearmanr': spearmanr(notNonePlays, notNonePlayTimes)}

    def getPlaysRecommendedPlayersCorr(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        plays = [x.numPlays for x in self.items]
        recommendedPlayers = [x.recommendedPlayers for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.numPlays != 0]

        notNoneRatings = [plays[index] for index in notNoneIndexes]
        notNoneRecommendedPlayers = [
            recommendedPlayers[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneRecommendedPlayers), 'spearmanr': spearmanr(notNoneRatings, notNoneRecommendedPlayers)}

    def getPlaysMaxPlayersCorr(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        plays = [x.numPlays for x in self.items]
        maxPlayers = [x.maxPlayers for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.numPlays != 0]

        notNoneRatings = [plays[index] for index in notNoneIndexes]
        notNoneMaxPlayers = [
            maxPlayers[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNoneMaxPlayers), 'spearmanr': spearmanr(notNoneRatings, notNoneMaxPlayers)}

    def getPlaysPriceCorr(self):
        if not self.checkIfAnyRecordedPlays():
            return None
        plays = self.getTotalPlaysEachItem()
        prices = [x.medianPrice for x in self.items]
        notNoneIndexes = [i for i, x in enumerate(
            self.items) if x.medianPrice is not None and x.numPlays != 0]

        notNoneRatings = [plays[index] for index in notNoneIndexes]
        notNonePrices = [
            prices[index] for index in notNoneIndexes]

        return {'pearsonr': pearsonr(notNoneRatings, notNonePrices), 'spearmanr': spearmanr(notNoneRatings, notNonePrices)}

    def getAvgYear(self):
        years = [x.yearPublished for x in self.items if x.yearPublished is not None]
        return int(mean(years))

    def getYearOccurrences(self):
        years = [x.yearPublished for x in self.items]
        yearSet = set(years)
        occurences = {}
        for year in yearSet:
            occurences[year] = years.count(year)
        return occurences

    def getAvgRecommendedPlayers(self):
        recommendedPlayers = [x.recommendedPlayers for x in self.items]
        return mean(recommendedPlayers)

    def getAvgMaxPlayers(self):
        maxPlayers = [x.maxPlayers for x in self.items]
        return mean(maxPlayers)

    def getMedianMaxPlayers(self):
        maxPlayers = [x.maxPlayers for x in self.items]
        return median(maxPlayers)

    def getAvgMinPlayers(self):
        minPlayers = [x.minPlayers for x in self.items]
        return mean(minPlayers)

    def getAvgPrice(self):
        prices = [x.medianPrice
                  for x in self.items if x.medianPrice is not None and x.medianPrice <= 500]
        return mean(prices)

    def getMedianPrice(self):
        prices = [x.medianPrice
                  for x in self.items if x.medianPrice is not None]
        return median(prices)

    def getTotalPrice(self):
        prices = [x.medianPrice
                  for x in self.items if x.medianPrice is not None and x.medianPrice <= 500]
        return sum(prices)

    def getAllRanks(self):
        return [x.getRank() for x in self.items]

    def genInsight(self, insightType):

        if insightType == 'mostPlayed':
            return genInsightMostPlayed(self)

        if insightType == 'mostTimePlayed':
            return genInsightMostTimePlayed(self)

        if insightType == 'leastPlayed':
            return genInsightLeastPlayed(self)

        if insightType == 'leastTimePlayed':
            return genInsightLeastTimePlayed(self)

        if insightType == 'avgPlays':
            return genInsightAvgPlays(self)

        if insightType == 'avgTimePlayed':
            return genInsightAvgTimePlayed(self)

        if insightType == 'notPlayed':
            return genInsightNotPlayed(self)

        if insightType == 'bestValue':
            return genInsightBestValue(self)

        if insightType == 'worstValue':
            return genInsightWorstValue(self)

        if insightType == 'avgValue':
            return genInsightAvgValue(self)

        if insightType == 'maxWeight':
            return genInsightMaxWeight(self)

        if insightType == 'minWeight':
            return genInsightMinWeight(self)

        if insightType == 'avgWeight':
            return genInsightAvgWeight(self)

        if insightType == 'highestRated':
            return genInsightHighestRated(self)

        if insightType == 'lowestRated':
            return genInsightLowestRated(self)

        if insightType == 'avgRating':
            return genInsightAvgRating(self)

        if insightType == 'highestBggRating':
            return genInsightHighestBggRating(self)

        if insightType == 'lowestBggRating':
            return genInsightLowestBggRating(self)

        if insightType == 'avgBggRating':
            return genInsightAvgBggRating(self)

        if insightType == 'highestAvgRating':
            return genInsightHighestAvgRating(self)

        if insightType == 'lowestAvgRating':
            return genInsightLowestAvgRating(self)

        if insightType == 'avgAvgRating':
            return genInsightAvgAvgRating(self)

        if insightType == 'avgRatingDiff':
            return genInsightAvgRatingDiff(self)

        if insightType == 'largestRatingDiff':
            return genInsightLargestRatingDiff(self)

        if insightType == 'largestPosRatingDiff':
            return genInsightLargestPosRatingDiff(self)

        if insightType == 'largestNegRatingDiff':
            return genInsightLargestNegRatingDiff(self)

        if insightType == 'ratingAvgRatingCorr':
            return genInsightRatingAvgRatingCorr(self)

        if insightType == 'ratingWeightCorr':
            return genInsightRatingWeightCorr(self)

        if insightType == 'ratingRecommendedPlayersCorr':
            return genInsightRatingRecommendedPlayersCorr(self)

        if insightType == 'ratingPlayTimeCorr':
            return genInsightRatingPlayTimeCorr(self)

        if insightType == 'ratingMaxPlayersCorr':
            return genInsightRatingMaxPlayersCorr(self)

        if insightType == 'ratingPlaysCorr':
            return genInsightRatingPlaysCorr(self)

        if insightType == 'ratingTimePlayedCorr':
            return genInsightRatingTimePlayedCorr(self)

        if insightType == 'ratingPriceCorr':
            return genInsightRatingPriceCorr(self)

        if insightType == 'ratingYearCorr':
            return genInsightRatingYearCorr(self)

        if insightType == 'playsWeightCorr':
            return genInsightPlaysWeightCorr(self)

        if insightType == 'playsPlayTimeCorr':
            return genInsightPlaysPlayTimeCorr(self)

        if insightType == 'playsRecommendedPlayersCorr':
            return genInsightPlaysRecommendedPlayersCorr(self)

        if insightType == 'playsMaxPlayersCorr':
            return genInsightPlaysMaxPlayersCorr(self)

        if insightType == 'playsPriceCorr':
            return genInsightPlaysPriceCorr(self)

        if insightType == 'avgYear':
            return genInsightAvgYear(self)

        if insightType == 'mostCommonYears':
            return genInsightMostCommonYears(self)

        if insightType == 'avgRecommendedPlayers':
            return genInsightAvgRecommendedPlayers(self)

        if insightType == 'avgMaxPlayers':
            return genInsightAvgMaxPlayers(self)

        if insightType == 'medianMaxPlayers':
            return genInsightMedianMaxPlayers(self)

        if insightType == 'avgMinPlayers':
            return genInsightAvgMinPlayers(self)

        if insightType == 'avgPrice':
            return genInsightAvgPrice(self)

        if insightType == 'medianPrice':
            return genInsightMedianPrice(self)

        if insightType == 'totalPrice':
            return genInsightTotalPrice(self)

        if insightType == 'top100':
            return genInsightTop100(self)

        if insightType == 'kickstarter':
            return genInsightKickstarter(self)

        if insightType == 'mostCommonCategory':
            return genInsightMostCommonCategory(self)

        if insightType == 'mostCommonMechanic':
            return genInsightMostCommonMechanic(self)

        if insightType == 'mostCommonFamily':
            return genInsightMostCommonFamily(self)

        if insightType == 'mostCommonPublisher':
            return genInsightMostCommonPublisher(self)

        if insightType == 'mostCommonDesigner':
            return genInsightMostCommonDesigner(self)

        if insightType == 'mostCommonArtist':
            return genInsightMostCommonArtist(self)

    def genAllInsights(self):
        insightTypes = ['mostPlayed', 'mostTimePlayed', 'leastPlayed', 'leastTimePlayed', 'avgPlays', 'avgTimePlayed',
                        'notPlayed', 'bestValue', 'worstValue', 'avgValue', 'maxWeight', 'minWeight', 'avgWeight', 'highestRated',
                        'lowestRated', 'avgRating', 'highestBggRating', 'lowestBggRating', 'avgBggRating', 'highestAvgRating',
                        'lowestAvgRating', 'avgAvgRating', 'avgRatingDiff', 'largestRatingDiff', 'largestPosRatingDiff',
                        'largestNegRatingDiff', 'ratingAvgRatingCorr', 'ratingWeightCorr', 'ratingRecommendedPlayersCorr',
                        'ratingPlayTimeCorr', 'ratingMaxPlayersCorr', 'ratingPlaysCorr', 'ratingTimePlayedCorr', 'ratingPriceCorr',
                        'ratingYearCorr', 'playsWeightCorr', 'playsPlayTimeCorr', 'playsRecommendedPlayersCorr', 'playsMaxPlayersCorr',
                        'playsPriceCorr', 'avgYear', 'mostCommonYears', 'avgRecommendedPlayers', 'avgMaxPlayers', 'medianMaxPlayers', 'avgMinPlayers',
                        'avgPrice', 'medianPrice', 'totalPrice', 'top100', 'kickstarter', 'mostCommonCategory', 'mostCommonMechanic', 'mostCommonFamily',
                        'mostCommonPublisher', 'mostCommonDesigner', 'mostCommonArtist']
        insights = {}
        for insightType in insightTypes:
            insight = self.genInsight(insightType)
            if insight.status == 'ok':
                insights[insightType] = insight.data
        return insights


def genInsightMostPlayed(collection):
    insightType = 'mostPlayed'
    mostPlayedItems = collection.getMostPlayed()

    if mostPlayedItems == []:
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'nPlays': mostPlayedItems[0].numPlays,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays} for x in mostPlayedItems]}
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightMostTimePlayed(collection):
    insightType = 'mostTimePlayed'
    mostPlayedItems = collection.getMostTimePlayed()

    if mostPlayedItems == []:
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'timePlayed': mostPlayedItems[0].numPlays * mostPlayedItems[0].playTime,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'playTime': x.playTime} for x in mostPlayedItems]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightLeastPlayed(collection):
    insightType = 'leastPlayed'
    leastPlayedItems = collection.getLeastPlayed()

    if leastPlayedItems == []:
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'nPlays': leastPlayedItems[0].numPlays,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays} for x in leastPlayedItems]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightLeastTimePlayed(collection):
    insightType = 'leastTimePlayed'
    leastPlayedItems = collection.getLeastTimePlayed()

    if leastPlayedItems == []:
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'timePlayed': leastPlayedItems[0].numPlays * leastPlayedItems[0].playTime,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'playTime': x.playTime} for x in leastPlayedItems]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightAvgPlays(collection):
    insightType = 'avgPlays'
    if not collection.checkIfAnyRecordedPlays():
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'avgPlays': collection.getAvgPlays(),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays} for x in collection.items]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightAvgTimePlayed(collection):
    insightType = 'avgTimePlayed'
    if not collection.checkIfAnyRecordedPlays():
        insightData = {
            'errorMessage': 'No recorded plays.'
        }
        insightStatus = 'error'
    elif collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    else:
        insightData = {
            'avgTimePlayed': collection.getAvgTimePlayed(),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'playTime': x.playTime} for x in collection.items]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightNotPlayed(collection):
    insightType = 'notPlayed'
    notPlayedItems = collection.getNotPlayedItems()

    if collection.getLastLoggedPlayDiff() > LAST_LOGGED_PLAY_THRESH:
        insightData = {
            'errorMessage': 'No recent logged plays.'
        }
        insightStatus = 'error'
    elif collection.totalPlays < 10:
        insightData = {
            'errorMessage': 'Not enough logged plays.'
        }
        insightStatus = 'error'
    elif notPlayedItems == []:
        insightData = {
            'nNotPlayed': 0,
            'prctNotPlayed': 0,
            'items': []}
        insightStatus = 'ok'
    else:
        insightData = {
            'nNotPlayed': len(notPlayedItems),
            'prctNotPlayed': round(len(notPlayedItems)/len(collection.items), 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image} for x in notPlayedItems]
        }
        insightStatus = 'ok'

    return Insight(insightType, insightData, insightStatus)


def genInsightBestValue(collection):
    insightType = 'bestValue'
    if not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    else:
        bestValueItem = collection.getBestValueItem()
        insightData = {
            'bestValue': round(collection.getBestValue(), 2),
            'items':  [{
                'id': bestValueItem.id,
                'name': bestValueItem.name,
                'image': bestValueItem.image,
                'nPlays': bestValueItem.numPlays,
                'price': bestValueItem.medianPrice,
                'value': bestValueItem.getItemValue()}]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightWorstValue(collection):
    insightType = 'worstValue'
    if not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    else:
        worstValueItem = collection.getWorstValueItem()

        insightData = {
            'worstValue': round(collection.getWorstValue(), 2),
            'items':  [{
                'id': worstValueItem.id,
                'name': worstValueItem.name,
                'image': worstValueItem.image,
                'nPlays': worstValueItem.numPlays,
                'price': worstValueItem.medianPrice,
                'value': worstValueItem.getItemValue()}]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgValue(collection):
    insightType = 'avgValue'
    if not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    elif round(collection.getAvgValue(), 2) == 0:
        insightData = {}
        insightStatus = 'Value is zero.'
    else:
        avgValue = collection.getAvgValue()
        insightData = {
            'avgValue': round(avgValue, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'price': x.medianPrice,
                'value': x.getItemValue()} for x in collection.items if x.getItemValue() != -1]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightMaxWeight(collection):
    insightType = 'maxWeight'
    if not collection.checkIfAnyWeights():
        insightData = {}
        insightStatus = 'No weights.'
    else:
        maxWeightItem = collection.getMaxWeightItem()
        insightData = {
            'maxWeight': round(maxWeightItem.averageWeight, 2),
            'items': [{
                'id': maxWeightItem.id,
                'name': maxWeightItem.name,
                'image': maxWeightItem.image,
                'weight': maxWeightItem.averageWeight}]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightMinWeight(collection):
    insightType = 'minWeight'
    if not collection.checkIfAnyWeights():
        insightData = {}
        insightStatus = 'No weights.'
    else:
        minWeightItem = collection.getMinWeightItem()
        insightData = {
            'minWeight': round(minWeightItem.averageWeight, 2),
            'items': [{
                'id': minWeightItem.id,
                'name': minWeightItem.name,
                'image': minWeightItem.image,
                'weight': minWeightItem.averageWeight}]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgWeight(collection):
    insightType = 'avgWeight'
    if not collection.checkIfAnyWeights():
        insightData = {}
        insightStatus = 'No weights.'
    else:
        avgWeight = collection.getAvgWeight()
        insightData = {
            'avgWeight': round(avgWeight, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'weight': x.averageWeight} for x in collection.items if x.averageWeight is not None]
        }
        insightStatus = "ok"
    return Insight(insightType, insightData, insightStatus)


def genInsightHighestRated(collection):
    insightType = 'highestRated'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        highestRatedItems = collection.getHighestRatedItems()
        insightData = {
            'highestUserRating': highestRatedItems[0].userRating,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'userRating': x.userRating} for x in highestRatedItems]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLowestRated(collection):
    insightType = 'lowestRated'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        lowestRatedItems = collection.getLowestRatedItems()
        insightData = {
            'lowestUserRating': lowestRatedItems[0].userRating,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'userRating': x.userRating} for x in lowestRatedItems]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgRating(collection):
    insightType = 'avgRating'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        avgRating = collection.getAvgRating()
        insightData = {
            'avgUserRating': round(avgRating, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'userRating': x.userRating} for x in collection.items if x.userRating != None]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightHighestBggRating(collection):
    insightType = 'highestBggRating'
    if not collection.checkIfAnyBggRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        highestBggRatingItem = collection.getHighestBggRating()
        insightData = {
            'highestBggRating': round(highestBggRatingItem.bayesAverageRating, 2),
            'items': [{
                'id': highestBggRatingItem.id,
                'name': highestBggRatingItem.name,
                'image': highestBggRatingItem.image,
                'bggRating': highestBggRatingItem.bayesAverageRating}]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLowestBggRating(collection):
    insightType = 'lowestBggRating'
    if not collection.checkIfAnyBggRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        lowestBggRatingItem = collection.getLowestBggRating()
        insightData = {
            'lowestBggRating': round(lowestBggRatingItem.bayesAverageRating, 2),
            'items': [{
                'id': lowestBggRatingItem.id,
                'name': lowestBggRatingItem.name,
                'image': lowestBggRatingItem.image,
                'bggRating': lowestBggRatingItem.bayesAverageRating}]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgBggRating(collection):
    insightType = 'avgBggRating'

    if not collection.checkIfAnyBggRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        avgBggRating = collection.getAvgBggRating()
        insightData = {
            'avgBggRating': round(avgBggRating, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'bggRating': x.bayesAverageRating} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightHighestAvgRating(collection):
    insightType = 'highestAvgRating'

    if not collection.checkIfAnyAvgRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        highestAvgRatingItem = collection.getHighestAvgRating()
        insightData = {
            'highestAvgRating': round(highestAvgRatingItem.averageRating, 2),
            'items': [{
                'id': highestAvgRatingItem.id,
                'name': highestAvgRatingItem.name,
                'image': highestAvgRatingItem.image,
                'avgRating': highestAvgRatingItem.averageRating}]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLowestAvgRating(collection):
    insightType = 'lowestAvgRating'

    if not collection.checkIfAnyAvgRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        lowestAvgRatingItem = collection.getLowestAvgRating()
        insightData = {
            'lowestAvgRating': round(lowestAvgRatingItem.averageRating, 2),
            'items': [{
                'id': lowestAvgRatingItem.id,
                'name': lowestAvgRatingItem.name,
                'image': lowestAvgRatingItem.image,
                'avgRating': lowestAvgRatingItem.averageRating}]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgAvgRating(collection):
    insightType = 'avgAvgRating'

    if not collection.checkIfAnyAvgRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        avgAvgRating = collection.getAvgAvgRating()
        insightData = {
            'avgAvgRating': round(avgAvgRating, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'avgRating': x.averageRating} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgRatingDiff(collection):
    insightType = 'avgRatingDiff'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        avgRatingDiff = collection.getAvgRatingDiff()
        insightData = {
            'avgRatingDiff': round(avgRatingDiff, 2),
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'ratingDiff': x.userRating - x.averageRating,
                'ratingDiffPrct': (x.userRating - x.averageRating) / x.averageRating} for x in collection.items if x.userRating != None]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLargestRatingDiff(collection):
    insightType = 'largestRatingDiff'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        largestDiffItem = collection.getLargestRatingDiffItem()
        insightData = {
            'largestRatingDiff': largestDiffItem.userRating - largestDiffItem.averageRating,
            'items': [{
                'id': largestDiffItem.id,
                'name': largestDiffItem.name,
                'image': largestDiffItem.image,
                'ratingDiff': largestDiffItem.userRating - largestDiffItem.averageRating,
                'ratingDiffPrct': (largestDiffItem.userRating - largestDiffItem.averageRating) / largestDiffItem.averageRating}
            ]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLargestPosRatingDiff(collection):
    insightType = 'largestPosRatingDiff'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        largestDiffItem = collection.getLargestPosRatingDiffItem()
        if largestDiffItem == []:
            insightData = {
            }
            insightStatus = 'No positive rating differences.'
        else:
            insightData = {
                'largestPosRatingDiff': largestDiffItem.userRating - largestDiffItem.averageRating,
                'items': [{
                    'id': largestDiffItem.id,
                    'name': largestDiffItem.name,
                    'image': largestDiffItem.image,
                    'ratingDiff': largestDiffItem.userRating - largestDiffItem.averageRating,
                    'ratingDiffPrct': (largestDiffItem.userRating - largestDiffItem.averageRating) / largestDiffItem.averageRating}]
            }
            insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightLargestNegRatingDiff(collection):
    insightType = 'largestNegRatingDiff'
    if not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        largestDiffItem = collection.getLargestNegRatingDiffItem()
        if largestDiffItem == []:
            insightData = {}
            insightStatus = 'No negative rating differencess.'
        else:
            insightData = {
                'largestNegRatingDiff': largestDiffItem.averageRating - largestDiffItem.userRating,
                'items': [{
                    'id': largestDiffItem.id,
                    'name': largestDiffItem.name,
                    'image': largestDiffItem.image,
                    'ratingDiff': largestDiffItem.userRating - largestDiffItem.averageRating,
                    'ratingDiffPrct': (largestDiffItem.userRating - largestDiffItem.averageRating) / largestDiffItem.averageRating}]
            }
            insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingAvgRatingCorr(collection):
    insightType = 'ratingAvgRatingCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating':  x.userRating,
        'avgRating': x.averageRating} for x in collection.items if x.userRating is not None and x.averageRating is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingAvgRatingCorr = collection.getRatingAvgRatingCorr()
        insightData = {
            'pearsonr': ratingAvgRatingCorr['pearsonr'][0],
            'spearmanr': ratingAvgRatingCorr['spearmanr'][0],
            'items': items
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingWeightCorr(collection):
    insightType = 'ratingWeightCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating':  x.userRating,
        'weight': x.averageWeight} for x in collection.items if x.userRating is not None and x.averageWeight is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingWeightCorr = collection.getRatingWeightCorr()
        insightData = {
            'pearsonr': ratingWeightCorr['pearsonr'][0],
            'spearmanr': ratingWeightCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['weight'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 1, 4.5)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingRecommendedPlayersCorr(collection):
    insightType = 'ratingRecommendedPlayersCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating': x.userRating,
        'recommendedPlayers': x.recommendedPlayers} for x in collection.items if x.userRating is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingRecommendedPlayersCorr = collection.getRatingRecommendedPlayersCorr()
        insightData = {
            'pearsonr': ratingRecommendedPlayersCorr['pearsonr'][0],
            'spearmanr': ratingRecommendedPlayersCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['recommendedPlayers'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 1, 7)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingMaxPlayersCorr(collection):
    insightType = 'ratingMaxPlayersCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating': x.userRating,
        'maxPlayers': x.maxPlayers} for x in collection.items if x.userRating is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingMaxPlayersCorr = collection.getRatingMaxPlayersCorr()
        insightData = {
            'pearsonr': ratingMaxPlayersCorr['pearsonr'][0],
            'spearmanr': ratingMaxPlayersCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['maxPlayers'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 1, 7)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingPlayTimeCorr(collection):
    insightType = 'ratingPlayTimeCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating': x.userRating,
        'playTime': x.playTime} for x in collection.items if x.userRating is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingPlayTimeCorr = collection.getRatingPlayTimeCorr()
        insightData = {
            'pearsonr': ratingPlayTimeCorr['pearsonr'][0],
            'spearmanr': ratingPlayTimeCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['playTime'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 10, 300)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingPlaysCorr(collection):
    insightType = 'ratingPlaysCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating': x.userRating,
        'nPlays': x.numPlays} for x in collection.items if x.userRating is not None and x.numPlays != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingPlaysCorr = collection.getRatingPlaysCorr()
        insightData = {
            'pearsonr': ratingPlaysCorr['pearsonr'][0],
            'spearmanr': ratingPlaysCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['nPlays'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 0, 100)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingTimePlayedCorr(collection):
    insightType = 'ratingTimePlayedCorr'
    items = [{
        'id': x.id,
        'name': x.name,
        'image': x.image,
        'userRating': x.userRating,
        'nPlays': x.numPlays,
        'playTime': x.playTime,
        'timePlayed': round((x.numPlays * x.playTime)/60, 2)} for x in collection.items if x.userRating is not None and x.numPlays != 0 and x.playTime != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingTimePlayedCorr = collection.getRatingTimePlayedCorr()
        insightData = {
            'pearsonr': ratingTimePlayedCorr['pearsonr'][0],
            'spearmanr': ratingTimePlayedCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['timePlayed'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 0, 100)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingPriceCorr(collection):
    insightType = 'ratingPriceCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'userRating': x.userRating,
                'price': x.medianPrice} for x in collection.items if x.userRating is not None and x.medianPrice is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingPriceCorr = collection.getRatingPriceCorr()
        insightData = {
            'pearsonr': ratingPriceCorr['pearsonr'][0],
            'spearmanr': ratingPriceCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['price'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 10, 300)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightRatingYearCorr(collection):
    insightType = 'ratingYearCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'userRating': x.userRating,
                'yearPublished': x.yearPublished} for x in collection.items if x.userRating is not None and x.yearPublished is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyUserRatings():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        ratingYearCorr = collection.getRatingYearCorr()
        insightData = {
            'pearsonr': ratingYearCorr['pearsonr'][0],
            'spearmanr': ratingYearCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['yearPublished'] for e in insightData['items']], [
            e['userRating'] for e in insightData['items']], 1980, 2020)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightPlaysWeightCorr(collection):
    insightType = 'playsWeightCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'weight': round(x.averageWeight, 1)} for x in collection.items if x.numPlays != 0 and x.averageWeight is not None]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No recorded plays.'
    else:
        playsWeightCorr = collection.getPlaysWeightCorr()
        insightData = {
            'pearsonr': playsWeightCorr['pearsonr'][0],
            'spearmanr': playsWeightCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['weight'] for e in insightData['items']], [
            e['nPlays'] for e in insightData['items']], 1, 4.5)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightPlaysPlayTimeCorr(collection):
    insightType = 'playsPlayTimeCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'playTime': x.playTime} for x in collection.items if x.numPlays != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        playsPlayTimeCorr = collection.getPlaysPlayTimeCorr()
        insightData = {
            'pearsonr': playsPlayTimeCorr['pearsonr'][0],
            'spearmanr': playsPlayTimeCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['playTime'] for e in insightData['items']], [
            e['nPlays'] for e in insightData['items']], 10, 300)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightPlaysRecommendedPlayersCorr(collection):
    insightType = 'playsRecommendedPlayersCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'recommendedPlayers': x.recommendedPlayers} for x in collection.items if x.numPlays != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        playsRecommendedPlayersCorr = collection.getPlaysRecommendedPlayersCorr()
        insightData = {
            'pearsonr': playsRecommendedPlayersCorr['pearsonr'][0],
            'spearmanr': playsRecommendedPlayersCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['recommendedPlayers'] for e in insightData['items']], [
            e['nPlays'] for e in insightData['items']], 1, 7)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightPlaysMaxPlayersCorr(collection):
    insightType = 'playsMaxPlayersCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'maxPlayers': x.maxPlayers} for x in collection.items if x.numPlays != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        playsMaxPlayersCorr = collection.getPlaysMaxPlayersCorr()
        insightData = {
            'pearsonr': playsMaxPlayersCorr['pearsonr'][0],
            'spearmanr': playsMaxPlayersCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['maxPlayers'] for e in insightData['items']], [
            e['nPlays'] for e in insightData['items']], 1, 7)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightPlaysPriceCorr(collection):
    insightType = 'playsPriceCorr'
    items = [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'nPlays': x.numPlays,
                'price': x.medianPrice} for x in collection.items if x.medianPrice is not None and x.numPlays != 0]
    if len(items) < 30:
        insightData = {}
        insightStatus = 'Less than 30 boardgames to consider.'
    elif not collection.checkIfAnyRecordedPlays():
        insightData = {}
        insightStatus = 'No rated items.'
    else:
        playsPriceCorr = collection.getPlaysPriceCorr()
        insightData = {
            'pearsonr': playsPriceCorr['pearsonr'][0],
            'spearmanr': playsPriceCorr['spearmanr'][0],
            'items': items
        }
        insightData['trend'] = getBestCurveFit([e['price'] for e in insightData['items']], [
            e['nPlays'] for e in insightData['items']], 10, 300)
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgYear(collection):
    insightType = 'avgYear'

    if not collection.checkIfAnyYear():
        insightData = {}
        insightStatus = 'No items with publication year.'
    else:
        avgYear = collection.getAvgYear()
        insightData = {
            'avgYear': avgYear,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'yearPublished': x.yearPublished} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonYears(collection):
    insightType = 'mostCommonYears'
    if not collection.checkIfAnyYear():
        insightData = {}
        insightStatus = 'No items with publication year.'
    else:
        yearOccurrences = collection.getYearOccurrences()
        yearOccurrencesKeys = list(yearOccurrences.keys())
        yearOccurrencesValues = list(yearOccurrences.values())
        maxOccurrences = max(yearOccurrencesValues)
        maxOccurrencesIndexes = [i for i, x in enumerate(
            yearOccurrencesValues) if x == max(yearOccurrencesValues)]
        insightData = {
            'mostCommonYears': [yearOccurrencesKeys[index] for index in maxOccurrencesIndexes],
            'mostCommonYearOccurrences': maxOccurrences,
            'yearOccurences': yearOccurrences,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'yearPublished': x.yearPublished} for x in collection.items if x.yearPublished in [yearOccurrencesKeys[index] for index in maxOccurrencesIndexes]]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgRecommendedPlayers(collection):
    insightType = 'avgRecommendedPlayers'

    if not collection.checkIfAnyRecommendedPlayers():
        insightData = {}
        insightStatus = 'No items with recommended players registered.'
    else:
        avgRecommendedPlayers = collection.getAvgRecommendedPlayers()
        insightData = {
            'avgRecommendedPlayers': avgRecommendedPlayers,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'recommendedPlayers': x.recommendedPlayers} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgMaxPlayers(collection):
    insightType = 'avgMaxPlayers'

    if not collection.checkIfAnyMaxPlayers():
        insightData = {}
        insightStatus = 'No items with max players registered.'
    else:
        avgMaxPlayers = collection.getAvgMaxPlayers()
        insightData = {
            'avgMaxPlayers': avgMaxPlayers,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'maxPlayers': x.maxPlayers} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMedianMaxPlayers(collection):
    insightType = 'medianMaxPlayers'

    if not collection.checkIfAnyMaxPlayers():
        insightData = {}
        insightStatus = 'No items with max players registered.'
    else:
        medianMaxPlayers = collection.getMedianMaxPlayers()
        insightData = {
            'medianMaxPlayers': medianMaxPlayers,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'maxPlayers': x.maxPlayers} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgMinPlayers(collection):
    insightType = 'avgMinPlayers'

    if not collection.checkIfAnyMinPlayers():
        insightData = {}
        insightStatus = 'No items with min players registered.'
    else:
        avgMinPlayers = collection.getAvgMinPlayers()
        insightData = {
            'avgMinPlayers': avgMinPlayers,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'minPlayers': x.minPlayers} for x in collection.items]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightAvgPrice(collection):
    insightType = 'avgPrice'

    if not collection.checkIfAnyPrices():
        insightData = {}
        insightStatus = 'No items with price registered.'
    else:
        avgPrice = collection.getAvgPrice()
        insightData = {
            'avgPrice': avgPrice,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'price': x.medianPrice} for x in collection.items if x.medianPrice is not None and x.medianPrice <= 500]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMedianPrice(collection):
    insightType = 'medianPrice'

    if not collection.checkIfAnyPrices():
        insightData = {}
        insightStatus = 'No items with price registered.'
    else:
        medianPrice = collection.getMedianPrice()
        insightData = {
            'medianPrice': medianPrice,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'price': x.medianPrice} for x in collection.items if x.medianPrice is not None]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightTotalPrice(collection):
    insightType = 'totalPrice'

    if not collection.checkIfAnyPrices():
        insightData = {}
        insightStatus = 'No items with price registered.'
    else:
        totalPrice = collection.getTotalPrice()
        insightData = {
            'totalPrice': totalPrice,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'price': x.medianPrice} for x in collection.items if x.medianPrice is not None and x.medianPrice <= 500]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightTop100(collection):
    insightType = 'top100'

    if not collection.checkIfAnyRanks():
        insightData = {}
        insightStatus = 'No items with rank registered.'
    else:
        ranks = [x for x in collection.getAllRanks() if x is not None]
        nTop100 = sum([1 for x in ranks if x <= 100])
        prctTop100 = nTop100 / len(ranks)

        insightData = {
            'nTop100': nTop100,
            'prctTop100': prctTop100,
            'items': [{
                'id': x.id,
                'name': x.name,
                'image': x.image,
                'rank': x.getRank()} for x in collection.items if x.getRank() is not None and x.getRank() <= 100]
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightKickstarter(collection):
    insightType = 'kickstarter'

    kickstarterGames = collection.getStatGames('families', 'kickstarter')

    nKickstarter = len(kickstarterGames)
    prctKickstarter = nKickstarter / len(collection.items)

    insightData = {
        'nKickstarter': nKickstarter,
        'prctKickstarter': round(prctKickstarter, 2),
        'items': kickstarterGames
    }
    insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonCategory(collection):
    insightType = 'mostCommonCategory'

    categoryHist = collection.getStatHist('categories')
    mostCommonCategory = getHighestCountKeys(categoryHist)

    if categoryHist[mostCommonCategory[0]] == 1:
        insightData = {}
        insightStatus = 'No category matching 2 or more boardgames.'
    else:
        mostCommonCategoryGames = []
        for categoryEntry in mostCommonCategory:
            mostCommonCategoryGamesAux = collection.getStatGames(
                'categories', categoryEntry)
            for game in mostCommonCategoryGamesAux:
                mostCommonCategoryGames.append(game)
        mostCommonCategoryGames = list(
            {v['id']: v for v in mostCommonCategoryGames}.values())

        insightData = {
            'mostCommonCategory': mostCommonCategory,
            'nMostCommonCategory': categoryHist[mostCommonCategory[0]],
            'prctMostCommonCategory': categoryHist[mostCommonCategory[0]] / len(collection.items),
            'categoryHist': categoryHist,
            'items': mostCommonCategoryGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonMechanic(collection):
    insightType = 'mostCommonMechanic'

    mechanicHist = collection.getStatHist('mechanics')
    mostCommonMechanic = getHighestCountKeys(mechanicHist)

    if mechanicHist[mostCommonMechanic[0]] == 1:
        insightData = {}
        insightStatus = 'No mechanic matching 2 or more boardgames.'
    else:
        mostCommonMechanicGames = []
        for mechanicEntry in mostCommonMechanic:
            mostCommonMechanicGamesAux = collection.getStatGames(
                'mechanics', mechanicEntry)
            for game in mostCommonMechanicGamesAux:
                mostCommonMechanicGames.append(game)
        mostCommonMechanicGames = list(
            {v['id']: v for v in mostCommonMechanicGames}.values())

        insightData = {
            'mostCommonMechanic': mostCommonMechanic,
            'nMostCommonMechanic': mechanicHist[mostCommonMechanic[0]],
            'prctMostCommonMechanic': mechanicHist[mostCommonMechanic[0]] / len(collection.items),
            'mechanicHist': mechanicHist,
            'items': mostCommonMechanicGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonFamily(collection):
    insightType = 'mostCommonFamily'

    familyHist = collection.getStatHist('families')
    mostCommonFamily = getHighestCountKeys(familyHist)

    if familyHist[mostCommonFamily[0]] == 1:
        insightData = {}
        insightStatus = 'No family matching 2 or more boardgames.'
    else:
        mostCommonFamilyGames = []
        for familyEntry in mostCommonFamily:
            mostCommonFamilyGamesAux = collection.getStatGames(
                'families', familyEntry)
            for game in mostCommonFamilyGamesAux:
                mostCommonFamilyGames.append(game)
        mostCommonFamilyGames = list(
            {v['id']: v for v in mostCommonFamilyGames}.values())

        insightData = {
            'mostCommonFamily': mostCommonFamily,
            'nMostCommonFamily': familyHist[mostCommonFamily[0]],
            'prctMostCommonFamily': familyHist[mostCommonFamily[0]] / len(collection.items),
            'familyHist': familyHist,
            'items': mostCommonFamilyGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonDesigner(collection):
    insightType = 'mostCommonDesigner'

    designerHist = collection.getStatHist('designers')
    mostCommonDesigner = getHighestCountKeys(designerHist)

    if designerHist[mostCommonDesigner[0]] == 1:
        insightData = {}
        insightStatus = 'No designer matching 2 or more boardgames.'
    else:
        mostCommonDesignerGames = []
        for designerEntry in mostCommonDesigner:
            mostCommonDesignerGamesAux = collection.getStatGames(
                'designers', designerEntry)
            for game in mostCommonDesignerGamesAux:
                mostCommonDesignerGames.append(game)
        mostCommonDesignerGames = list(
            {v['id']: v for v in mostCommonDesignerGames}.values())

        insightData = {
            'mostCommonDesigner': mostCommonDesigner,
            'nMostCommonDesigner': designerHist[mostCommonDesigner[0]],
            'prctMostCommonDesigner': designerHist[mostCommonDesigner[0]] / len(collection.items),
            'designerHist': designerHist,
            'items': mostCommonDesignerGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonPublisher(collection):
    insightType = 'mostCommonPublisher'

    publisherHist = collection.getStatHist('publishers')
    mostCommonPublisher = getHighestCountKeys(publisherHist)

    if publisherHist[mostCommonPublisher[0]] == 1:
        insightData = {}
        insightStatus = 'No publisher matching 2 or more boardgames.'
    else:
        mostCommonPublisherGames = []
        for designerEntry in mostCommonPublisher:
            mostCommonPublisherGamesAux = collection.getStatGames(
                'publishers', designerEntry)
            for game in mostCommonPublisherGamesAux:
                mostCommonPublisherGames.append(game)
        mostCommonPublisherGames = list(
            {v['id']: v for v in mostCommonPublisherGames}.values())

        insightData = {
            'mostCommonPublisher': mostCommonPublisher,
            'nMostCommonPublisher': publisherHist[mostCommonPublisher[0]],
            'prctMostCommonPublisher': publisherHist[mostCommonPublisher[0]] / len(collection.items),
            'publisherHist': publisherHist,
            'items': mostCommonPublisherGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)


def genInsightMostCommonArtist(collection):
    insightType = 'mostCommonArtist'

    artistHist = collection.getStatHist('artists')
    mostCommonArtist = getHighestCountKeys(artistHist)

    if artistHist[mostCommonArtist[0]] == 1:
        insightData = {}
        insightStatus = 'No artist matching 2 or more boardgames.'
    else:
        mostCommonArtistGames = []
        for designerEntry in mostCommonArtist:
            mostCommonArtistGamesAux = collection.getStatGames(
                'artists', designerEntry)
            for game in mostCommonArtistGamesAux:
                mostCommonArtistGames.append(game)
        mostCommonArtistGames = list(
            {v['id']: v for v in mostCommonArtistGames}.values())

        insightData = {
            'mostCommonArtist': mostCommonArtist,
            'nMostCommonArtist': len(mostCommonArtistGames),
            'prctMostCommonArtist': len(mostCommonArtistGames) / len(collection.items),
            'artistHist': artistHist,
            'items': mostCommonArtistGames
        }
        insightStatus = 'ok'
    return Insight(insightType, insightData, insightStatus)
