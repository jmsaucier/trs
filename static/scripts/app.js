function getChannelPreviewDiv(id,channel,playing){
    var ret = '';

    ret += '<div id="carousel-item-'+id+'" class="item">'


    ret += '<img src="http://static-cdn.jtvnw.net/previews-ttv/live_user_'+channel+'-960x540.jpg" />';
    ret += '<div class="container">';
    ret += '<div class="carousel-caption">';
    ret += '<p><a class="btn btn-lg- btn-primary" href="http://twitch.tv/'+channel+'">http://twitch.tv/'+channel+'<br/>'+channel+'</a></p>';
    ret += '<p>Currently playing: '+playing+'</p>';
    ret += '</a>';
    ret += '</div>';
    ret += '</div>';
    ret += '</div>';

    return ret;
}

var currentChannels = [];

$(document).ready(function(){

    $('.carousel').carousel({
        interval: false
    });

    $.ajax({
        url: '/recommend/',
        success: function(data){
            $('#btnGetRecommendations').hide();
            var container = $('#carousel-inner-container');
            container.empty();
            var data = JSON.parse(data);
            for(i in data) {
                var channelName = data[i][0];
    var playing = data[i][1];

                container.append(getChannelPreviewDiv(i,channelName, playing));

            }

            $('#carousel-inner-container div:first').addClass('active');




        }
    });

});
