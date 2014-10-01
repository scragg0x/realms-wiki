function Aced(settings) {
  var id,
    options,
    editor,
    element,
    preview,
    previewWrapper,
    profile,
    autoInterval,
    themes,
    themeSelect,
    loadedThemes = {};

  settings = settings || {};

  options = {
    sanitize: true,
    preview: null,
    editor: null,
    theme: 'idle_fingers',
    themePath: '/static/vendor/ace-builds/src',
    mode: 'markdown',
    autoSave: true,
    autoSaveInterval: 5000,
    syncPreview: false,
    keyMaster: false,
    submit: function(data){ alert(data); },
    showButtonBar: false,
    themeSelect: null,
    submitBtn: null,
    renderer: null,
    info: null
  };

  themes = {
    chrome: "Chrome",
    clouds: "Clouds",
    clouds_midnight: "Clouds Midnight",
    cobalt: "Cobalt",
    crimson_editor: "Crimson Editor",
    dawn: "Dawn",
    dreamweaver: "Dreamweaver",
    eclipse: "Eclipse",
    idle_fingers: "idleFingers",
    kr_theme: "krTheme",
    merbivore: "Merbivore",
    merbivore_soft: "Merbivore Soft",
    mono_industrial: "Mono Industrial",
    monokai: "Monokai",
    pastel_on_dark: "Pastel on Dark",
    solarized_dark: "Solarized Dark",
    solarized_light: "Solarized Light",
    textmate: "TextMate",
    tomorrow: "Tomorrow",
    tomorrow_night: "Tomorrow Night",
    tomorrow_night_blue: "Tomorrow Night Blue",
    tomorrow_night_bright: "Tomorrow Night Bright",
    tomorrow_night_eighties: "Tomorrow Night 80s",
    twilight: "Twilight",
    vibrant_ink: "Vibrant Ink"
  };

  function editorId() {
    return "aced." + id;
  }

  function infoKey() {
    return editorId() + ".info";
  }

  function gc() {
    // Clean up localstorage
    store.forEach(function(key, val) {
      var re = new RegExp("aced\.(.*?)\.info");
      var info = re.exec(key);
      if (!info || !val.time) {
        return;
      }

      var id = info[1];

      // Remove week+ old stuff
      var now = new Date().getTime() / 1000;

      if (now > (val.time + 604800)) {
        store.remove(key);
        store.remove('aced.' + id);
      }
    });
  }

  function buildThemeSelect() {
    var $sel = $("<select class='aced-theme-sel' data-placeholder='Theme'></select>");
    $sel.append('<option></option>');
    $.each(themes, function(k, v) {
      $sel.append("<option value='" + k + "'>" + v + "</option>");
    });
    return $("<div/>").html($sel);
  }

  function toJquery(o) {
    return (typeof o == 'string') ? $("#" + o) : $(o);
  }

  function initProfile() {
    profile = {theme: ''};

    try {
      // Need to merge in any undefined/new properties from last release
      // Meaning, if we add new features they may not have them in profile
      profile = $.extend(true, profile, store.get('aced.profile'));
    } catch (e) { }
  }

  function updateProfile(obj) {
    profile = $.extend(null, profile, obj);
    store.set('profile', profile);
  }

  function render(content) {
    return (options.renderer) ? options.renderer(content) : content;
  }

  function bindKeyboard() {
    // CMD+s TO SAVE DOC
    key('command+s, ctrl+s', function (e) {
      submit();
      e.preventDefault();
    });

    var saveCommand = {
      name: "save",
      bindKey: {
        mac: "Command-S",
        win: "Ctrl-S"
      },
      exec: function () {
        submit();
      }
    };
    editor.commands.addCommand(saveCommand);
  }

  function info(info) {
    if (info) {
      store.set(infoKey(), info);
    }
    return store.get(infoKey());
  }

  function val(val) {
    // Alias func
    if (val) {
      editor.getSession().setValue(val);
    }
    return editor.getSession().getValue();
  }

  function discardDraft() {
    stopAutoSave();
    store.remove(editorId());
    store.remove(infoKey());
    location.reload();
  }

  function save() {
    store.set(editorId(), val());
  }

  function submit() {
    store.remove(editorId());
    store.remove(editorId() + ".info");
    options.submit(val());
  }

  function autoSave() {
    if (options.autoSave) {
      autoInterval = setInterval(function () {
        save();
      }, options.autoSaveInterval);
    } else {
      stopAutoSave();
    }
  }

  function stopAutoSave() {
    if (autoInterval){
      clearInterval(autoInterval)
    }
  }

  function renderPreview() {
    if (!preview) {
      return;
    }
    preview.html(render(val()));
    $('pre code', preview).each(function(i, e) {
      hljs.highlightBlock(e)
    });
  }

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

  function getPreviewWrapper(obj) {
    // Attempts to get the wrapper for preview based on overflow prop
    if (!obj) {
      return;
    }
    if (obj.css('overflow') == 'auto' || obj.css('overflow') == 'scroll') {
      return obj;
    } else {
      return getPreviewWrapper(obj.parent());
    }
  }

  function syncPreview() {

    var editorScrollRange = (editor.getSession().getLength());

    var previewScrollRange = (getScrollHeight(preview));

    // Find how far along the editor is (0 means it is scrolled to the top, 1
    // means it is at the bottom).
    var scrollFactor = editor.getFirstVisibleRow() / editorScrollRange;

    // Set the scroll position of the preview pane to match.  jQuery will
    // gracefully handle out-of-bounds values.

    previewWrapper.scrollTop(scrollFactor * previewScrollRange);
  }

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

  function setTheme(theme) {
    var cb = function(theme) {
      editor.setTheme('ace/theme/'+theme);
      updateProfile({theme: theme});
    };

    if (loadedThemes[theme]) {
      cb(theme);
    } else {
      asyncLoad(options.themePath + "/theme-" + theme + ".js", function () {
        cb(theme);
        loadedThemes[theme] = true;
      });
    }
  }

  function initSyncPreview() {
    if (!preview || !options.syncPreview) return;
    previewWrapper = getPreviewWrapper(preview);
    window.onload = function () {
      /**
       * Bind synchronization of preview div to editor scroll and change
       * of editor cursor position.
       */
      editor.session.on('changeScrollTop', syncPreview);
      editor.session.selection.on('changeCursor', syncPreview);
    };
  }

  function initProps() {
    // Id of editor
    if (typeof settings == 'string') {
      settings = { editor: settings };
    }

    if ('theme' in profile && profile['theme']) {
      settings['theme'] = profile['theme'];
    }

    if (settings['preview'] && !settings.hasOwnProperty('syncPreview')) {
      settings['syncPreview'] = true;
    }

    $.extend(options, settings);

    if (options.editor) {
      element = toJquery(options.editor);
    }

    $.each(options, function(k, v){
      if (element.data(k.toLowerCase())) {
        options[k] = element.data(k.toLowerCase());
      }
    });

    if (options.themeSelect) {
      themeSelect = toJquery(options.themeSelect);
    }

    if (options.submitBtn) {
      var submitBtn = toJquery(options.submitBtn);
      submitBtn.click(function(){
        submit();
      });
    }

    if (options.preview) {
      preview = toJquery(options.preview);

      // Enable sync unless set otherwise
      if (!settings.hasOwnProperty('syncPreview')) {
        options['syncPreview'] = true;
      }
    }

    if (!element.attr('id')) {
      // No id, make one!
      id = Math.random().toString(36).substring(7);
      element.attr('id', id);
    } else {
      id = element.attr('id')
    }
  }

  function initEditor() {
    editor = ace.edit(id);
    setTheme(profile.theme || options.theme);
    editor.getSession().setMode('ace/mode/' + options.mode);
    if (store.get(editorId()) && store.get(editorId()) != val()) {
      editor.getSession().setValue(store.get(editorId()));
    }
    editor.getSession().setUseWrapMode(true);
    editor.getSession().setTabSize(2);
    editor.getSession().setUseSoftTabs(true);
    editor.setShowPrintMargin(false);
    editor.renderer.setShowInvisibles(true);
    editor.renderer.setShowGutter(false);

    if (options.showButtonBar) {
      var $btnBar = $('<div class="aced-button-bar aced-button-bar-top">' + buildThemeSelect().html() + ' <button type="button" class="btn btn-primary btn-xs aced-save">Save</button></div>')
      element.find('.ace_content').before($btnBar);

      $(".aced-save", $btnBar).click(function(){
        submit();
      });

      if ($.fn.chosen) {
        $('select', $btnBar).chosen().change(function(){
          setTheme($(this).val());
        });
      }
    }

    if (options.keyMaster) {
      bindKeyboard();
    }

    if (preview) {
      editor.getSession().on('change', function (e) {
        renderPreview();
      });
      renderPreview();
    }

    if (themeSelect) {
      themeSelect
        .find('li > a')
        .bind('click', function (e) {
          setTheme($(e.target).data('value'));
          $(e.target).blur();
          return false;
        });
    }

    if (options.info) {
      // If no info exists, save it to storage
      if (!store.get(infoKey())) {
        store.set(infoKey(), options.info);
      } else {
        // Check info in storage against one passed in
        // for possible changes in data that may have occurred
        var info = store.get(infoKey());
        if (info['sha'] != options.info['sha'] && !info['ignore']) {
          // Data has changed since start of draft
          $(document).trigger('shaMismatch');
        }
      }
    }

    $(this).trigger('ready');
  }

  function init() {
    gc();
    initProfile();
    initProps();
    initEditor();
    initSyncPreview();
    autoSave();
  }

  init();

  return {
    editor: editor,
    submit: submit,
    val: val,
    discard: discardDraft,
    info: info
  };
}