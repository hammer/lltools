// http://www.datatables.net/plug-ins/api#fnStandingRedraw
$.fn.dataTableExt.oApi.fnStandingRedraw = function(oSettings) {
  if(oSettings.oFeatures.bServerSide === false){
    var before = oSettings._iDisplayStart;

    oSettings.oApi._fnReDraw(oSettings);

    // iDisplayStart has been reset to zero - so lets change it back
    oSettings._iDisplayStart = before;
    oSettings.oApi._fnCalculateEnd(oSettings);
  }

  // draw the 'current' page
  console.log("_iDisplayLength: " + oSettings["_iDisplayLength"]);
  console.log("_iDisplayStart: " + oSettings["_iDisplayStart"]);
  oSettings.oApi._fnDraw(oSettings);
};

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
  // Autocomplete support for jEditable fields
  $.editable.addInputType('autocomplete', {
    element: $.editable.types.text.element,
    plugin: function(settings, original) {
      $('input', this).autocomplete(settings.autocomplete);
    }
  });

  var oTable = $('#things').dataTable({
    "bAutoWidth": false,
    "bProcessing": true,
    "bServerSide": true,
    "bSortClasses": false,
    "oLanguage": {"sSearch": "Search all columns:"},
    "sAjaxSource": "vocabulary",
    "aoColumns": [
      {"mData": "delete", "sType": "string",
       "sWidth": "10px", "bSortable": false, "bSearchable": false},
      {"mData": "italian", "sType": "string",
       "sClass": "editable", "sWidth": "20%"},
      {"mData": "english", "sType": "string",
       "sClass": "editable", "sWidth": "30%"},
      {"mData": "part_of_speech", "sType": "string",
       "sClass": "editable", "sWidth": "5%"},
      {"mData": "course", "sType": "string",
       "sWidth": "15%"},
      {"mData": "tags", "sType": "string",
       "sClass": "editabletags", "sWidth": "20%"},
      {"mData": "wiktionary_rank", "sType": "int-None",
       "sWidth": "5%", "bSearchable": false},
      {"mData": "it_2012_occurrences", "sType": "int-None",
       "sWidth": "5%", "bSearchable": false},
    ],
    "fnDrawCallback": function () {
      // Delete (row)
      var that = this;
      this.$('td:first-child').each(function (i) {
        that.fnUpdate('<form action="vocabulary" method="post" class="delete"> \
                        <button type="submit" class="fa fa-trash-o fa-lg"></button> \
                       </form>',
		      this.parentNode, 0, false, false);
      });

      $('form.delete').submit(function(e) {
        e.preventDefault();

	var row_id = this.parentNode.parentNode.getAttribute('id');
	var submitdata = {"row_id": row_id, "delete": true};

	jQuery.post('vocabulary', submitdata, function() {
	  $('#things').dataTable().fnStandingRedraw();
	});
      });

      // TODO(hammer): Don't copy code here
      // Update (no autocomplete)
      $('#things tbody td.editable').editable('vocabulary', {
        "callback": function(sValue, y) {
	  var oTable = $('#things').dataTable();
	  var aPos = oTable.fnGetPosition(this);
	  oTable.fnUpdate(sValue, aPos[0], aPos[1], false);
          oTable.fnStandingRedraw();
        },
	"submitdata": function (value, settings) {
	  var oTable = $('#things').dataTable();
	  return {
	    "row_id": this.parentNode.getAttribute('id'),
	    "column": oTable.fnGetPosition(this)[2]
	  };
        },
	"placeholder": ""
      });

      // Update (autocomplete tags)
      $('#things tbody td.editabletags').editable('vocabulary', {
	"type": "autocomplete",
	"autocomplete": {
	  source: "vocabulary",
	  autoFocus: true,
	  messages: {
	    noResults: '',
	    results: function() {}
	  }
	},
        "callback": function(sValue, y) {
	  var oTable = $('#things').dataTable();
	  var aPos = oTable.fnGetPosition(this);
	  oTable.fnUpdate(sValue, aPos[0], aPos[1], false);
          oTable.fnStandingRedraw();
        },
	"submitdata": function (value, settings) {
	  var oTable = $('#things').dataTable();
	  return {
	    "row_id": this.parentNode.getAttribute('id'),
	    "column": oTable.fnGetPosition(this)[2]
	  };
        },
	"placeholder": ""
      });
    }
  });

  // Per-column filtering
  var tfoot = '<tfoot><tr>' +
      '<th rowspan="1" colspan="1"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="italian" placeholder="Search italian" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="english" placeholder="Search english" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="pos" placeholder="Search POS" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="course" placeholder="Search course" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"><input type="text" name="tags" placeholder="Search tags" class="search_init"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '<th rowspan="1" colspan="1"></th>' +
      '</tr></tfoot>';
  $('#things').append(tfoot);

  $("tfoot input").keyup(function () {
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
});