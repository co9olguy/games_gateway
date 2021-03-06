
//player-range slider
$(function() {
    $( "#player-range" ).slider({
      range: true,
      min: 1,
      max: 15,
      values: [ 2, 8 ],
      slide: function( event, ui ) {
        $( "#player-amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
      },
      stop: function( event, ui ) {
            updatePlot();
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
      values: [ 0, 180 ],
      step: 15,
      stop: function( event, ui ) {
                $( "#time-check").prop("checked", true);
                updatePlot();
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
      values: [ 0 ],
      slide: function( event, ui ) {
        $( "#minage-amount" ).val( ui.values[ 0 ])
      },
      stop: function( event, ui ) {
            $( "#age-check").prop("checked", true);
            updatePlot();
            return true
      }
    });
    $( "#minage-amount" ).val( $( "#minage-slider" ).slider( "values", 0 ) );
});

//rank selector
$(function() {
    $( "#rank-slider" ).slider({
      min: 0,
      max: 10000,
      step: 100,
      values: [ 2000 ],
      slide: function( event, ui ) {
        $( "#rank-amount" ).val( ui.values[ 0 ])
      },
      stop: function( event, ui ) {
            $( "#rank-check").prop("checked", true);
            updatePlot();
            return true
      }
    });
    $( "#rank-amount" ).val( $( "#rank-slider" ).slider( "values", 0 ) );
});

//year-range selector
$(function() {
    $( "#year-range" ).slider({
      range: true,
      min: -3500,
      max: 2016,
      values: [ 1980, 2016 ],
      step: 1,
      stop: function( event, ui ) {
                $( "#year-check").prop("checked", true);
                updatePlot();
                return true},
      slide: function( event, ui ) {
        $( "#year-amount" ).val( ui.values[ 0 ] + " to " + ui.values[ 1 ] )
      }
    });
    $( "#year-amount" ).val( $( "#year-range" ).slider( "values", 0 ) +
      " to " + $( "#year-range" ).slider( "values", 1 ) );
});

// axis select-menus
$(function() {
    $( "#x-axis" ).selectmenu({
        select: function( event, ui ) {updatePlot()}
    });
    $( "#y-axis" ).selectmenu({
        select: function( event, ui ) {updatePlot()}
    });
});


// function to update bokeh plot
function updatePlot(){
      $( '#plot-container' ).empty().html('<img src="http://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif" style="float:left;">')
      // get data to feed to app
      $.getJSON(
      $SCRIPT_ROOT + '/_explore',
      { minplayers: $( "#player-range" ).slider( "values", 0 ),
        maxplayers: $( "#player-range" ).slider( "values", 1 ),
        minplaytime: $( "#time-range" ).slider( "values", 0 ),
        maxplaytime: $( "#time-range" ).slider( "values", 1 ),
        minage: $( "#minage-slider" ).slider( "values", 0 ),
        minyear: $( "#year-range" ).slider( "values", 0 ),
        maxyear: $( "#year-range" ).slider( "values", 1 ),
        rank: $( '#rank-slider' ).slider( "values", 0 ),
        xaxis: $( '#x-axis' ).val(),
        yaxis: $( '#y-axis' ).val(),
        useplayers: $( '#player-check:checked' ).val(),
        useplaytime: $( '#time-check:checked' ).val(),
        useage: $( '#age-check:checked' ).val()
      },

      //display returned data
      function( data ) {
        if ( data.flag == 0 ){
          var plot = data.plot;
          $( '#status-msg' ).empty()
          $( "#plot-container" ).empty().append(plot);
        }
        else {
          $( "#plot-container" ).empty().text( data.return_string );
        };
      });

}
$(document).ready(function(){
    updatePlot();
});