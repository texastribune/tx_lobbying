// FIXME browserify

var source = function (request, response_func) {
  console.log(request);
  $.getJSON(LOB.ac, {q: request.term}, function (data) {
    response_func(data.results);
  });
};

$('#site_search').autocomplete({
  source: source
});
