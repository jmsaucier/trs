import pg8000
import marshal
import random
import twitchapiretriever
from oauth import OAuthSignIn
from threading import Timer

print "Starting matrix load..."
graphMatrix = marshal.load(open('graphMatrixFilled.dat', 'rb'))
channelLookupById = marshal.load(open('channelLookupById.dat','rb'))
liveChannelCache = {}

auth = OAuthSignIn()

def refreshChannelCache():
    global liveChannelCache

    channels = twitchapiretriever.getStreamingChannels(auth.client_id)

    tempChannelCache = {}
    for i in channels:
        tempChannelCache[i[0]] = i[1]

    liveChannelCache = tempChannelCache
    
    cacheTimer = Timer(300.0, refreshChannelCache)


def getChannelIdsForUserName(name, totalChannels):
    conn = pg8000.connect(user="postgres", password="masons", database="TRS_Copy")
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



def generateRecommendationListForUser(follower):
    global graphMatrix, channelLookupById
    totalFollowedChannels = getChannelIdsForUserName(follower, max(channelLookupById))
    followedChannels = totalFollowedChannels

    if len(followedChannels) > 20:
        followedChannels = random.sample(totalFollowedChannels, 20)

    if len(followedChannels) == 0:
        followedChannels = random.sample(totalFollowedChannels, 20)

    uniqueViewerWorkingDict = {}

    for i in followedChannels:
        uniqueViewerWorkingDict[i] = float(graphMatrix[i][i])

    for i in range(len(followedChannels)):
        for j in range(i + 1, len(followedChannels)):
            iId = followedChannels[i]
            jId = followedChannels[j]
            uniqueViewerWorkingDict[jId] -= uniqueViewerWorkingDict[iId] * (graphMatrix[iId][jId] / float(graphMatrix[iId][iId]))
        #update_progress((i + 1) / float(len(followedChannels)))

    possibleRecommendations = [float(0)] * len(graphMatrix)

    for i in range(len(followedChannels)):
        for j in range(len(possibleRecommendations)):
            iId = followedChannels[i]
            if(iId != j and j in channelLookupById):
                graphMatrixFollowing = graphMatrix[iId][j]
                uniqueViewerCount = uniqueViewerWorkingDict[iId]
                possibleRecommendations[j] += graphMatrixFollowing * uniqueViewerCount
        #update_progress((i + 1) / float(len(followedChannels)))

    recommendations = [i for i in sorted(enumerate(possibleRecommendations), key=lambda x: x[1], reverse=True)]
    recommendations = filter(lambda x: (not x[0] in totalFollowedChannels) and x[0] in channelLookupById and channelLookupById[x[0]][1] in liveChannelCache,recommendations )
    recommendations = map(lambda x: channelLookupById[x[0]][1], recommendations)
    

    return recommendations[:10]
print "Starting refresh of channel cache..."
refreshChannelCache()