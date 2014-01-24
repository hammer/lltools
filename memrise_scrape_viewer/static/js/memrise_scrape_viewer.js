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
    "bAutoWidth": false,
    "sAjaxSource": "vocabulary",
    "aoColumns": [
      {"mData": "delete", "sType": "string",
       "sWidth": "10px", "bSortable": false, "bSearchable": false},
      {"mData": "italian", "sType": "string",
       "sClass": "editable", "sWidth": "20%"},
      {"mData": "english", "sType": "string",
       "sClass": "editable", "sWidth": "30%"},
      {"mData": "part_of_speech", "sType": "string",
       "sClass": "editable", "sWidth": "10%"},
      {"mData": "course", "sType": "string",
       "sWidth": "20%"},
      {"mData": "wiktionary_rank", "sType": "int-None",
       "sWidth": "10%", "bSearchable": false},
      {"mData": "it_2012_occurrences", "sType": "int-None",
       "sWidth": "10%", "bSearchable": false},
    ],
    "oLanguage": {"sSearch": "Search all columns:"},
    "bSortClasses": false,
    "fnDrawCallback": function () {
      // sDefaultContent doesn't seem to work
      // Better to do on client than on server?
      var that = this;
      this.$('td:first-child').each(function (i) {
        that.fnUpdate('<form action="vocabulary" method="post" class="delete"> \
                        <button type="submit" class="fa fa-trash-o fa-lg"></button> \
                       </form>',
		      this.parentNode, 0, false, false);
      });

      // Delete
      $('form.delete').submit(function(e) {
        e.preventDefault();

	var row_id = this.parentNode.parentNode.getAttribute('id');
	var submitdata = {"row_id": row_id, "delete": true};

	jQuery.post('vocabulary', submitdata, function() {
	  $('#things').dataTable().fnDraw();
	});
      });

      // jEditable
      $('#things tbody td.editable').editable('vocabulary', {
        "callback": function(sValue, y) {
	  var oTable = $('#things').dataTable();
	  var aPos = oTable.fnGetPosition(this);
	  oTable.fnUpdate(sValue, aPos[0], aPos[1]);
          oTable.fnDraw();
        },
	"submitdata": function (value, settings) {
	  var oTable = $('#things').dataTable();
	  var aPos2 = oTable.fnGetPosition(this);
	  var id2 = oTable.fnGetData(aPos2[0]);
	  return {
	    "row_id": this.parentNode.getAttribute('id'),
	    "column": oTable.fnGetPosition(this)[2]
	  };
        },
	"placeholder": ""
      });
    }
  });

  // Need to add a tfoot so the per-column search boxes will appear
  var tfoot = '<tfoot><tr>' +
      '<th rowspan="1" colspan="1"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="italian" placeholder="Search italian" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="english" placeholder="Search english" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="pos" placeholder="Search POS" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="course" placeholder="Search course" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '</tr></tfoot>';
  $('#things').append(tfoot);

  $("tfoot input").keyup(function () {
    /* Filter on the column (the index) of this th element */
    oTable.fnFilter(this.value, $("tfoot th").index(this.parentNode));
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

  /* Apply the jEditable handlers to the table */
});