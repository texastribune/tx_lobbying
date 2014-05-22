/* global notebook, $ */
(function (geocode) {
  'use strict';

  if (document.getElementById('notebook')) {
    notebook.retrieve('/');
  }

  $(function () {
    geocode.process();
  });
})(this.geocode);
