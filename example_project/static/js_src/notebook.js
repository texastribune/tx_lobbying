(function (exports, $) {
  'use strict';
  var $paper = $('#notebook');

  var retrieve = function (url) {
    var $page = $('<div class="page"/>').appendTo($paper);
    $page.data('notebook', {
      url: url,
      retrievedAt: Date.now()
    });
    $page.load(url + ' #main', function () {
      console.log('load', arguments);
    });
    // $page.load(url + ' body');
  };

  // exports
  exports.notebook = {
    retrieve: retrieve
  };

})(this, this.jQuery);
