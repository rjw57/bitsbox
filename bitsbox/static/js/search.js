// Generic type-to-search functionality
$(document).ready(function() {
  $('[data-role="search"]').each(function(idx, elem) {
    var input = $(elem), list = $($(elem).data('target')), searchElems;
    searchElems = $(list).find('[data-search-text]');

    function runSearch() {
      var newVal = input.val().trim().toLowerCase(), searchTerms;

      // make sure all items in list are visible by default
      searchElems.removeClass('hidden');

      // that's all if there's no input
      if(!newVal || (newVal === '')) { return; }

      searchTerms = newVal.split(/\s+/);

      // otherwise, filter each element so that it must match all of the search
      // terms.
      searchElems.not(function(idx, listElem) {
        var matchText = $(listElem).data('search-text').toLowerCase();
        return searchTerms.reduce(function(accum, val) {
          return accum && (matchText.indexOf(val) !== -1);
        }, true);
      }).addClass('hidden');
    }

    input.on('change input', runSearch);

    // handle initial value
    runSearch();
  });
});
