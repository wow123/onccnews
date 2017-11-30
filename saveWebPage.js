var  page = require('webpage').create(),
  system = require('system'),
  url;
if (system.args.length === 1) {
  console.log('Usage: SaveWebPage.js <some URL>');
  phantom.exit();
}

url = system.args[1];
page.settings.userAgent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36';
page.open(url, function(status) {
  if (status !== 'success') {
    console.log('FAIL to load the url');
  } else {
    var markup = page.evaluate(function(){return document.documentElement.innerHTML;});
    console.log(markup);
  }
  phantom.exit();
});
