"use strict";
var page = require('webpage').create(),
    server = 'http://www.aquabid.com/cgi-bin/auction/closed.cgi',
    data = 'action=results&DAYS=3&category=all&B1=Submit';

page.open(server, 'post', data, function(status){
    if(status !== 'success'){
       console.log('Unable to post');
    }else{
      console.log(page.content);
    }
    phantom.exit();
});

