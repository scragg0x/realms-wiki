var $entry_markdown_header = $("#entry-markdown-header");
var $entry_preview_header = $("#entry-preview-header");
var $entry_markdown = $(".entry-markdown");
var $entry_preview = $(".entry-preview");
var $page_name = $("#page-name");
var $page_message = $("#page-message");

// Tabs
$entry_markdown_header.click(function(){
  $entry_markdown.addClass('active');
  $entry_preview.removeClass('active');
});

$entry_preview_header.click(function(){
  $entry_preview.addClass('active');
  $entry_markdown.removeClass('active');
});

$(document).on('shaMismatch', function() {
  bootbox.dialog({
    title: "Page has changed",
    message: "This page has changed and differs from your draft.  What do you want to do?",
    buttons: {
      ignore: {
        label: "Ignore",
        className: "btn-default",
        callback: function() {
          var info = aced.info();
          info['ignore'] = true;
          aced.info(info);
        }
      },
      discard: {
        label: "Discard Draft",
        className: "btn-danger",
        callback: function() {
          aced.discard();
        }
      },
      changes: {
        label: "Show Diff",
        className: "btn-primary",
        callback: function() {
          bootbox.alert("Draft diff not done! Sorry");
        }
      }
    }
  })
});

$(function(){
  $("#discard-draft-btn").click(function() {
    aced.discard();
  });

  $(".entry-markdown .floatingheader").click(function(){
    aced.editor.focus();
  });

  $("#delete-page-btn").click(function() {
    bootbox.confirm('Are you sure you want to delete this page?', function(result) {
      if (result) {
        deletePage();
      }
    });
  });
});

var deletePage = function() {
  var pageName = $page_name.val();
  var path = Config['RELATIVE_PATH'] + '/' + pageName;

  $.ajax({
    type: 'DELETE',
    url: path,
  }).done(function(data) {
    var msg = 'Deleted page: ' + pageName;
    bootbox.alert(msg, function() {
      location.href = '/';
    });
  }).fail(function(data, status, error) {
    bootbox.alert('Error deleting page!');
  });
};

var aced = new Aced({
  editor: $('#entry-markdown-content').find('.editor').attr('id'),
  renderer: function(md) { return MDR.convert(md) },
  info: Commit.info,
  submit: function(content) {
    var data = {
      name: $page_name.val().replace(/^\/*/g, "").replace(/\/+/g, "/"),
      message: $page_message.val(),
      content: content
    };

    // If renaming an existing page, use the old page name for the URL to PUT to
    var subPath = (PAGE_NAME) ? PAGE_NAME : data['name'];
    var path = Config['RELATIVE_PATH'] + '/' + subPath;
    var newPath = Config['RELATIVE_PATH'] + '/' + data['name'];

    var type = (Commit.info['sha']) ? "PUT" : "POST";

    $.ajax({
      type: type,
      url: path,
      data: data,
      dataType: 'json'
    }).always(function(data, status, error) {
      var res = data['responseJSON'];
      if (res && res['error']) {
        $page_name.addClass('parsley-error');
        bootbox.alert("<h3>" + res['message'] + "</h3>");
      } else {
        location.href = newPath;
      }
    });
  }
});
