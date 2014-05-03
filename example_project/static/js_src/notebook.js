(function (exports, $) {
  'use strict';
  var $paper = $('#notebook');
  var $nav = $('#breadcrumbs');

  var retrieve = function (url) {
    var $page = $('<article class="page"/>').appendTo($paper);
    // TODO don't use load, just do ajax and manually parse to get TITLE and
    // get rid of #main hack
    $page.load(url + ' #main', function () {
      // callback
    });
    // TODO use title instead of url
    $nav.append('<span class="page">' + url + '</span>');
    $page.data('notebook', {
      url: url,
      retrievedAt: Date.now()
    });
    $(window).scrollLeft(1e6);
  };

  $paper.on('click', 'a', function (e) {
    e.preventDefault();
    var $el = $(this);
    $nav.append('<span class="link">' + $el.text() + '</span>');
    retrieve($el.attr('href'));
  });

  // exports
  exports.notebook = {
    retrieve: retrieve
  };

})(this, this.jQuery);
