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

  $("#delete-draft-btn").click(function() {
    bootbox.alert("Not Done Yet! Sorry");
  });
});

var aced = new Aced({
  editor: $('#entry-markdown-content').find('.editor').attr('id'),
  renderer: function(md) { return MDR.convert(md) },
  info: Commit.info,
  submit: function(content) {
    var data = {
      name: $page_name.val(),
      message: $page_message.val(),
      content: content
    };

    var path = Config['RELATIVE_PATH'] + '/' + data['name'];
    var type = (Commit.info['sha']) ? "PUT" : "POST";

    $.ajax({
      type: type,
      url: path,
      data: data,
      dataType: 'json'
    }).always(function(data, status, error) {
      if (data && data['error']) {
        $page_name.addClass('parsley-error');
        bootbox.alert("<h3>" + data['message'] + "</h3>");
      } else {
        location.href = path;
      }
    });
  }
});