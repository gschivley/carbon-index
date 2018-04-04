// This is a rough version based on the index plot. Need to clean it up.


(function () {
    // var data_url = 'http://localhost:8000/annual_index_website.csv';
    var data_url = '//s3.amazonaws.com/org-emissionsindex/js/test/annual_index_website.csv';
    var d3_ae = Plotly.d3;
    var WIDTH_IN_PERCENT_OF_PARENT = 100,
        HEIGHT_IN_PERCENT_OF_PARENT = 100;//100;//95;
    var gd_ae = document.getElementById('myDiv_annual_co2');
    var gd3_ae = d3_ae.select("div#myDiv_annual_co2")
        .style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            // 'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

            // When height is given as 'vh' the plot won't resize vertically.
            height: HEIGHT_IN_PERCENT_OF_PARENT + '%', //'vh',

            'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) + '%'//'vh'
            // 'margin-top': 45 + 'px'
            // 'margin-top': 5 + 'vh'
        });

    var my_Div_ae = gd3_ae.node();


    var icon_ae = {
        'width': 1792,
        'path': 'M448,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S448,174.7,448,192z M192,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S192,174.7,192,192z M64,416V96c0-26.7,9.3-49.3,28-68s41.3-28,68-28l1472,0c26.7,0,49.3,9.3,68,28s28,41.3,28,68v320c0,26.7-9.3,49.3-28,68s-41.3,28-68,28h-465l-135-136c-38.7-37.3-84-56-136-56s-97.3,18.7-136,56L624,512H160c-26.7,0-49.3-9.3-68-28S64,442.7,64,416z M389,985c-11.3-27.3-6.7-50.7,14-70l448-448c12-12.7,27-19,45-19s33,6.3,45,19l448,448c20.7,19.3,25.3,42.7,14,70c-11.3,26-31,39-59,39h-256v448c0,17.3-6.3,32.3-19,45c-12.7,12.7-27.7,19-45,19H768c-17.3,0-32.3-6.3-45-19s-19-27.7-19-45v-448H448C420,1024,400.3,1011,389,985z',
        'ascent': 1642,
        'descent': -150
    };

    // 2005 baseline in SI units
    var emissions_2005 = 2429.59
    // Multiply to convert kg to lbs
    var kg_to_lb = 2.2046


    var frame1_ae = {
        "yaxis": {
            "separatethousands": true,
            "title": "Million Metric Tonnes",
            "showgrid": false,
            "rangemode": "tozero",
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005,
                "y0": emissions_2005,
                "x0": 0,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.8,
                "y0": emissions_2005 * 0.8,
                "x0": 0.5,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.6,
                "y0": emissions_2005 * 0.6,
                "x0": 0.75,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.2,
                "y0": emissions_2005 * 0.2,
                "x0": 0.95,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            }
        ],
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
                "opacity": 1,
                "yanchor": "middle",
                "xref": "paper",
                "xanchor": "right",
                "yref": "paper",
                "sizex": 0.5,
                "sizey": 0.12,
                "source": "//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png",
                "y": -0.03,
                "x": -0.03
            }
        ],
        "font": {
            "size": 10
        },
        "margin": {
            "l": 70,//80,
            "t": 10,
            "r": 30,
            "b": 30//50
        },
        "annotations": [
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "2005 Annual Level",
                "y": emissions_2005,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 20%",
                "y": emissions_2005 * 0.8,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 40%",
                "y": emissions_2005 * 0.6,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 80%",
                "y": emissions_2005 * 0.2,
                "x": 0.94,
                "showarrow": false
            },
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "center",
                "yref": "paper",
                "text": "EmissionsIndex.org",
                "y": 0,
                "x": 0.5,
                "showarrow": false
            }
        ],
        // "updatemenus": update_menu
    };

    var frame2_ae = {
        "yaxis": {
            "separatethousands": true,
            "title": "Million Metric Tonnes",
            "showgrid": false,
            "rangemode": "tozero",
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005,
                "y0": emissions_2005,
                "x0": 0,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.8,
                "y0": emissions_2005 * 0.8,
                "x0": 0.5,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.6,
                "y0": emissions_2005 * 0.6,
                "x0": 0.75,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.2,
                "y0": emissions_2005 * 0.2,
                "x0": 0.95,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            }
        ],
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
                "opacity": 1,
                "yanchor": "middle",
                "xref": "paper",
                "xanchor": "right",
                "yref": "paper",
                "sizex": 0.5,
                "sizey": 0.12,
                "source": "//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png",
                "y": -0.03,
                "x": -0.03
            }
        ],
        "font": {
            "size": 13
        },
        "margin": {
            "l": 115,
            "t": 20,
            "r": 30,
            "b": 50,//80
            "pad": 5
        },
        "annotations": [
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "2005 Annual Level",
                "y": emissions_2005,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "20% Below 2005",
                "y": emissions_2005 * 0.8,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "40% Below 2005",
                "y": emissions_2005 * 0.6,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "80% Below 2005",
                "y": emissions_2005 * 0.2,
                "x": 0.94,
                "showarrow": false
            },
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "center",
                "yref": "paper",
                "text": "EmissionsIndex.org",
                "y": 0,
                "x": 0.5,
                "showarrow": false
            }
        ],
        // "updatemenus": update_menu
    };
    var frame3_ae = {
        "yaxis": {
            "separatethousands": true,
            "title": "Million Metric Tonnes",
            "showgrid": false,
            "rangemode": "tozero",
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005,
                "y0": emissions_2005,
                "x0": 0,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.8,
                "y0": emissions_2005 * 0.8,
                "x0": 0.5,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.6,
                "y0": emissions_2005 * 0.6,
                "x0": 0.75,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            },
            {
                "layer": "below",
                "xref": "paper",
                "y1": emissions_2005 * 0.2,
                "y0": emissions_2005 * 0.2,
                "x0": 0.95,
                "x1": 1,
                "type": "line",
                "line": {
                    "color": "#919296",
                    "width": 1
                }
            }
        ],
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
                "opacity": 1,
                "yanchor": "middle",
                "xref": "paper",
                "xanchor": "right",
                "yref": "paper",
                "sizex": 0.5,
                "sizey": 0.12,
                "source": "//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png",
                "y": -0.03,
                "x": -0.03
            }
        ],
        "font": {
            "size": 13
        },
        "margin": {
            "l": 150,
            "t": 20,
            "r": 30,
            "b": 60,//80
            "pad": 5
        },
        "annotations": [
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "2005 Annual Level",
                "y": emissions_2005,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "20% Below 2005",
                "y": emissions_2005 * 0.8,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "40% Below 2005",
                "y": emissions_2005 * 0.6,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "80% Below 2005",
                "y": emissions_2005 * 0.2,
                "x": 0.94,
                "showarrow": false
            },
            {
                "yanchor": "bottom",
                "xref": "paper",
                "xanchor": "center",
                "yref": "paper",
                "text": "EmissionsIndex.org",
                "y": 0,
                "x": 0.5,
                "showarrow": false
            }
        ],
        // "updatemenus": update_menu
    };

    //Options for the modebar buttons
    var plot_options_ae = {
        scrollZoom: false, // lets us scroll to zoom in and out - works
        showLink: false, // removes the link to edit on plotly - works
        modeBarButtonsToRemove: ['autoScale2d', 'select2d', 'zoom2d', 'pan2d',
            'hoverCompareCartesian', 'zoomOut2d', //'zoomIn2d',
            'hoverClosestCartesian', 'sendDataToCloud'],
        //modeBarButtonsToAdd: ['lasso2d'],
        modeBarButtonsToAdd: [{
            name: 'Download data',
            icon: icon_ae,
            click: function (gd_ae) {
                window.location.href = 'https://github.com/EmissionsIndex/Emissions-Index/raw/master/Calculated%20values/2017/2017%20Q4%20US%20Power%20Sector%20CO2%20Emissions%20Intensity.xlsx';
            }
        }],
        displaylogo: false,
        displayModeBar: 'hover', //this one does work
        fillFrame: false
    };

    //Check initial window width to determine appropriate layout
    var initial_width_ae = window.innerWidth;

    var aspect_ratio = 7.0 / 5.0;


    var get = function (data, column) {
        return data.map(function (x) {
            return x[column];
        });
    };

    d3_ae.csv(data_url, function (error, data) {
        if (error) {
            console.log(error);
        } else {
            // var imperial_text_ae = get(data, 'Imperial hovertext');
            var text_ae = get(data, 'Emissions hovertext');

            var years = get(data, 'year');
            var co2 = get(data, 'final co2 (million mt)');
            // var si_ys = get(data, 'index (g/kWh)');
            var data_ae = [
                {
                    "hoverinfo": "text+x",
                    "visible": true,
                    "text": text_ae,
                    "y": co2,
                    "x": years,
                    "line": {
                        "shape": "spline",
                        "smoothing": 0.6,
                        "width": 2
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                // {
                //     // "hoverinfo": "text+x",
                //     "visible": false,
                //     // "text": si_text_ae,
                //     "y": si_ys,
                //     "x": years,
                //     "line": {
                //         "shape": "spline",
                //         "smoothing": 0.8,
                //         "width": 2
                //     },
                //     "type": "scatter",
                //     "mode": "lines"
                // }
            ];
        };


        if (initial_width_ae < 500) {
            var layout1_ae = frame1_ae
            layout1_ae.height = (initial_width_ae - 32) / aspect_ratio;
            data_ae[0].line.width = 1.5;


            Plotly.plot('myDiv_annual_co2',
                data_ae,
                layout1_ae,
                plot_options_ae)
        } else if (initial_width_ae <= 767) {
            var layout2_ae = frame2_ae
            layout2_ae.height = (initial_width_ae - 32) / aspect_ratio


            Plotly.plot('myDiv_annual_co2',
                data_ae,
                layout2_ae,
                plot_options_ae)
        } else if (initial_width_ae <= 1023) {
            var layout3_ae = frame3_ae
            layout3_ae.height = (initial_width_ae - 32) / aspect_ratio

            // left pad of 150 is reasonable at 1023, but too much at 768
            var percent_extra_pad_ae = (1023 - initial_width_ae) / (1023 - 768)
            layout3_ae.margin.l = 150 - 40 * percent_extra_pad_ae;


            Plotly.plot('myDiv_annual_co2',
                data_ae,
                layout3_ae,
                plot_options_ae)
        } else if (initial_width_ae <= 1279) {
            var layout2_ae = frame2_ae
            layout2_ae.height = (initial_width_ae - 418) / aspect_ratio


            Plotly.plot('myDiv_annual_co2',
                data_ae,
                layout2_ae,
                plot_options_ae)
        } else {
            var layout2_ae = frame2_ae
            layout2_ae.height = 752 / aspect_ratio


            Plotly.plot('myDiv_annual_co2',
                data_ae,
                layout2_ae,
                plot_options_ae)
        };

        // Array of the 3 frames, so that they can be looped through
        frames_ae = [frame1_ae, frame2_ae, frame3_ae];

        // // Function to change layout values touched by the updatemenu to SI
        // function si_layout_function(frame) {
        //     frame.yaxis.title = "US Power Sector<br>kg CO<sub>2</sub>/MWh";
        //     frame.yaxis.range = [0, 725.75];
        //     frame.shapes[0].y0 = emissions_2005;
        //     frame.shapes[0].y1 = emissions_2005;
        //     frame.annotations[0].y = emissions_2005;
        //     frame.shapes[1].y0 = emissions_2005 * 0.8;
        //     frame.shapes[1].y1 = emissions_2005 * 0.8;
        //     frame.annotations[1].y = emissions_2005 * 0.8;
        //     frame.shapes[2].y0 = emissions_2005 * 0.6;
        //     frame.shapes[2].y1 = emissions_2005 * 0.6;
        //     frame.annotations[2].y = emissions_2005 * 0.6;
        //     frame.shapes[3].y0 = emissions_2005 * 0.2;
        //     frame.shapes[3].y1 = emissions_2005 * 0.2;
        //     frame.annotations[3].y = emissions_2005 * 0.2
        // };
        //
        // // Function to change layout values touched by the updatemenu to Imperial
        // function imperial_layout_function(frame) {
        //     frame.yaxis.title = "US Power Sector<br>Pounds CO<sub>2</sub>/MWh";
        //     frame.yaxis.range = [0, 1600];
        //     frame.shapes[0].y0 = emissions_2005;
        //     frame.shapes[0].y1 = emissions_2005;
        //     frame.annotations[0].y = emissions_2005;
        //     frame.shapes[1].y0 = emissions_2005 * 0.8;
        //     frame.shapes[1].y1 = emissions_2005 * 0.8;
        //     frame.annotations[1].y = emissions_2005 * 0.8;
        //     frame.shapes[2].y0 = emissions_2005 * 0.6;
        //     frame.shapes[2].y1 = emissions_2005 * 0.6;
        //     frame.annotations[2].y = emissions_2005 * 0.6;
        //     frame.shapes[3].y0 = emissions_2005 * 0.2;
        //     frame.shapes[3].y1 = emissions_2005 * 0.2;
        //     frame.annotations[3].y = emissions_2005 * 0.2
        // };

        window.addEventListener('resize', function () {
            //This can probably be changed to bounding box width at some point in case page layout changes
            var window_width_ae = window.innerWidth;

            // Find the current y-axis title
            // If the title contains "kg", change the layout to SI
            // If not, change to imperial
            // var y_label_ae = my_Div_ae.layout.yaxis.title;
            // if (y_label_ae.indexOf("kg") >= 0) {
            //     frames_ae.forEach(si_layout_function);
            //     my_Div_ae.layout.updatemenus.active = -1
            // } else {
            //     frames_ae.forEach(imperial_layout_function);
            //     my_Div_ae.layout.updatemenus.active = 0
            // };

            //for some reason the left pad gets stuck at the frame3 or frame1 size when the plot starts in frame2. Manually setting it here works.
            if (window_width_ae < 500) {

                Plotly.relayout('myDiv_annual_co2',
                    frame1_ae);
            } else if (window_width_ae <= 767) {
                frame2_ae.margin.l = 110;

                // add updatemenus back
                // frame2_ae.updatemenus = update_menu;
                Plotly.relayout('myDiv_annual_co2',
                    frame2_ae);
            } else if (window_width_ae <= 1023) {
                // left pad of 150 is reasonable at 1023, but too much at 768
                var percent_extra_pad_ae = (1023 - window_width_ae) / (1023 - 768)
                frame3_ae.margin.l = 150 - (40 * percent_extra_pad_ae)

                // add updatemenus back
                // frame3_ae.updatemenus = update_menu;
                Plotly.relayout('myDiv_annual_co2',
                    frame3_ae);
            } else if (window_width_ae <= 1279) {

                //adjust the margin down here?
                frame2_ae.margin.l = 110;

                // add updatemenus back
                // frame2_ae.updatemenus = update_menu;
                Plotly.relayout('myDiv_annual_co2',
                    frame2_ae);
            } else {
                frame2_ae.margin.l = 110;

                // add updatemenus back
                // frame2_ae.updatemenus = update_menu;
                Plotly.relayout('myDiv_annual_co2',
                    frame2_ae);
            };

            Plotly.Plots.resize(my_Div_ae);

        });
    });
})();
