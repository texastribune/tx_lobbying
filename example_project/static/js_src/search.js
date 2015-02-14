'use strict';
/* global LOB */

var $ = require('jquery');
require('jquery-ui/autocomplete');

var init = function () {
  $('#site_search')  // XXX magic constant
    .autocomplete({
      appendTo: $('#site_search').closest('form'),
      source: LOB.ac,
      select: function (e, ui) {
        // change urls
        // does not capture 'click' so can't interpret middle click
        document.location.href = ui.item.value;
      }
    });
};

exports.init = init;
