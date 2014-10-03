// Helper to get hash from end of URL or generate a random one.
function getExampleRef() {
  var ref = new Firebase('https://' + Config['FIREBASE_HOSTNAME']);
  var hash = window.location.hash.replace(/^#fp-/, '');
  if (hash) {
    ref = ref.child(hash);
  } else {
    ref = ref.push(); // generate unique location.
    window.location = window.location + '#fp-' + ref.name(); // add it as a hash to the URL.
  }
  return ref;
}

function initFirepad() {
  var new_ = true;
  if (window.location.hash.lastIndexOf('#fp-', 0) === 0) {
    new_ = false;
  }
  var firepadRef = getExampleRef();
  var session = aced.editor.session;
  var content;

  if (new_) {
    content = session.getValue();
  }

  // Firepad wants an empty editor
  session.setValue('');

  //// Create Firepad.
  var firepad = Firepad.fromACE(firepadRef, aced.editor, {
    defaultText: content
  });

  firepad.on('ready', function() {
    startCollaboration();
  });

  $(document).on('end-collaboration', function() {
    firepad.dispose();
  });
}

$(document).on('loading-collaboration', function() {
  initFirepad(true);
});

$(function(){
  if (window.location.hash.lastIndexOf('#fp-', 0) === 0) {
    loadingCollaboration();
  }
});