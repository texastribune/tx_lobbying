'use strict';

require('./canonical_urls').init();
require('./geocode').init();
require('./search').init();

// HACK get jquery available globally
window.$ = require('jquery');

// TODO
// if (document.getElementById('notebook')) {
//   notebook.retrieve('/');
// }
