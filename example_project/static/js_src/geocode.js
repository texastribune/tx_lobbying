(function (exports, $, L) {
  'use strict';

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

  var mapMany = function ($container) {
    var uniquePoints = {};
    var bounds = [];
    var $points = $container.find('span.h-geo');
    if ($points.length === 0) {
      // nothing to map
      return;
    }
    var map = L.map($container.find('div.map')[0], {scrollWheelZoom: false});
    $points.each(function () {
      var $el = $(this);
      var lat = +$el.find('span.p-latitude').html();
      var lng = +$el.find('span.p-longitude').html();
      var key = lat + lng;
      lat = +lat;
      lng = +lng;
      if (uniquePoints[key]) {
        // this lat/lng has already been made into a marker
        return;
      }
      var title = $.trim($el.find('span.coordinate_quality').text());
      bounds.push([lat, lng]);
      var marker = L.marker([lat, lng], {title: title});
      marker.addTo(map);
      uniquePoints[key] = marker;
    });
    map.fitBounds(bounds);

    // add an OpenStreetMap tile layer
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  };

  // exports
  exports.geocode = {
    adr: geocodeAdr,
    map: map,
    mapMany: mapMany
  };

})(this, this.jQuery, this.L);
