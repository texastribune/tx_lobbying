'use strict';

var geocode = require('./geocode');
geocode.init();

var search = require('./search');
search.init();

// HACK get jquery available globally
window.$ = require('jquery');

// TODO
// if (document.getElementById('notebook')) {
//   notebook.retrieve('/');
// }
