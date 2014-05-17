/* global notebook, $ */
(function (geocode) {
  'use strict';

  if (document.getElementById('notebook')) {
    notebook.retrieve('/');
  }

  $(function () {
    $('p.h-adr').each(function () {
      var $el = $(this);
      if ($el.find('span.h-geo').length) {
        geocode.map($el);
      } else {
        geocode.adr($el);
      }
    });
  });
})(this.geocode);
