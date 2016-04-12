  //player-range slider
  $(function() {
    $( "#player-range" ).slider({
      range: true,
      min: 1,
      max: 15,
      values: [ 2, 4 ],
      slide: function( event, ui ) {
        $( "#player-amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
      },
      stop: function( event, ui ) {
            $( "#player-check").prop("checked", true);
            return true
      }
    });
    $( "#player-amount" ).val( $( "#player-range" ).slider( "values", 0 ) +
      " - " + $( "#player-range" ).slider( "values", 1 ) );
  });

  //time-range selector
  $(function() {
    $( "#time-range" ).slider({
      range: true,
      min: 0,
      max: 600,
      values: [ 30, 120 ],
      step: 15,
      stop: function( event, ui ) {
                                    $( "#time-check").prop("checked", true);
                                    return true},
      slide: function( event, ui ) {
        $( "#time-amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] )
      }
    });
    $( "#time-amount" ).val( $( "#time-range" ).slider( "values", 0 ) +
      " - " + $( "#time-range" ).slider( "values", 1 ) );
  });

  //minimum age selector
  $(function() {
    $( "#minage-slider" ).slider({
      min: 0,
      max: 18,
      values: [ 8 ],
      slide: function( event, ui ) {
        $( "#minage-amount" ).val( ui.values[ 0 ])
      },
      stop: function( event, ui ) {
            $( "#age-check").prop("checked", true);
            return true
      }
    });
    $( "#minage-amount" ).val( $( "#minage-slider" ).slider( "values", 0 ) );
  });

  //submit button
  $(function() {
    $( "#submit-button" ).click(function() {
      // get data to feed to app
      $.getJSON(
      $SCRIPT_ROOT + '/_recommend',
      { minplayers: $( "#player-range" ).slider( "values", 0 ),
        maxplayers: $( "#player-range" ).slider( "values", 1 ),
        minplaytime: $( "#time-range" ).slider( "values", 0 ),
        maxplaytime: $( "#time-range" ).slider( "values", 1 ),
        minage: $( "#minage-slider" ).slider( "values", 0 ),
        category: $( "#categories" ).val(),
        family: $( "#families" ).val(),
        useplayers: $( '#player-check:checked' ).val(),
        useplaytime: $( '#time-check:checked' ).val(),
        useage: $( '#age-check:checked' ).val(),
        usecategory: $( '#category-check:checked' ).val(),
        usefamily: $( '#family-check:checked' ).val()
      },

      //display returned data
      function( data ) {
        if ( data.flag == 0 ){
          var recs_html = data.recs_html;
          $( "#recs-container" ).empty().append(recs_html);
        }
        else {
          $( "#recs-container" ).empty().text( data.return_string );
        };
      });
      return false;
    });
  });
