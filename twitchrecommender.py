import pg8000
import marshal
import random
import twitchapiretriever
from oauth import OAuthSignIn
from threading import Timer
import ConfigParser

print "Starting matrix load..."
#graphMatrix = marshal.load(open('graphMatrixFilled.dat', 'rb'))

print "Starting lookup load..."
channelLookupById = marshal.load(open('channelLookupById.dat','rb'))
channelLookupByName = {}
for i in channelLookupById:

    name = channelLookupById[i][1]
    #print name
    channelLookupByName[name] = channelLookupById

liveChannelCache = {}
auth = OAuthSignIn()

config = ConfigParser.RawConfigParser()
config.read('settings.cfg')

dbUser = config.get('AppSettings', 'db_user')
dbPass = config.get('AppSettings', 'db_pass')
dbName = config.get('AppSettings', 'db_name')


def refreshChannelCache():
    global liveChannelCache, channelLookupById

    channels = twitchapiretriever.getStreamingChannels(auth.client_id)

    tempChannelCache = {}
    for i in channels:
        channelName = i[0]
        gameName = i[1]
        tempChannelCache[channelName] = gameName

    #for i in channelLookupById:
#    tempChannelCache[channelLookupById[i][1]] = i

    liveChannelCache = tempChannelCache
    if __name__ != '__main__':
        cacheTimer = Timer(300.0, refreshChannelCache)
        cacheTimer.start()

def getChannelIdsForUserName(name, totalChannels):
    global dbUser, dbPass, dbName
    conn = pg8000.connect(user=dbUser, password=dbPass, database=dbName)
    cur = conn.cursor()
    cur.execute("""
       select distinct c.Id from "t_Channels" c
        join "t_gamechannelfollower_mapping" m on c.Id = m.channelId
        join "t_Followers" f on f.Id = m.followerId
        where f.name = %s and c.Id <= %s
    """,(name,totalChannels,))
    result = cur.fetchall()

    ret = map(lambda x: x[0], result)

    conn.commit()
    conn.close()
    return ret

def generateDetailedRecommendationListForUser(follower):
    global graphMatrix, channelLookupById
    totalFollowedChannels = getChannelIdsForUserName(follower, max(channelLookupById))
    followedChannels = filter(lambda x: channelLookupById[x][1] in liveChannelCache, totalFollowedChannels)

    if len(followedChannels) > 20:
        followedChannels = random.sample(totalFollowedChannels, 20)

    if len(followedChannels) == 0:
        totalFollowedChannels = random.sample(liveChannelCache, 20)
        followedChannels = filter(lambda x: channelLookupById[x][1] in liveChannelCache, totalFollowedChannels)

    uniqueViewerWorkingDict = {}

    for i in range(len(followedChannels)):
        channel = followedChannels[i]
        invChannel = followedChannels[len(followedChannels) - i - 1]
        uniqueViewerWorkingDict[channel] = float(graphMatrix[invChannel][invChannel])#graphMatrix[i][i])

    for i in range(len(followedChannels)):
        for j in range(i + 1, len(followedChannels)):
            iId = followedChannels[i]
            jId = followedChannels[j]
            uniqueViewerWorkingDict[jId] -= uniqueViewerWorkingDict[iId] * (graphMatrix[iId][jId] / float(graphMatrix[iId][iId]))
        #update_progress((i + 1) / float(len(followedChannels)))

    possibleRecommendations = [[float(0)] * (len(followedChannels) + 1)] * len(graphMatrix)

    for i in range(len(followedChannels)):
        for j in range(len(possibleRecommendations)):
            iId = followedChannels[i]
            if(iId != j and j in channelLookupById):
                graphMatrixFollowing = graphMatrix[iId][j]
                uniqueViewerCount = uniqueViewerWorkingDict[iId]
                possibleRecommendations[j][0] += graphMatrixFollowing * uniqueViewerCount


    recommendations = [i for i in sorted(enumerate(possibleRecommendations), key=lambda x: x[1], reverse=True)]
    recommendations = filter(lambda x: (not x[0] in totalFollowedChannels) and x[0] in channelLookupById and channelLookupById[x[0]][1] in liveChannelCache,recommendations )
    recommendations = map(lambda x: channelLookupById[x[0]][1], recommendations)

    return recommendations[:10]

def generateRecommendationListForUser(follower):
    global graphMatrix, channelLookupById, channelLookupByName
    #retrieve followers and filter to ones that aren't live
    #we do this because they may not [i]really[/i] like their followed channels that are live
    totalFollowedChannels = getChannelIdsForUserName(follower, max(channelLookupById))

    #they are not in the DB, so we need to generate random recommendations
    if follower == '' or len(totalFollowedChannels) == 0:
        totalFollowedChannels = random.sample(channelLookupById, 100)

    followedChannels = filter(lambda x: not channelLookupById[x] in liveChannelCache, totalFollowedChannels)
    #pair down list for easier analysis
    if len(followedChannels) > 20:
        followedChannels = random.sample(followedChannels, 20)


    uniqueViewerWorkingDict = {}

    #for now, all channels are created equal
    #this will change later when viewing multiple days actually counts for something
    #ie: i watched sevadus for 3 days, therefore he means a lot to me <3
    for i in followedChannels:
        uniqueViewerWorkingDict[i] = 1000

    #try to grab unique viewers across all channels
    for i in range(len(followedChannels)):
       for j in range(i + 1, len(followedChannels)):
           iId = followedChannels[i]
           jId = followedChannels[j]
           uniqueViewerWorkingDict[jId] -= uniqueViewerWorkingDict[iId] * (graphMatrix[iId][jId] / float(graphMatrix[iId][iId]))

    #initialize recommendation array
    possibleRecommendations = [float(0)] * len(graphMatrix)

    #compute recommendation
    for i in range(len(followedChannels)):
        for j in range(len(possibleRecommendations)):
            iId = followedChannels[i]
            if(iId != j and j in channelLookupById):
                graphMatrixFollowing = graphMatrix[iId][j] / float(graphMatrix[iId][iId])
                uniqueViewerCount = uniqueViewerWorkingDict[iId]
                possibleRecommendations[j] += graphMatrixFollowing * uniqueViewerCount

    recommendations = []

    #we need to make sure users that are not logged in aren't completely random
    #therefore we sort by number of viewers
    if(follower == ''):
        recommendations = [i for i in sorted(enumerate(possibleRecommendations), key=lambda x: x[1], reverse=True)]
    else:
        recommendations = [i for i in sorted(enumerate(possibleRecommendations), key=lambda x: x[1] / float(graphMatrix[x[0]][x[0]] + 1), reverse=True)]

    #sort and filter recommendations that are not live
    recommendations = filter(lambda x: (not x[0] in totalFollowedChannels) and x[0] in channelLookupById and channelLookupById[x[0]][1] in liveChannelCache,recommendations )

    def recommendation_mapping(x):
        name = channelLookupById[x[0]][1]
        game = liveChannelCache[name]
        return [name, game]

    #call mapping function to our output
    recommendations = map(recommendation_mapping, recommendations)
    #limit the number of recommendations, should probably load this number from config
    limitedRecommendation = recommendations[:min(len(recommendations), 10)]

    return limitedRecommendation

print "Starting refresh of channel cache..."
refreshChannelCache()
if __name__ == '__main__':
    print "Running recommendations"
    for j in range(3):
        recommendations = generateRecommendationListForUser('')
        for i in range(len(recommendations)):
            print i,recommendations[i][0], recommendations[i][1]
