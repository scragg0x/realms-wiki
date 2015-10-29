// Init highlight JS
hljs.initHighlightingOnLoad();

function splitInput(str) {
  if (str.slice(0, 3) !== '---') return;

  var matcher = /\n(\.{3}|\-{3})/g;
  var metaEnd = matcher.exec(str);

  return metaEnd && [str.slice(0, metaEnd.index), str.slice(matcher.lastIndex)];
}

/* © 2013 j201
 * https://github.com/j201/meta-marked */

// Splits the given string into a meta section and a markdown section if a meta section is present, else returns null
var metaMarked = function(src, opt, callback) {
  if (Object.prototype.toString.call(src) !== '[object String]')
    throw new TypeError('First parameter must be a string.');

  var mySplitInput = splitInput(src);
  if (mySplitInput) {
    var meta;
    try {
      meta = jsyaml.safeLoad(mySplitInput[0]);
    } catch(e) {
      meta = null;
    }
    return {
      meta: meta,
      md: mySplitInput[1]
    };
  } else {
    return {
      meta: null,
      md: src
    }
  }
};

marked.setOptions({
  renderer: new marked.Renderer(),
  gfm: true,
  tables: true,
  breaks: false,
  pedantic: false,
  sanitize: false,
  smartLists: true,
  smartypants: false
});

// Markdown Renderer
var MDR = {
  meta: null,
  md: null,
  sanitize: true, // Override
  renderer: new marked.Renderer(),
  parse: function(md){
    return marked(md, { renderer: this.renderer });
  },
  convert: function(md, sanitize) {
    if (this.sanitize !== null) {
      sanitize = this.sanitize;
    }
    this.md = md;
    this.processMeta();
    try {
      var html = this.parse(this.md);
    } catch(e) {
      return this.md;
    }

    if (sanitize) {
      // Causes some problems with inline styles
      html = html_sanitize(html, function(url) {
        try {
          var prot = decodeURIComponent(url.toString());
        } catch (e) {
          return '';
        }
        if (prot.indexOf('javascript:') === 0) {
          return '';
        }
        return prot;
      }, function(id){
        return id;
      });
    }
    this.hook();
    return html;
  },

  processMeta: function() {
    var doc = metaMarked(this.md);
    this.md = doc.md;
    this.meta = doc.meta;
    if (this.meta) {
      try {
        var template = Handlebars.compile(this.md);
        this.md = template(this.meta);
      } catch(e) {
        console.log(e);
      }
    }
  },

  hook: function() {
  }
};

MDR.renderer.table = function(header, body) {
  return '<table class="table table-bordered">\n'
    + '<thead>\n'
    + header
    + '</thead>\n'
    + '<tbody>\n'
    + body
    + '</tbody>\n'
    + '</table>\n';
};