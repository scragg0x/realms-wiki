/*
 Source is modified version of http://dillinger.io/
 */
$(function () {

  var url_prefix = "";
  var sha = $("#sha").text();
  var $theme = $('#theme-list');
  var $preview = $('#preview');
  var $autosave = $('#autosave');
  var $wordcount = $('#wordcount');
  var $wordcounter = $('#wordcounter');
  var $pagename = $("#page-name");

  var $entry_markdown_header = $("#entry-markdown-header");
  var $entry_preview_header = $("#entry-preview-header");

  // Tabs
  $entry_markdown_header.click(function(){
    $("section.entry-markdown").addClass('active');
    $("section.entry-preview").removeClass('active');
  });

  $entry_preview_header.click(function(){
    $("section.entry-preview").addClass('active');
    $("section.entry-markdown").removeClass('active');
  });


  var editor;
  var autoInterval;
  var profile = {
      theme: 'ace/theme/idle_fingers',
      currentMd: '',
      autosave: {
        enabled: true,
        interval: 3000 // might be too aggressive; don't want to block UI for large saves.
      },
      current_filename: $pagename.val()
  };

  // Feature detect ish
  var dillinger = 'dillinger';
  var dillingerElem = document.createElement(dillinger);
  var dillingerStyle = dillingerElem.style;
  var domPrefixes = 'Webkit Moz O ms Khtml'.split(' ');

  /// UTILS =================

  /**
   * Utility method to async load a JavaScript file.
   *
   * @param {String} The name of the file to load
   * @param {Function} Optional callback to be executed after the script loads.
   * @return {void}
   */
  function asyncLoad(filename, cb) {
    (function (d, t) {

      var leScript = d.createElement(t)
        , scripts = d.getElementsByTagName(t)[0];

      leScript.async = 1;
      leScript.src = filename;
      scripts.parentNode.insertBefore(leScript, scripts);

      leScript.onload = function () {
        cb && cb();
      }

    }(document, 'script'));
  }

  /**
   * Grab the user's profile from localStorage and stash in "profile" variable.
   *
   * @return {Void}
   */
  function getUserProfile() {
    localforage.getItem('profile', function(p) {
      profile = $.extend(true, profile, p);
      if (profile.filename != $pagename.val()) {
        setEditorValue("");
        updateUserProfile({ filename: $pagename.val(), currentMd: "" });
      } else {
        if (profile.currentMd) {
          setEditorValue(profile.currentMd);
        }
      }
    });
  }

  /**
   * Update user's profile in localStorage by merging in current profile with passed in param.
   *
   * @param {Object}  An object containg proper keys and values to be JSON.stringify'd
   * @return {Void}
   */
  function updateUserProfile(obj) {
    localforage.clear();
    localforage.setItem('profile', $.extend(true, profile, obj));
  }

  /**
   * Utility method to test if particular property is supported by the browser or not.
   * Completely ripped from Modernizr with some mods.
   * Thx, Modernizr team!
   *
   * @param {String}  The property to test
   * @return {Boolean}
   */
  function prefixed(prop) {
    return testPropsAll(prop, 'pfx')
  }

  /**
   * A generic CSS / DOM property test; if a browser supports
   * a certain property, it won't return undefined for it.
   * A supported CSS property returns empty string when its not yet set.
   *
   * @param  {Object}  A hash of properties to test
   * @param  {String}  A prefix
   * @return {Boolean}
   */
  function testProps(props, prefixed) {

    for (var i in props) {

      if (dillingerStyle[ props[i] ] !== undefined) {
        return prefixed === 'pfx' ? props[i] : true;
      }

    }
    return false
  }

  /**
   * Tests a list of DOM properties we want to check against.
   * We specify literally ALL possible (known and/or likely) properties on
   * the element including the non-vendor prefixed one, for forward-
   * compatibility.
   *
   * @param  {String}  The name of the property
   * @param  {String}  The prefix string
   * @return {Boolean}
   */
  function testPropsAll(prop, prefixed) {

    var ucProp = prop.charAt(0).toUpperCase() + prop.substr(1)
      , props = (prop + ' ' + domPrefixes.join(ucProp + ' ') + ucProp).split(' ');

    return testProps(props, prefixed);
  }

  /**
   * Normalize the transitionEnd event across browsers.
   *
   * @return {String}
   */
  function normalizeTransitionEnd() {

    var transEndEventNames =
    {
      'WebkitTransition': 'webkitTransitionEnd', 'MozTransition': 'transitionend', 'OTransition': 'oTransitionEnd', 'msTransition': 'msTransitionEnd' // maybe?
      , 'transition': 'transitionend'
    };

    return transEndEventNames[ prefixed('transition') ];
  }


  /**
   * Returns the full text of an element and all its children.
   * The script recursively traverses all text nodes, and returns a
   * concatenated string of all texts.
   *
   * Taken from
   * http://stackoverflow.com/questions/2653670/innertext-textcontent-vs-retrieving-each-text-node
   *
   * @param node
   * @return {int}
   */
  function getTextInElement(node) {
    if (node.nodeType === 3) {
      return node.data;
    }

    var txt = '';

    if (node = node.firstChild) do {
      txt += getTextInElement(node);
    } while (node = node.nextSibling);

    return txt;
  }

  /**
   * Counts the words in a string
   *
   * @param string
   * @return int
   */
  function countWords(string) {
    var words = string.replace(/W+/g, ' ').match(/\S+/g);
    return words && words.length || 0;
  }


  /**
   * Initialize application.
   *
   * @return {Void}
   */
  function init() {
    // Attach to jQuery support object for later use.
    $.support.transitionEnd = normalizeTransitionEnd();

    initAce();

    getUserProfile();

    initUi();

    bindPreview();

    bindNav();

    bindKeyboard();

    autoSave();
  }

  function initAce() {
    editor = ace.edit("editor");
    editor.focus();
    editor.setOptions({
      enableBasicAutocompletion: true
    });
  }

  function initUi() {
    // Set proper theme value in theme dropdown
    fetchTheme(profile.theme, function () {
      $theme.find('li > a[data-value="' + profile.theme + '"]').addClass('selected');

      editor.setBehavioursEnabled(true);
      editor.getSession().setUseWrapMode(true);
      editor.setShowPrintMargin(false);
      editor.getSession().setTabSize(2);
      editor.getSession().setUseSoftTabs(true);
      editor.renderer.setShowInvisibles(true);
      editor.renderer.setShowGutter(false);
      editor.getSession().setMode('ace/mode/markdown');
      setEditorValue(profile.currentMd || editor.getSession().getValue());
      previewMd();
    });


    // Set text for dis/enable autosave / word counter
    $autosave.html(profile.autosave.enabled ? '<i class="icon-remove"></i>&nbsp;Disable Autosave' : '<i class="icon-ok"></i>&nbsp;Enable Autosave');
    $wordcount.html(!profile.wordcount ? '<i class="icon-remove"></i>&nbsp;Disabled Word Count' : '<i class="icon-ok"></i>&nbsp;Enabled Word Count');

    $('.dropdown-toggle').dropdown();
  }


  function clearSelection() {
    setEditorValue("");
    previewMd();
  }

  function saveFile(isManual) {

    updateUserProfile({currentMd: editor.getSession().getValue()});

    if (isManual) {
      updateUserProfile({  currentMd: "" });

      var data = {
        name: $pagename.val(),
        message: $("#page-message").val(),
        content: editor.getSession().getValue()
      };
      $.post(window.location, data, function() {
        location.href = url_prefix + '/' + data['name'];
      });
    }

  }

  function autoSave() {

    if (profile.autosave.enabled) {
      autoInterval = setInterval(function() {
        saveFile();
      }, profile.autosave.interval);

    } else {
      clearInterval(autoInterval)
    }

  }

  $("#save-native").on('click', function() {
    saveFile(true);
  });


  function resetProfile() {
    // For some reason, clear() is not working in Chrome.
    localforage.clear();

    // Let's turn off autosave
    profile.autosave.enabled = false;
    localforage.removeItem('profile', function() {
      window.location.reload();
    });
  }

  function changeTheme(e) {
    // check for same theme
    var $target = $(e.target);
    if ($target.attr('data-value') === profile.theme) {
      return;
    }
    else {
      // add/remove class
      $theme.find('li > a.selected').removeClass('selected');
      $target.addClass('selected');
      // grabnew theme
      var newTheme = $target.attr('data-value');
      $(e.target).blur();
      fetchTheme(newTheme, function () {

      });
    }
  }

  function fetchTheme(th, cb) {
    var name = th.split('/').pop();
    asyncLoad("/static/vendor/ace-builds/src/theme-" + name + ".js", function () {
      editor.setTheme(th);
      cb && cb();
      updateBg(name);
      updateUserProfile({theme: th});
    });

  }

  function updateBg(name) {
    // document.body.style.backgroundColor = bgColors[name]
  }

  function setEditorValue(str) {
    editor.getSession().setValue(str);
  }

  function previewMd() {
    $preview.html(MDR.convert(editor.getSession().getValue(), true));
  }

  function updateFilename(str) {
    // Check for string because it may be keyup event object
    var f;
    if (typeof str === 'string') {
      f = str;
    } else {
      f = getCurrentFilenameFromField();
    }
    updateUserProfile({ current_filename: f });
  }


  function showHtml() {

    // TODO: UPDATE TO SUPPORT FILENAME NOT JUST A RANDOM FILENAME

    var unmd = editor.getSession().getValue();

    function _doneHandler(jqXHR, data, response) {
      // console.dir(resp)
      var resp = JSON.parse(response.responseText);
      $('#myModalBody').text(resp.data);
      $('#myModal').modal();
    }

    function _failHandler() {
      alert("Roh-roh. Something went wrong. :(");
    }

    var config = {
      type: 'POST',
      data: "unmd=" + encodeURIComponent(unmd),
      dataType: 'json',
      url: '/factory/fetch_html_direct',
      error: _failHandler,
      success: _doneHandler
    };

    $.ajax(config)

  }

  function toggleAutoSave() {
    $autosave.html(profile.autosave.enabled ? '<i class="icon-remove"></i>&nbsp;Disable Autosave' : '<i class="icon-ok"></i>&nbsp;Enable Autosave');
    updateUserProfile({autosave: {enabled: !profile.autosave.enabled }});
    autoSave();
  }

  function bindPreview() {
    editor.getSession().on('change', function (e) {
      previewMd();
    });
  }

  function bindNav() {

    $theme
      .find('li > a')
      .bind('click', function (e) {
        changeTheme(e);
        return false;
      });

    $('#clear')
      .on('click', function () {
        clearSelection();
        return false;
      });

    $("#autosave")
      .on('click', function () {
        toggleAutoSave();
        return false;
      });

    $('#reset')
      .on('click', function () {
        resetProfile();
        return false;
      });

    $('#cheat').
      on('click', function () {
        window.open("https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet", "_blank");
        return false;
      });

  } // end bindNav()


  function bindKeyboard() {
    // CMD+s TO SAVE DOC
    key('command+s, ctrl+s', function (e) {
      saveFile(true);
      e.preventDefault(); // so we don't save the web page - native browser functionality
    });

    var saveCommand = {
      name: "save",
      bindKey: {
        mac: "Command-S",
        win: "Ctrl-S"
      },
      exec: function () {
        saveFile(true);
      }
    };

    editor.commands.addCommand(saveCommand);
  }

  init();
});


