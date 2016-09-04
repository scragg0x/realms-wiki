var $startCollaborationBtn = $('#start-collaboration');
var $endCollaborationBtn = $('#end-collaboration');
var $loadingCollaborationBtn = $('#loading-collaboration');

function loadingCollaboration() {
  $endCollaborationBtn.hide();
  $startCollaborationBtn.hide();
  $loadingCollaborationBtn.show();
  $(document).trigger('loading-collaboration');
}

function startCollaboration() {
  $loadingCollaborationBtn.hide();
  $startCollaborationBtn.hide();
  $endCollaborationBtn.show();
  $(document).trigger('start-collaboration');
}

function endCollaboration() {
  $loadingCollaborationBtn.hide();
  $endCollaborationBtn.hide();
  $startCollaborationBtn.show();
  $(document).trigger('end-collaboration');
}

$(function() {
  $startCollaborationBtn.click(function(e) {
    loadingCollaboration();
    e.preventDefault();
  });
  $endCollaborationBtn.click(function(e) {
    endCollaboration();
    e.preventDefault();

  });
});
