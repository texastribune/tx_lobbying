'use strict';
/* global LOB */

var $ = require('jquery');
require('jquery-ui/autocomplete');

var source = function (request, response_func) {
  $.getJSON(LOB.ac, {q: request.term}, function (data) {
    response_func(data.results);
  });
};

var init = function () {
  $('#site_search')  // XXX magic constant
    .autocomplete({
      source: source
    });
};

exports.init = init;
