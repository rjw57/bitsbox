$(document).ready(function() {
  var drawerSelect = $('#drawer-select'),
      cabinetSelect = $('#cabinet-select'),
      drawerData = window.DRAWER_DATA || [];

  function cabinetChange(event) {
    var selectedOption = cabinetSelect.find('option:selected').val(),
        drawers = [];
    if(!selectedOption) { return; }

    if(selectedOption.slice(0, 4) === 'cab_') {
      drawers = drawerData.byCabinetId[selectedOption.slice(4)] || [];
    }

    drawerSelect.attr('disabled', drawers.length === 0);
    drawerSelect.children().detach();
    $.each(drawerData.byCabinetId[selectedOption.slice(4)]||[], function(k, v) {
      drawerSelect.append($('<option>').attr('value', v.id).text(v.label));
    });
  }

  cabinetSelect.change(cabinetChange);
  cabinetChange();
});
