$(function(){

    // Cache some shit
    var $theme = $('#theme-list')
        , $preview = $('#preview')
        , $autosave = $('#autosave')
        , $wordcount = $('#wordcount')
        , $wordcounter = $('#wordcounter')
        , $pagename = $("#page-name");

    var editor
        , autoInterval
        , keyCheck // used to detect changes not made via keyup
        , profile =
        {
            theme: 'ace/theme/idle_fingers'
            , currentMd: ''
            , autosave:
        {
            enabled: true
            , interval: 3000 // might be too aggressive; don't want to block UI for large saves.
        }
            , current_filename : $pagename.val()
        };

    // Feature detect ish
    var dillinger = 'dillinger'
        , dillingerElem = document.createElement(dillinger)
        , dillingerStyle = dillingerElem.style
        , domPrefixes = 'Webkit Moz O ms Khtml'.split(' ');

    /// UTILS =================


    /**
     * Utility method to async load a JavaScript file.
     *
     * @param {String} The name of the file to load
     * @param {Function} Optional callback to be executed after the script loads.
     * @return {void}
     */
    function asyncLoad(filename,cb){
        (function(d,t){

            var leScript = d.createElement(t)
                , scripts = d.getElementsByTagName(t)[0];

            leScript.async = 1;
            leScript.src = filename;
            scripts.parentNode.insertBefore(leScript,scripts);

            leScript.onload = function(){
                cb && cb();
            }

        }(document,'script'));
    }

    /**
     * Utility method to determin if localStorage is supported or not.
     *
     * @return {Boolean}
     */
    function hasLocalStorage(){
        // http://mathiasbynens.be/notes/localstorage-pattern
        var storage;
        try{ if(localStorage.getItem) {storage = localStorage} }catch(e){}
        return storage;
    }

    /**
     * Grab the user's profile from localStorage and stash in "profile" variable.
     *
     * @return {Void}
     */
    function getUserProfile(){

        var p;

        try{
            p = JSON.parse( localStorage.profile );
            // Need to merge in any undefined/new properties from last release
            // Meaning, if we add new features they may not have them in profile
            p = $.extend(true, profile, p);
        }catch(e){
            p = profile
        }

        if (p.filename != $pagename.val()) {
            updateUserProfile({ filename: $pagename.val(), currentMd: "" });
        }
        profile = p;
    }

    /**
     * Update user's profile in localStorage by merging in current profile with passed in param.
     *
     * @param {Object}  An object containg proper keys and values to be JSON.stringify'd
     * @return {Void}
     */
    function updateUserProfile(obj){
        localStorage.clear();
        localStorage.profile = JSON.stringify( $.extend(true, profile, obj) );
    }

    /**
     * Utility method to test if particular property is supported by the browser or not.
     * Completely ripped from Modernizr with some mods.
     * Thx, Modernizr team!
     *
     * @param {String}  The property to test
     * @return {Boolean}
     */
    function prefixed(prop){ return testPropsAll(prop, 'pfx') }

    /**
     * A generic CSS / DOM property test; if a browser supports
     * a certain property, it won't return undefined for it.
     * A supported CSS property returns empty string when its not yet set.
     *
     * @param  {Object}  A hash of properties to test
     * @param  {String}  A prefix
     * @return {Boolean}
     */
    function testProps( props, prefixed ) {

        for ( var i in props ) {

            if( dillingerStyle[ props[i] ] !== undefined ) {
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
    function testPropsAll( prop, prefixed ) {

        var ucProp  = prop.charAt(0).toUpperCase() + prop.substr(1)
            , props   = (prop + ' ' + domPrefixes.join(ucProp + ' ') + ucProp).split(' ');

        return testProps(props, prefixed);
    }

    /**
     * Normalize the transitionEnd event across browsers.
     *
     * @return {String}
     */
    function normalizeTransitionEnd()
    {

        var transEndEventNames =
        {
            'WebkitTransition' : 'webkitTransitionEnd'
            , 'MozTransition'    : 'transitionend'
            , 'OTransition'      : 'oTransitionEnd'
            , 'msTransition'     : 'msTransitionEnd' // maybe?
            , 'transition'       : 'transitionend'
        };

        return transEndEventNames[ prefixed('transition') ];
    }



    /**
     * Get current filename from contenteditable field.
     *
     * @return {String}
     */
    function getCurrentFilenameFromField(){
        return $('#filename > span[contenteditable="true"]').text()
    }


    /**
     * Set current filename from profile.
     *
     * @param {String}  Optional string to force set the value.
     * @return {String}
     */
    function setCurrentFilenameField(str){
        $('#filename > span[contenteditable="true"]').text( str || profile.current_filename || "Untitled Document")
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
    function init(){

        if( !hasLocalStorage() ) { sadPanda() }
        else{

            // Attach to jQuery support object for later use.
            $.support.transitionEnd = normalizeTransitionEnd();

            getUserProfile();

            initAce();

            initUi();

            bindPreview();

            bindNav();

            bindKeyboard();

            autoSave();

        }

    }

    /**
     * Initialize theme and other options of Ace editor.
     *
     * @return {Void}
     */
    function initAce(){

        editor = ace.edit("editor");

    }

    /**
     * Initialize various UI elements based on userprofile data.
     *
     * @return {Void}
     */
    function initUi(){
        // Set proper theme value in theme dropdown
        fetchTheme(profile.theme, function(){
            $theme.find('li > a[data-value="'+profile.theme+'"]').addClass('selected');

            editor.getSession().setUseWrapMode(true);
            editor.setShowPrintMargin(false);

            editor.getSession().setMode('ace/mode/markdown');

            editor.getSession().setValue( profile.currentMd || editor.getSession().getValue());

            // Immediately populate the preview <div>
            previewMd();
        });


        // Set text for dis/enable autosave / word counter
        $autosave.html( profile.autosave.enabled ? '<i class="icon-remove"></i>&nbsp;Disable Autosave' : '<i class="icon-ok"></i>&nbsp;Enable Autosave' );
        $wordcount.html( !profile.wordcount ? '<i class="icon-remove"></i>&nbsp;Disabled Word Count' : '<i class="icon-ok"></i>&nbsp;Enabled Word Count' );

        setCurrentFilenameField();

        /* BEGIN RE-ARCH STUFF */

        $('.dropdown-toggle').dropdown();

        /* END RE-ARCH STUFF */

    }


    /// HANDLERS =================


    /**
     * Clear the markdown and text and the subsequent HTML preview.
     *
     * @return {Void}
     */
    function clearSelection(){
        editor.getSession().setValue("");
        previewMd();
    }

    // TODO: WEBSOCKET MESSAGE?
    /**
     * Save the markdown via localStorage - isManual is from a click or key event.
     *
     * @param {Boolean}
     * @return {Void}
     */
    function saveFile(isManual){
        if (!keyCheck && profile.currentMd != editor.getSession().getValue()) {
            previewMd();
            console.log(keyCheck);
        }
        keyCheck = false;
        updateUserProfile({currentMd: editor.getSession().getValue()});

        if (isManual) {
            updateUserProfile({  currentMd: "" });

            var data = {
                name: $pagename.val(),
                message: $("#page-message").val(),
                content: editor.getSession().getValue()
            };
            $.post(window.location, data, function(){
                location.href = "/" + data['name'];
            });
        }

    }

    /**
     * Enable autosave for a specific interval.
     *
     * @return {Void}
     */
    function autoSave(){

        if(profile.autosave.enabled) {
            autoInterval = setInterval( function(){
                // firefox barfs if I don't pass in anon func to setTimeout.
                saveFile();
            }, profile.autosave.interval);

        } else {
            clearInterval( autoInterval )
        }

    }

    $("#save-native").on('click', function() {
        saveFile(true);
    });


    /**
     * Clear out user profile data in localStorage.
     *
     * @return {Void}
     */
    function resetProfile(){
        // For some reason, clear() is not working in Chrome.
        localStorage.clear();
        // Let's turn off autosave
        profile.autosave.enabled = false
            // Delete the property altogether --> need ; for JSHint bug.
        ; delete localStorage.profile;
        // Now reload the page to start fresh
        window.location.reload();
    }

    /**
     * Dropbown nav handler to update the current theme.
     *
     * @return {Void}
     */
    function changeTheme(e){
        // check for same theme
        var $target = $(e.target);
        if( $target.attr('data-value') === profile.theme) { return; }
        else {
            // add/remove class
            $theme.find('li > a.selected').removeClass('selected');
            $target.addClass('selected');
            // grabnew theme
            var newTheme = $target.attr('data-value');
            $(e.target).blur();
            fetchTheme(newTheme, function(){

            });
        }
    }

    // TODO: Maybe we just load them all once and stash in appcache?
    /**
     * Dynamically appends a script tag with the proper theme and then applies that theme.
     *
     * @param {String}  The theme name
     * @param {Function}   Optional callback
     * @return {Void}
     */
    function fetchTheme(th, cb){
        var name = th.split('/').pop();
        asyncLoad("/static/js/ace/theme-"+ name +".js", function() {
            editor.setTheme(th);
            cb && cb();
            updateBg(name);
            updateUserProfile({theme: th});
        });

    }

    /**
     * Change the body background color based on theme.
     *
     * @param {String}  The theme name
     * @return {Void}
     */
    function updateBg(name){
        // document.body.style.backgroundColor = bgColors[name]
    }

    /**
     * Clientside update showing rendered HTML of Markdown.
     *
     * @return {Void}
     */
    function previewMd(){

        var unmd = editor.getSession().getValue()
            , md = MDR.convert(unmd, true);

        $preview
            .html('') // unnecessary?
            .html(md);

        //refreshWordCount();
    }

    /**
     * Stash current file name in the user's profile.
     *
     * @param {String}  Optional string to force the value
     * @return {Void}
     */
    function updateFilename(str){
        // Check for string because it may be keyup event object
        var f;
        if(typeof str === 'string'){
            f = str;
        } else {
            f = getCurrentFilenameFromField();
        }
        updateUserProfile( { current_filename: f });
    }


    function showHtml(){

        // TODO: UPDATE TO SUPPORT FILENAME NOT JUST A RANDOM FILENAME

        var unmd = editor.getSession().getValue();

        function _doneHandler(jqXHR, data, response){
            // console.dir(resp)
            var resp = JSON.parse(response.responseText);
            $('#myModalBody').text(resp.data);
            $('#myModal').modal();
        }

        function _failHandler(){
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

    /**
     * Show a sad panda because they are using a shitty browser.
     *
     * @return {Void}
     */
    function sadPanda(){
        // TODO: ACTUALLY SHOW A SAD PANDA.
        alert('Sad Panda - No localStorage for you!')
    }

    /**
     * Toggles the autosave feature.
     *
     * @return {Void}
     */
    function toggleAutoSave(){
        $autosave.html( profile.autosave.enabled ? '<i class="icon-remove"></i>&nbsp;Disable Autosave' : '<i class="icon-ok"></i>&nbsp;Enable Autosave' );
        updateUserProfile({autosave: {enabled: !profile.autosave.enabled }});
        autoSave();
    }

    /**
     * Bind keyup handler to the editor.
     *
     * @return {Void}
     */
    function bindPreview(){
        $('#editor').bind('keyup', function() {
            keyCheck = true;
            previewMd();
        });
    }

    /**
     * Bind navigation elements.
     *
     * @return {Void}
     */
    function bindNav(){

        $theme
            .find('li > a')
            .bind('click', function(e){
                changeTheme(e);
                return false;
            });

        $('#clear')
            .on('click', function(){
                clearSelection();
                return false;
            });

        $("#autosave")
            .on('click', function(){
                toggleAutoSave();
                return false;
            });

        $('#reset')
            .on('click', function(){
                resetProfile();
                return false;
            });

        $('#cheat').
            on('click', function(){
                window.open("https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet", "_blank");
                return false;
            });

    } // end bindNav()

    /**
     * Bind special keyboard handlers.
     *
     * @return {Void}
     */
    function bindKeyboard(){
        // CMD+s TO SAVE DOC
        key('command+s, ctrl+s', function(e){
            saveFile(true);
            e.preventDefault(); // so we don't save the webpage - native browser functionality
        });

        var saveCommand = {
            name: "save",
            bindKey: {
                mac: "Command-S",
                win: "Ctrl-S"
            },
            exec: function(){
                saveFile(true);
            }
        };

        editor.commands.addCommand(saveCommand);
    }

    init();
});



/**
 * Get scrollHeight of preview div
 * (code adapted from https://github.com/anru/rsted/blob/master/static/scripts/editor.js)
 *
 * @param {Object} The jQuery object for the preview div
 * @return {Int} The scrollHeight of the preview area (in pixels)
 */
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

/**
 * Scroll preview to match cursor position in editor session
 * (code adapted from https://github.com/anru/rsted/blob/master/static/scripts/editor.js)
 *
 * @return {Void}
 */

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
    $prev.scrollTop(scrollFactor * previewScrollRange);
}

window.onload = function(){
    var $loading = $('#loading');

    if ($.support.transition){
        $loading
            .bind( $.support.transitionEnd, function(){
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