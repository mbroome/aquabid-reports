"use strict";
var page = require('webpage').create(),
    server = 'http://www.aquabid.com/cgi-bin/auction/auction.cgi?disp&allend&24';

page.open(server, function(status){
    if(status !== 'success'){
       console.log('Unable to post');
    }else{
      console.log(page.content);
    }
    phantom.exit();
});