function getScrollHeight($prevFrame) {
  // Different browsers attach the scrollHeight of a document to different
  // elements, so handle that here.
  if ($prevFrame[0].scrollHeight !== undefined) {
    return $prevFrame[0].scrollHeight;
  } else if ($prevFrame.find('html')[0].scrollHeight !== undefined &&
    $prevFrame.find('html')[0].scrollHeight !== 0) {
    return $prevFrame.find('html')[0].scrollHeight;
  } else {
    return $prevFrame.find('body')[0].scrollHeight;
  }
}


function syncPreview() {
  var $ed = window.ace.edit('editor');
  var $prev = $('#preview');

  var editorScrollRange = ($ed.getSession().getLength());

  var previewScrollRange = (getScrollHeight($prev));

  // Find how far along the editor is (0 means it is scrolled to the top, 1
  // means it is at the bottom).
  var scrollFactor = $ed.getFirstVisibleRow() / editorScrollRange;

  // Set the scroll position of the preview pane to match.  jQuery will
  // gracefully handle out-of-bounds values.
  $prev.parent().scrollTop(scrollFactor * previewScrollRange);
}

window.onload = function () {
  var $loading = $('#loading');

  if ($.support.transition) {
    $loading
      .bind($.support.transitionEnd, function () {
        $('#main').removeClass('bye');
        $loading.remove();
      })
      .addClass('fade_slow');
  } else {
    $('#main').removeClass('bye');
    $loading.remove();
  }

  /**
   * Bind synchronization of preview div to editor scroll and change
   * of editor cursor position.
   */
  window.ace.edit('editor').session.on('changeScrollTop', syncPreview);
  window.ace.edit('editor').session.selection.on('changeCursor', syncPreview);
};