var newvid=true;
function getArt(ytID){
    return "".concat('<img class="album-art img-responsive img-rounded" src="http://img.youtube.com/vi/', ytID, '/0.jpg">');
}

//// BACKBONE.MARIONETTE ////
var App = new Marionette.Application();

App.addRegions({
  queueRegion: '#queue-region'
});

App.on("start", function(){
  console.log("in Start block");

  var listView = new App.ListView({collection:data});
  App.queueRegion.show(listView);
  Backbone.history.start();

});

// ItemView for each of the songs
App.ItemView = Backbone.Marionette.ItemView.extend({
    initialize: function() {
        //For Debugging Purposes:
        //console.log('this.model =',this.model);
        //console.log(this);
    },
    template: '#queue-item-template',
    tagName: 'div',
    className: 'list-group-item metadata',
    modelEvents : {
	"change" : function() { this.render(); }
    }
});

// CompositeView to hold all of the Items.
App.ListView = Backbone.Marionette.CollectionView.extend({
    tagName: 'ul',
    className: 'list-group music-queue',
    template: '#queue-tempate',
    childViewContainer: 'ul',
    childView: App.ItemView,
    modelEvents : {
	"change" : function() { this.render(); }
    }
});


var Song = Backbone.Model.extend();
var Songs = Backbone.Collection.extend({
    model:Song
});


var data = new Songs([]);

var test = new Song({"songname":"Idioteque","songartist":'Radiohead',"albumarturl":"http://upload.wikimedia.org/wikipedia/en/8/8b/Radiohead.bends.albumart.jpg", "songID":"DNqv3nHyteM"});
//var test2 = new Song({"songname":"GDFR","songartist":'Flo Rida',"albumarturl":"http://upload.wikimedia.org/wikipedia/en/8/8b/Radiohead.bends.albumart.jpg", "songID":"F8Cg572dafQ"});
//data.push(test);
//data.push(test2);
//console.log(test);


// Controllers, etc
var MyController = Marionette.Controller.extend({
    makeHome: function() {
	var listView = new App.ListView({model:song,collection:data});
	App.queueRegion.show(listView);
    }
});


App.controller = new MyController();

// Routers
App.router = new Marionette.AppRouter({
    controller : App.controller,
    appRoutes : {
    default  :  "makeHome",     //  /#
    }
});



App.start();

///////// Youtube Iframe API shizz


// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
var playIndex;
var videoData;
var paused = false;




