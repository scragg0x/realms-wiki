$(document).on('loading-collaboration', function() {
  TogetherJS();
});

$(document).on('end-collaboration', function() {
  TogetherJS();
});

TogetherJSConfig_toolName = "Collaboration";
TogetherJSConfig_suppressJoinConfirmation = true;

if (User.is_authenticated) {
  TogetherJSConfig_getUserName = function () {
    return User.username;
  };

  TogetherJSConfig_getUserAvatar = function () {
    return User.avatar;
  };
}

TogetherJSConfig_on_ready = function () {
  startCollaboration();
};

TogetherJSConfig_on_close = function () {
  //endCollaboration();
};