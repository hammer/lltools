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
  var oTable = $('#things').dataTable({
    bAutoWidth: false,
    bProcessing: true,
    bServerSide: true,
    bSortClasses: false,
    iDisplayLength: 20,
    oLanguage: {sSearch: 'Search all columns:'},
    sAjaxSource: 'vocabulary',
    sDom: '<"top"ip>rt<"bottom"ip><"clear">',
    aoColumns: [
      {mData: 'delete', sType: 'string',
       sWidth: '10px', bSortable: false, bSearchable: false},
      {mData: 'italian', sType: 'string',
       sClass: 'editable', sWidth: '20%'},
      {mData: "english", sType: "string",
       sClass: "editable", sWidth: "30%"},
      {mData: "part_of_speech", sType: "string",
       sClass: "editable", sWidth: "5%"},
      {mData: "course", sType: "string",
       sWidth: "15%"},
      {mData: "tags", sType: "string",
       sClass: "editabletags", sWidth: "20%"},
      {mData: "wiktionary_rank", sType: "int-None",
       sWidth: "5%", bSearchable: false},
      {mData: "it_2012_occurrences", sType: "int-None",
       sWidth: "5%", bSearchable: false},
    ],
    fnDrawCallback: function() {
      // Delete (row)
      var that = this;
      this.$('td:first-child').each(function () {
        that.fnUpdate('<form action="vocabulary" method="post" class="delete"> \
                        <button type="submit" class="fa fa-trash-o fa-lg"></button> \
                       </form>',
		      this.parentNode, 0, false, false);
      });

      $('form.delete').submit(function(e) {
        e.preventDefault();

	var row_id = this.parentNode.parentNode.getAttribute('id');
	var submitdata = {row_id: row_id, delete: true};

	jQuery.post('vocabulary', submitdata, function() {
	  $('#things').dataTable().fnStandingRedraw();
	});
      });

      // TODO(hammer): Don't copy code here
      // Update (text)
      $('#things tbody td.editable').editable('vocabulary', {
        callback: function(sValue, y) {
	  var oTable = $('#things').dataTable();
	  var aPos = oTable.fnGetPosition(this);
	  oTable.fnUpdate(sValue, aPos[0], aPos[1], false);
          oTable.fnStandingRedraw();
        },
	submitdata: function (value, settings) {
	  var oTable = $('#things').dataTable();
	  return {
	    row_id: this.parentNode.getAttribute('id'),
	    column: oTable.fnGetPosition(this)[2]
	  };
        },
	placeholder: ""
      });

      // Update (tags)
      var that = this;
      this.$('td.editabletags').each(function () {
	var input = $('<input />');
	var tags = [];
	$(this).text().split(',').forEach(function(tag) {
	  tags.push(tag);
	});
	// TODO(hammer): Find out why input.val(...) doesn't work
	input.attr('value', tags.join(','));

	var aPos = that.fnGetPosition(this);
        that.fnUpdate(input[0].outerHTML, aPos[0], aPos[1], false, false);
      });

      this.$('td.editabletags input').tagit({
	autocomplete: {source: 'vocabulary', autoFocus: true}
      });
    }
  });

  // Per-column filtering
  $("#search_things input").keyup(function () {
    var displayColumns = ['delete', 'italian', 'english', 'part_of_speech', 'course',
			   'tags', 'wiktionary_rank', 'it_2012_occurrences'];
    var iSearchIndex = displayColumns.indexOf(this.id);
    oTable.fnFilter(this.value, iSearchIndex);
  });

  // Autocomplete for tags
  $("input#tags").autocomplete({
    source: 'vocabulary',
    autoFocus: true
  });
});