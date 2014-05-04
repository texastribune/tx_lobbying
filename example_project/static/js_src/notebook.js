(function (exports, $) {
  'use strict';
  var $paper = $('#notebook');
  var $nav = $('#breadcrumbs');

  var retrieve = function (url) {
    var $page = $('<article class="page"/>').appendTo($paper);
    // TODO don't use load, just do ajax and manually parse to get TITLE and
    var $index = $('<span class="page"><em>loading...</em></span>').appendTo($nav);
    $.ajax(url, {
      dataType: 'html',
      success: function (data) {
        var $document = $('<div>' + data + '</div>');
        $page.append($document.find('div.page-content'));
        var title = $document.find('title').html() || 'TODO';
        $index.text(title);
      }
    });
    $page.data('notebook', {
      url: url,
      $index: $index,
      retrievedAt: Date.now()
    });
    $(window).scrollLeft(1e6);
  };

  var retrieveThis = function (e) {
    if (this.target) {
      // if a taget was set, treat as normal link
      return;
    }
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

    var $pageContent = $page.children().first();
    $pageContent.find('div.placeholder').remove();
    var newTop = $el.position().top + $el.outerHeight() + $pageContent.scrollTop();
    $('<div class="placeholder"/>').appendTo($pageContent)
      .css('top', newTop);
  };

  var $window = $(window);
  var adjustNavScroll = function () {
    var navWidth = $nav[0].scrollWidth;
    var windowWidth = $window.width();
    var offscreenWidth = document.body.scrollWidth - windowWidth;
    if (navWidth > windowWidth) {
      // TODO use translate instead of left
      var percentLeft = $window.scrollLeft() / offscreenWidth;
      $nav.css('left', -1 * percentLeft * (navWidth - windowWidth));
    }
  };

  $paper.on('click', 'a', retrieveThis);

  // XXX side effect
  $window.on('scroll', adjustNavScroll);

  // exports
  exports.notebook = {
    retrieve: retrieve
  };

})(this, this.jQuery);
