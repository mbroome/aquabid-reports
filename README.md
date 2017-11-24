 Need phantomjs to scrape aquabid.

```shell
phantomjs  lib/pollers/active-auctions.js >active.html
bin/active.py > active.json
```

```shell
phantomjs  lib/pollers/closed-auctions.js >closed.html
bin/closed.py > closed.json
```

