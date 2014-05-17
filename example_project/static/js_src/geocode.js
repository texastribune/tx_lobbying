(function (exports, $, L) {
  'use strict';

  var geocode = function () {
    // url = 'http://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V04_01.aspx?';
    var url = 'http://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderService_V04_01.asmx';
    $.get(url, {
      apiKey: '7310e8fa0b15479fb44655c9a90958ab',
      version: '4.01',
    });
  };

  var drawMap = function ($el, options) {
    var $map = $('<div class="map"></div>');
    $map.insertAfter($el);

    // create a map in the "map" div, set the view to a given place and zoom
    var map = L.map($map[0], {
        scrollWheelZoom: false
      })
      .setView([options.lat, options.lng], 15);

    // add an OpenStreetMap tile layer
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // add a marker
    L.marker([options.lat, options.lng], {title: options.title}).addTo(map);
  };

  var geocodeAdr = function ($el) {
    var url = '/address/' + $el.attr('data-pk') + '/geocode/';  // XXX magic constant
    $.getJSON(url, function (data) {
      drawMap($el, {
        lat: data.latitude,
        lng: data.longitude,
        title: data.title
      });
    });
  };

  var map = function ($el) {
    // http://leafletjs.com/reference.html
    var lat = +$el.find('span.p-latitude').html();
    var lng = +$el.find('span.p-longitude').html();
    var title = $.trim($el.find('span.coordinate_quality').text());
    drawMap($el, {
      lat: lat,
      lng: lng,
      title: title
    });
  };

  // exports
  exports.geocode = {
    geocode: geocode,
    adr: geocodeAdr,
    map: map
  };

})(this, this.jQuery, this.L);
