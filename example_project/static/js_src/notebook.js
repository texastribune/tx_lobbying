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
    var $index = $('<span class="page">' + url + '</span>').appendTo($nav);
    $page.data('notebook', {
      url: url,
      $index: $index,
      retrievedAt: Date.now()
    });
    $(window).scrollLeft(1e6);
  };

  $paper.on('click', 'a', function (e) {
    e.preventDefault();
    var $el = $(this);
    var $page = $el.closest('article.page');

    // clear notebook to the right
    $page.nextAll().remove();
    var $index = $page.data('notebook').$index;
    $index.nextAll().remove();

    $nav.append('<span class="link">' + $el.text() + '</span>');
    retrieve($el.attr('href'));

    $page.find('a.clicked').removeClass('clicked');
    $el.addClass('clicked');

    $page.find('div.placeholder').remove();
    $('<div class="placeholder"/>').appendTo($page)
      .css('top', $el.position().top + $el.outerHeight());
  });

  // exports
  exports.notebook = {
    retrieve: retrieve
  };

})(this, this.jQuery);