function onYouTubeIframeAPIReady(callback) {
     playIndex = 0;
     player = new YT.Player('player', {
        height: '200',
        width: '200',
        videoId: data.models[playIndex].attributes.songID, //yass
        playerVars: { 'controls': 0,'disablekb':0 },
        events: {
            'onReady': callback,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    console.log("player ready");
}

function showSong() {
    console.log("showing song");
    $(".now-playing-song-name").html(player.getVideoData()['title']);
    $(".song-artist").html(player.getVideoData()['author']);
    var albumart = "".concat('<img class="album-art img-responsive img-rounded" src="http://img.youtube.com/vi/', data.models[playIndex].attributes.songID, '/0.jpg">');
    console.log(albumart)
     $(".album-art").html(albumart);
}

function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.PLAYING) {
        $('.play').removeClass("glyphicon-play").addClass("glyphicon-pause");
        $('.play').attr("onclick", "pauseVideo()");
        if (newvid) {
            showSong();
            vynl.sockets.playingSong(data.models[0], ipAddress);
            vynl.sockets.deleteSong({songID: data.models[playIndex].attributes.songID}, ipAddress);
            newvid=false;
        }

    }
    if (event.data === YT.PlayerState.PAUSED){
        $('.play').removeClass("glyphicon-pause").addClass("glyphicon-play");
        $('.play').attr("onclick", "playVideo()");
    }


    if (event.data == YT.PlayerState.ENDED){
        nextVideo();
        newvid=true;
        //console.log("shootme");
    }

};

function playVideo() {
    if (player === undefined) {
        onYouTubeIframeAPIReady(playVideo);
        return;
    }
    player.playVideo();
    $('.play').removeClass("glyphicon-play").addClass("glyphicon-pause");
    $('.play').attr("onclick", "pauseVideo()");
};

function pauseVideo() {
    paused = true;
    player.pauseVideo();
    $('.play').removeClass("glyphicon-pause").addClass("glyphicon-play");
    $('.play').attr("onclick", "playVideo()");
};

function nextVideo(){
    if (playIndex < data.models.length) {
        player.loadVideoById(data.models[playIndex].attributes.songID);
    } else {
        console.warn("can't call nextVideo: end of queue");
    }
    newvid=true;
};

function prevVideo(){
    if (playIndex > 0) {
        //playIndex--;
        //player.loadVideoById(data.models[playIndex].attributes.songID);
        console.warn("Can't do previous videos until played view implemented.")
    } else {
        console.warn("can't call previousVideo: start of queue");
    }
};

function hideDJOnly() {
    $(".dj").remove();
}
function nonDJ() {
    $(".others").remove();
}

$(document).ready(function() {

    vynl.sockets.getUserID();

    vynl.sockets.socket.on('getID', function() {
           console.log(ipAddress);
           vynl.sockets.join();
    });

    vynl.sockets.socket.on('join', function(songs) {
        console.log("joined");
        console.log(songs);
        data.reset();
        if (ipAddress !== songs.dj) {
            toastr.info("You may suggest and vote on songs", "You are not the DJ");
            hideDJOnly();
        } else {
            toastr.success("You have full access to the playlist", "You are the DJ!");
            console.log("you're the dj!");
            nonDJ();
        }
        var i;
        for (i = 0; i < songs.songs.length; i++) {
            data.push(songs.songs[i]);
        }
    });

    vynl.sockets.socket.on('updateSongs', function(songs) {
        data.reset();
        for (i = 0; i < songs.songs.length; i++) {
            console.log(songs.songs[i]["songname"]);
            songs.songs[i]["songname"]=decodeURIComponent(songs.songs[i]["songname"]);
            console.log(songs.songs[i]["songname"]);
            songs.songs[i]["songartist"]=decodeURIComponent(songs.songs[i]["songartist"]);
            data.push(songs.songs[i]);
        }
    });

    vynl.sockets.socket.on('notifySongUpdate', function(songs) {
        vynl.sockets.getSongs();
    });

    vynl.sockets.socket.on('addSong', function(songs) {
        console.log(songs);
        data.reset();
        for (i = 0; i < songs.songs.length; i++) {
            data.push(songs.songs[i]);
        }
    });

    vynl.sockets.socket.on('playingSong', function(song) {
        console.log(song);
        console.log("playing song");
        $(".now-playing-song-name").html(song.song.songname);
        $(".song-artist").html(song.song.songartist);
        var albumart = "".concat('<img class="album-art img-responsive img-rounded" src="http://img.youtube.com/vi/', song.song.songID, '/0.jpg">');
        $(".album-art").html(albumart);
    });

    var handleClick = function(e) {
        e.stopPropagation();
        e.preventDefault();

        if (e.handled !== true) {
            console.log(e);

            id = e.target.dataset.id;
            console.log(e.target.dataset.id);

            vote = e.target.dataset.vote;
            console.log(e.target.dataset.vote);

            vynl.sockets.vote({"songID": id}, parseInt(vote), ipAddress);
        } else {
            return false;
        }
    }

    $(document).on('touchstart click', '.fa.thumbs', handleClick);

    var handleDeleteClick = function(e) {
        e.stopPropagation();
        e.preventDefault();

        if (e.handled !== true) {
            id = e.target.dataset.id;
            vynl.sockets.deleteSong({"songID": id}, ipAddress);
        } else {
            return false;
        }
    }

    $(document).on('touchstart click', '.fa.fa-times', handleDeleteClick);

	var lastTime = (new Date()).getTime();

	setInterval(function() {
	  var currentTime = (new Date()).getTime();
	  if (currentTime > (lastTime + 2000*2)) {  // ignore small delays
	      vynl.sockets.join();
	  } else {
              console.log("browser is awake");
          }
	  lastTime = currentTime;
	}, 2000);


    window.onbeforeunload = function(e) {
        console.log("bruddah left");
        vynl.sockets.leave();
        return null;
    };

    $(document).on('touchstart click', '.glyphicon-step-backward', prevVideo());
    $(document).on('touchstart', '.glyphicon-play', playVideo());
    $(document).on('touchstart click', '.glyphicon-step-forwards', nextVideo());

});
