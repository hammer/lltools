// Custom sort for int-None type
$.fn.dataTableExt.oSort['int-None-asc']  = function(x,y) {
  if (x == 'None' && y == 'None') {
    return 0;
  } else if (x == 'None') {
    return 1;
  } else if (y == 'None') {
    return -1;
  } else {
    x = parseInt(x);
    y = parseInt(y);
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
  }
};

$.fn.dataTableExt.oSort['int-None-desc']  = function(x,y) {
  if (x == 'None' && y == 'None') {
    return 0;
  } else if (x == 'None') {
    return 1;
  } else if (y == 'None') {
    return -1;
  } else {
    x = parseInt(x);
    y = parseInt(y);
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
  }
};

$(document).ready(function() {
  var oTable = $('#things').dataTable({
    "bProcessing": true,
    "bServerSide": true,
    "sAjaxSource": "vocabulary",
    "aoColumns": [
      {"mData": "italian", "sType": "string"},
      {"mData": "english", "sType": "string"},
      {"mData": "part_of_speech", "sType": "string"},
      {"mData": "course", "sType": "string"},
      {"mData": "wiktionary_rank", "sType": "int-None", "bSearchable": false},
      {"mData": "it_2012_occurrences", "sType": "int-None", "bSearchable": false},
    ],
    "oLanguage": {"sSearch": "Search all columns:"},
    "bSortClasses": false
  });

  // Need to add a tfoot so the per-column search boxes will appear
  var tfoot = '<tfoot><tr>' +
      '<th rowspan="1" colspan="1"><input type="text" name="italian" placeholder="Search italian" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="english" placeholder="Search english" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="pos" placeholder="Search POS" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="course" placeholder="Search course" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '</tr></tfoot>';
  $('#things').append(tfoot);

  $("tfoot input").keyup(function () {
    /* Filter on the column (the index) of this element */
    oTable.fnFilter(this.value, $("tfoot input").index(this));
  });


  $('#wiktionary_unknown_words').dataTable({
    "aoColumns": [
      { "sType": "string" },
      { "sType": "string" },
      { "sType": "numeric" },
      { "sType": "numeric" },
    ],
    "bSortClasses": false
  });


  $('#it_2012_unknown_words').dataTable({
    "aoColumns": [
      { "sType": "string" },
      { "sType": "numeric" },
    ],
    "bSortClasses": false
  });
});