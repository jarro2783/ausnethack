function onready(f) {
  document.addEventListener('DOMContentLoaded', f, false);
}

function ajax(method, request, success, failure) {
  var xhr = new XMLHttpRequest();
  xhr.open(method, request, true);
  xhr.onload = function () {
    success(xhr.response);
  }
  xhr.onerror = function() {
    failure(xhr.response)
  }
  xhr.send()
}

function get_high_scores() {
  ajax('GET', '/tables/high_scores', console.log);
}
