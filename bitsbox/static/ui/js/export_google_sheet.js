// OAuth2 scopes
var SCOPE = [
  'profile',
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.readonly'
].join(' ');

var DISCOVERY_DOCS = [
  'https://sheets.googleapis.com/$discovery/rest?version=v4'
];

// APIs we wish to load (colon separated)
var GAPI_APIS = 'client:auth2:picker';

// RegExp to extract spreadsheetId from URLs
var SPREADSHEED_ID_REGEXP = /^https:\/\/docs.google.com\/spreadsheets\/d\/([^\/]*)\//;

// Plumbing to convert onGapiLoad callback into a promise called gapiAvailable
// which is resolved once the gapi APIs are loaded and configured.
var resolveGapiPromise,
    gapiAvailable = new Promise(function(resolve) {
      resolveGapiPromise = resolve;
    }).then(function() {
      return Promise.resolve(gapi.client.init({
        apiKey: GOOGLE_API_KEY,
        clientId: GOOGLE_CLIENT_ID,
        discoveryDocs: DISCOVERY_DOCS,
        scope: SCOPE
      }));
    }).then(function() { return gapi; });

// Function called when gapi has loaded.
function onGapiLoad() {
  // Load all the apis and then resolve the gapiAvailable promise
  gapi.load(GAPI_APIS, function() { resolveGapiPromise(gapi); });
}

// Arrange for a function to be called when sign in status has changed
var registerAuthCallback = gapiAvailable.then(function() {
  var auth = gapi.auth2.getAuthInstance();
  auth.isSignedIn.listen(onSigninStatusChange);
  auth.currentUser.listen(onCurrentUserChange);

  onSigninStatusChange(auth.isSignedIn.get());
  onCurrentUserChange(auth.currentUser.get());
});

// Wire in buttons
var registerSignInButtonEvents = gapiAvailable.then(function() {
  $('#authorize-button').click(function() {
    gapi.auth2.getAuthInstance().signIn();
  });
  $('#signout-button').click(function() {
    gapi.auth2.getAuthInstance().signOut();
  });
});

// Called when sign in status changes
function onSigninStatusChange(isSignedIn) {
  // Toggle visibility of UI components
  if(isSignedIn) {
    $('.show-when-signed-in').removeClass('hidden').addClass('show');
    $('.show-when-signed-out').removeClass('show').addClass('hidden');
  } else {
    $('.show-when-signed-in').removeClass('show').addClass('hidden');
    $('.show-when-signed-out').removeClass('hidden').addClass('show');
  }
}

// Called when the current user has changed
function onCurrentUserChange(user) {
  var authResponse, oauthToken;

  if(!user) { return; }
  authResponse = user.getAuthResponse();
  if(!authResponse || !authResponse.access_token) { return; }
  oauthToken = authResponse.access_token;

  gapiAvailable.then(function() {
    // Wire up buttons
    $('#export-existing-sheet').click(function() {
      // Function to call when picker has information
      function pickerCallback(data) {
        var documents, doc, match, spreadsheetId,
            Response = google.picker.Response,
            Action = google.picker.Action,
            Document = google.picker.Document;

        // Ignore everything except "picked"
        if(data[Response.ACTION] !== Action.PICKED) { return; }

        // Get documents selected by user
        documents = data[Response.DOCUMENTS];
        if(documents.length !== 1) { return; }
        doc = documents[0];

        if(doc[Document.MIME_TYPE] !== 'application/vnd.google-apps.spreadsheet') {
          console.error('User did not select a spreadsheet');
          return;
        }

        // The user picked a spreadsheet
        match = SPREADSHEED_ID_REGEXP.exec(doc[Document.URL]);
        if(!match) {
          console.warning('Document URL did not match regex:', doc[Document.URL]);
        }
        spreadsheetId = match[1];

        // Wire up onclick handler
        $('#overwrite-confirm').click(function() {
          $('#confirm-modal').modal('hide');
          exportToSpreadsheet(spreadsheetId);
        });

        // Show modal.
        $('.overwrite-name').text(doc[Document.NAME]);
        $('#confirm-modal').modal('show');
      }

      // Show a picker
      var picker = new google.picker.PickerBuilder().
        addView(google.picker.ViewId.SPREADSHEETS).
        //setOrigin(window.location.protocol + '//' + window.location.host).
        setOAuthToken(oauthToken).
        setDeveloperKey(GOOGLE_API_KEY).
        setCallback(pickerCallback).
        build();
      picker.setVisible(true);
    });
  });
}

// Called when a spreadsheet should be overwritten
function exportToSpreadsheet(spreadsheetId) {
  gapi.client.sheets.spreadsheets.get({
    spreadsheetId: spreadsheetId
  }).then(function(response) {
    console.log(response);
  });
}

// Toggle display of loading/on load content
Promise.all([
  registerAuthCallback, registerSignInButtonEvents
]).then(function() {
  $('.hidden-on-load').removeClass('show').addClass('hidden');
  $('.shown-on-load').removeClass('hidden').addClass('show');
});
