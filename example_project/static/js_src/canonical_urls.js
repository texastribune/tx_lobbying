// If the document we're looking at has a canonical url and it's different from
// the url we used to get here, then change it to match. This makes it possible
// for users to run through ids trying to look for matches, and gives them
// friendly urls too.
'use strict';

var $ = require('jquery');

// WISHLIST use xpath and get rid of jquery dependency
var init = function () {
  var $rel = $('head > link[rel=canonical]');
  if (!$rel.length) {
    // bail because nothing to do
    return;
  }
  var href = $rel.attr('href');
  if (href !== document.location.pathname) {
    if (history && history.replaceState) {
      history.replaceState(undefined, undefined, href);
    } else {
      document.location.replace(href);
    }
  }
};

exports.init = init;
