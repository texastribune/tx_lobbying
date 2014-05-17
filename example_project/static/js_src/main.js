/* global notebook */
(function () {
  'use strict';

  if (document.getElementById('notebook')) {
    notebook.retrieve('/');
  }
})();
