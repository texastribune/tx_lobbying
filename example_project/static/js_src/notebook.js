(function (exports, $) {
  'use strict';
  var $paper = $('#notebook');
  var $nav = $('#breadcrumbs');

  var retrieve = function (url) {
    var $page = $('<div class="page"/>').appendTo($paper);
    // TODO don't use load, just do ajax and manually parse to get TITLE and
    // get rid of #main hack
    $page.load(url + ' #main', function () {
      console.log('load', arguments);
    });
    // TODO use title instead of url
    $nav.append('<span>' + url + '</span>');
    $page.data('notebook', {
      url: url,
      retrievedAt: Date.now()
    });
  };

  // exports
  exports.notebook = {
    retrieve: retrieve
  };

})(this, this.jQuery);
