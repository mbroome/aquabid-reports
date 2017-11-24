"use strict";
var page = require('webpage').create(),
    server = 'http://www.aquabid.com/cgi-bin/auction/search.cgi',
    data = 'searchstring=.*&searchtype=keyword&category=all&searchloc=All';

page.open(server, 'post', data, function(status){
    if(status !== 'success'){
       console.log('Unable to post');
    }else{
      console.log(page.content);
    }
    phantom.exit();
});

