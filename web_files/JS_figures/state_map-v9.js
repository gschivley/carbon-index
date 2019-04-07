// JavaScript source code

(function () {

    //var d3_mi = Plotly.d3;
    var WIDTH_IN_PERCENT_OF_PARENT = 100,
        HEIGHT_IN_PERCENT_OF_PARENT = 100;
    var gd_mi = document.getElementById('myDiv');
    // var bb_load = gd.getBoundingClientRect();
    var gd3_mi = Plotly.d3.select("div[id='myDiv']")
        .style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            // 'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

            // When height is given as 'vh' the plot won't resize vertically.
            height: HEIGHT_IN_PERCENT_OF_PARENT + '%', //'vh',

            'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) + '%'//'vh'//
            // 'margin-top': 5 + 'vh'
        });

   var my_Div = gd3_mi.node();

   var steps = [];
   var n = 17
   for (var i = 0; i < n; i++) {
       steps.push({
           label: (2001 + i).toString(),
           method: "animate",
           args: [[(2001 + i).toString()], {
               mode: "immediate",
               transition: { duration: 300 },
               frame: { duration: 300, "redraw": false }
           }]
       });
   }

   function makelayout(x) {
       var aspect_ratio = 7.0 / 5.0
       var window_width_mi = [500, 767, 1023, 1279]
       var font = [10, 13, 13, 13, 13]
       var height = [(x - 32), (x - 32), (x - 32), (x - 418), 752]
       var margin = [{
           "l": 70,//80
           "t": 30,
           "r": 30,
           "b": 30//50
       },
       {
           "l": 110,
           "t": 30,
           "r": 30,
           "b": 50,//80
           "pad": 5
       },
       {
           "l": (150 - 40 * ((1023 - x) / (1023 - 768))),
           "t": 30,
           "r": 30,
           "b": 60,//80
           "pad": 5
       },
       {
           "l": 110,
           "t": 30,
           "r": 30,
           "b": 50,//80
           "pad": 5
       },
       {
           "l": 110,
           "t": 30,
           "r": 30,
           "b": 50,//80
           "pad": 5
       }
       ]

       for (var i = 0; i < 5; i++) {
           var layout = {
               yaxis: {
                   fixedrange: true
               },
               xaxis: {
                   fixedrange: true
               },
               title: " ",
               geo: {
                   scope: 'usa',
                   //            countrycolor: 'rgb(255, 255, 255)',
                   //            showland: true,
                   //            landcolor: 'rgb(217, 217, 217)',
                   //            showlakes: true,
                   //            lakecolor: 'rgb(255, 255, 255)',
                   //            subunitcolor: 'rgb(255, 255, 255)',
                   //            lonaxis: { },
                   //            lataxis: { }
               },
               "images": [
                   {
                       "opacity": 1,
                       "yanchor": "middle",
                       "xref": "paper",
                       "xanchor": "left",
                       "yref": "paper",
                       "sizex": 0.5,
                       "sizey": 0.12,
                       "source": "//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png",
                       "y": -0.03,
                       "x": -0.03
                   }
               ],
               updatemenus: [{
                   x: 0.1,
                   y: 0,
                   yanchor: "top",
                   xanchor: "right",
                   showactive: false,
                   direction: "left",
                   type: "buttons",
                   pad: { "t": 87, "r": 10 },
                   buttons: [{
                       method: "animate",
                       args: [null, {
                           fromcurrent: true,
                           transition: {
                               duration: 200,
                           },
                           frame: {
                               duration: 500,
                               redraw: false
                           }
                       }],
                       label: "Play"
                   }, {
                       method: "animate",
                       args: [
                           [null],
                           {
                               mode: "immediate",
                               transition: {
                                   duration: 0
                               },
                               frame: {
                                   duration: 0,
                                   redraw: false
                               }
                           }
                       ],
                       label: "Pause"
                   }]
               }],
               //height: height[i] / 2.0,
               sliders: [{
                   active: 0,
                   steps: steps,
                   x: 0.1,
                   len: 0.9,
                   xanchor: "left",
                   y: 0,
                   yanchor: "top",
                   pad: { t: 50, b: 10 },
                   currentvalue: {
                       visible: true,
                       prefix: "Year:",
                       xanchor: "right",
                       font: {
                           size: font[i],
                           color: "#666"
                       }
                   },
                   transition: {
                       duration: 300,
                       easing: "cubic-in-out"
                   }
               }]
           };

           if (i <= 3) {
               if (x < window_width_mi[i]) {
                   layout.height = height[i] / aspect_ratio
                   layout.font = font[i]
                   layout.sliders[0].currentvalue.font.size = font[i]
                   layout.margin = margin[i]
                   var divdiv = "myDiv"
                   break;
               }
           }
           else {
               layout.height = height[i] / aspect_ratio
               layout.font = font[i]
               layout.sliders[0].currentvalue.font.size = font[i]
               layout.margin = margin[i]
               var divdiv = my_Div
           }



       }
       return [layout, divdiv]

   }


   var icon_mi = {
       'width': 1792,
       'path': 'M448,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S448,174.7,448,192z M192,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S192,174.7,192,192z M64,416V96c0-26.7,9.3-49.3,28-68s41.3-28,68-28l1472,0c26.7,0,49.3,9.3,68,28s28,41.3,28,68v320c0,26.7-9.3,49.3-28,68s-41.3,28-68,28h-465l-135-136c-38.7-37.3-84-56-136-56s-97.3,18.7-136,56L624,512H160c-26.7,0-49.3-9.3-68-28S64,442.7,64,416z M389,985c-11.3-27.3-6.7-50.7,14-70l448-448c12-12.7,27-19,45-19s33,6.3,45,19l448,448c20.7,19.3,25.3,42.7,14,70c-11.3,26-31,39-59,39h-256v448c0,17.3-6.3,32.3-19,45c-12.7,12.7-27.7,19-45,19H768c-17.3,0-32.3-6.3-45-19s-19-27.7-19-45v-448H448C420,1024,400.3,1011,389,985z',
       'ascent': 1642,
       'descent': -150
   };

   //Options for the modebar buttons
   var plot_options_mi = {
       scrollZoom: false, // lets us scroll to zoom in and out - works
       showLink: false, // removes the link to edit on plotly - works
       modeBarButtonsToRemove: ['pan2d', 'autoScale2d', 'select2d', 'zoom2d',
           'zoomOut2d', 'hoverCompareCartesian', //'zoomIn2d',
           'hoverClosestCartesian', 'sendDataToCloud', 'lasso2d', 'Zoom out', 'zoomInGeo', 'zoomOutGeo', 'resetGeo', 'resetScale2d','hoverClosestGeo'],
       //modeBarButtonsToAdd: ['lasso2d'],
       modeBarButtonsToAdd: [{
           name: 'Download data',
           icon: icon_mi,
           click: function (gd_mi) {
               window.location.href = 'https://raw.githubusercontent.com/EmissionsIndex/Emissions-Index/master/State%20Data/state_index_map_website.csv';
           }
       }],
       displaylogo: false,
       displayModeBar: 'hover', //this one does work
       fillFrame: false
   };



   var data_url = 'https://raw.githubusercontent.com/EmissionsIndex/Emissions-Index/master/State%20Data/state_index_map_website.csv';

   //var data_url = 'http://localhost:8000/state_index_map_2001-17.csv';
   Plotly.d3.csv(data_url, function (err, rows) {

       function unpack(rows, key) {
           return rows.map(function (row) { return row[key]; })
       }

       function fillArray(value, len) {
           var arr = [];
           for (var i = 0; i < len; i++) {
               arr.push(value);
           }
           return arr;
       }

       var frames = []
       var z = unpack(rows, 'indexlb')
       var locations = unpack(rows, 'state')
       console.log(locations)
       var n = 17;
       var j = 51;
       var k = 0;
       var num = 2000
       for (var i = 0; i < n; i++) {
           k++
           num++
           j = 50
           //        j = j * k
           frames[i] = { data: [{ z: [], locations: [] }], name: num }
           frames[i].data[0].z = z.slice(i * j, (i + 1) * j + 1);
           // Rounding the values
           frames[i].data[0].z = frames[i].data[0].z.map(function (each_element) {
               return Math.round(each_element);
           });

           frames[i].data[0].locations = locations.slice(0, j);
       }

       var data = [{
           type: 'choropleth',
           locationmode: 'USA-states',
           locations: frames[0].data[0].locations,
           z: frames[0].data[0].z,
           // text: frames[0].data[0].locations,
           text: fillArray("lb/MWh", 50),
           zauto: false,
           zmin: 0,
           zmax: 2800,
           colorscale: [
               [0, 'rgb(255, 233, 69)'], [0.2, 'rgb(202, 185, 105)'],
               [0.4, 'rgb(149, 143, 120)'], [0.6, 'rgb(102, 104, 112)'],
               [0.8, 'rgb(49, 68, 107)'], [1, 'rgb(0, 32, 76)']
           ],
           colorbar: {
             title: 'lb CO<sub>2</sub>/MWh',
             thickness: 0.04,
             thicknessmode: 'fraction'
               //thickness: 0.8
           },
           marker: {
               line: {
                   color: 'rgb(255,255,255)',
                   width: 1
               }
           }
       }];



       Plotly.plot(makelayout(window.innerWidth)[1], data, makelayout(window.innerWidth)[0], plot_options_mi).then(function () {
           Plotly.addFrames(makelayout(window.innerWidth)[1], frames);
       });
   })

   window.addEventListener('resize', function () {
       Plotly.relayout(makelayout(window.innerWidth)[1], makelayout(window.innerWidth)[0]);
       Plotly.Plots.resize(makelayout(window.innerWidth)[1]);
   });


})();
// JavaScript source code
