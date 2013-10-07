/*!
 * WMD - Wanton Markdown
 * Copyright (c) 2010 Caolan McMahon
 */



/**
 * Main function for converting markdown to HTML.
 *
 * @param {String} content
 * @param {Object} options
 * @return {String}
 * @api public
 */

var WMD = function (content, options) {
    var doc = {raw: content, markdown: content};
    var opt = WMD.readOptions(options);
    WMD.preprocess(doc, opt);
    doc.html = WMD.processor(doc.markdown);
    WMD.postprocess(doc, opt);
    doc.toString = function () {
        return doc.html;
    };
    return doc;
};


function gsub(str, re, fn, /*optional*/newstr) {
    newstr = newstr || '';
    var match = re.exec(str);
    if (match) {
        newstr += str.slice(0, match.index);
        newstr += fn.apply(null, match);
        remaining = str.slice(match.index + match[0].length);
        return gsub(remaining, re, fn, newstr);
    }
    return newstr + str;
}

WMD.processor = new Showdown.converter().makeHtml;

WMD.preprocessors = {

    underscores: function (doc) {
        // prevent foo_bar_baz from ending up with an italic word in the middle
        doc.markdown = gsub(doc.markdown,
            /(^(?! {4}|\t)\w+_\w+_\w[\w_]*)/, function (match) {
                var count = 0;
                for (var i = 0; i < match.length; i++) {
                    if (match[i] == '_') count++;
                }
                if (count === 2) {
                    return match.replace(/_/g, '\\_');
                }
                return match;
            }
        );
        return doc;
    },

    metadata: function (doc) {
        var key;
        var lines = doc.markdown.split('\n');
        doc.metadata = {};

        while (lines.length) {
            var match = /^(\S+):\s+(.*)$/.exec(lines[0]);
            if (match) {
                var key = match[1];
                doc.metadata[key] = match[2];
                lines.shift();
            }
            else {
                var continued_value = /^\s+(.+)$/.exec(lines[0]);
                // strip empty lines
                if (/^\s*$/.exec(lines[0])) {
                    lines.shift();
                }
                else if (continued_value && key) {
                    doc.metadata[key] += '\n' + continued_value[1];
                    lines.shift();
                }
                else break;
            }
        }
        doc.markdown = lines.join('\n');
        return doc;
    }
};

WMD.postprocessors = {};

/**
 * Extends a default set of options with those passed to it.
 *
 * @param {Object} options
 * @return {Object}
 * @api public
 */

WMD.readOptions = function (options) {
    var obj = {
        preprocessors: [
            WMD.preprocessors.metadata,
            WMD.preprocessors.underscores
        ],
        postprocessors: []
    };
    for (var k in options) {
        obj[k] = options[k];
    }
    return obj;
};

/**
 * Runs all the preprocessors defined in options on the doc object.
 * This is executed before passing the doc's markdown property to the processor
 * function to be turned into HTML.
 *
 * @param {Object} doc
 * @param {Object} options
 * @return {String}
 * @api public
 */

WMD.preprocess = function (doc, options) {
    return options.preprocessors.reduce(function (doc, fn) {
        return fn(doc);
    }, doc);
};

/**
 * Runs all the postprocessors defined in options on the doc object.
 * This is executed after passing the doc's markdown property to the processor
 * function to be turned into HTML.
 *
 * @param {Object} doc
 * @param {Object} options
 * @return {String}
 * @api public
 */

WMD.postprocess = function (doc, options) {
    return options.postprocessors.reduce(function (doc, fn) {
        return fn(doc);
    }, doc);
};