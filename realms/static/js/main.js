// Init highlight JS
hljs.initHighlightingOnLoad();

// Markdown Renderer
MDR = {
    doc: null,
    callback: WMD.convert,
    sanitize: true, // Override
    convert: function(md, sanitize){
        if (this.sanitize !== null) {
            sanitize = this.sanitize;
        }
        this.doc = this.callback(md);
        var html = this.doc.html;
        if (sanitize) {
            // Causes some problems with inline styles
            html = html_sanitize(html, function(url) {
                if(/^https?:\/\//.test(url)) {
                    return url
                }
            }, function(id){
                return id;
            });
        }
        html = this.hook(html);
        return html;
    },
    hook: function(html) {
        if (!this.doc.metadata) {
            return html;
        }
        try {
            var template = Handlebars.compile(html);
            return template(this.doc.metadata);
        } catch(e) {
            return html;
        }
    }
};
