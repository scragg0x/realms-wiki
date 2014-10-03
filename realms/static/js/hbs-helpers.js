// Handlebar helpers
Handlebars.registerHelper('well', function(options) {
  return '<div class="well">' + options.fn(this) + '</div>';
});

Handlebars.registerHelper('well-sm', function(options) {
  return '<div class="well well-sm">' + options.fn(this) + '</div>';
});

Handlebars.registerHelper('well-lg', function(options) {
  return '<div class="well well-lg">' + options.fn(this) + '</div>';
});
