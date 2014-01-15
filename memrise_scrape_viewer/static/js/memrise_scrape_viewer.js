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
    "aoColumns": [
      { "sType": "string" },
      { "sType": "string" },
      { "sType": "string" },
      { "sType": "int-None" },
    ],
    "oLanguage": {"sSearch": "Search all columns:"}
  });

  // Need to add a tfoot so the per-column search boxes will appear
  var tfoot = '<tfoot><tr>' +
      '<th rowspan="1" colspan="1"><input type="text" name="italian" placeholder="Search italian" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="english" placeholder="Search english" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="pos" placeholder="Search POS" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="rank" placeholder="Search rank" class="search_init"></th>' +
      '</tr></tfoot>';
  $('#things').append(tfoot);
	
  $("tfoot input").keyup(function () {
    /* Filter on the column (the index) of this element */
    oTable.fnFilter(this.value, $("tfoot input").index(this));
  });
});