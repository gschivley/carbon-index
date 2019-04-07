(function () {
    var data_url = '//s3.amazonaws.com/org-emissionsindex/js/Index-Chart/quarterly_index_website.csv';
    var d3_qi = Plotly.d3;
    var WIDTH_IN_PERCENT_OF_PARENT = 100;
    var HEIGHT_IN_PERCENT_OF_PARENT = 100;//100;//95;
    var gd_qi = document.getElementById('myDiv_quarter_index');
    var gd3_qi = d3_qi.select("div[id='myDiv_quarter_index']")
        .style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            // 'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

            // When height is given as 'vh' the plot won't resize vertically.
            height: HEIGHT_IN_PERCENT_OF_PARENT + '%', //'vh',

            'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) + '%'//'vh'
            //'margin-top': 45 + 'px'
            //     'margin-top': 5 + 'vh'
        });
    // 2005 baseline in SI units
    var index_2005 = 599
    // Multiply to convert kg to lbs
    var kg_to_lb = 2.2046

    var my_Div_qi = gd3_qi.node();

    // Helpers
    var get = function (data, column) {
        return data.map(function (x) {
            return x[column];
        });
    };

    // var zip = function (xs, ys) {
    //     return xs.map(function (x, i) {
    //         return [x, ys[i]];
    //     });
    // }
    //
    // var zipmap = function (func, xs, ys) {
    //     return zip(xs, ys).map(function (xy) { return func(xy[0], xy[1]); });
    // };

    var update_menu = [
        {
            borderwidth: 0,
            type: "dropdown",
            // direction: "right",
            x: 0.05,
            y: 1.05,
            xanchor: "left",
            yanchor: "auto",
            buttons: [
                {
                    method: 'update',
                    args: [
                        { visible: [true, false] },
                        {
                            "yaxis.title": "US Power Sector<br>Pounds CO<sub>2</sub>/MWh",
                            "yaxis.range": [0, 1600],
                            "shapes[0].y0": index_2005 * kg_to_lb,
                            "shapes[0].y1": index_2005 * kg_to_lb,
                            "annotations[0].y": index_2005 * kg_to_lb,
                            "shapes[1].y0": index_2005 * 0.8 * kg_to_lb,
                            "shapes[1].y1": index_2005 * 0.8 * kg_to_lb,
                            "annotations[1].y": index_2005 * 0.8 * kg_to_lb,
                            "shapes[2].y0": index_2005 * 0.6 * kg_to_lb,
                            "shapes[2].y1": index_2005 * 0.6 * kg_to_lb,
                            "annotations[2].y": index_2005 * 0.6 * kg_to_lb,
                            "shapes[3].y0": index_2005 * 0.2 * kg_to_lb,
                            "shapes[3].y1": index_2005 * 0.2 * kg_to_lb,
                            "annotations[3].y": index_2005 * 0.2 * kg_to_lb
                        }
                    ],
                    label: 'lb/MWh'

                },
                {
                    method: 'update',
                    args: [
                        { visible: [false, true] },
                        {
                            "yaxis.title": "US Power Sector<br>kg CO<sub>2</sub>/MWh",
                            "yaxis.range": [0, 725.75],
                            "shapes[0].y0": index_2005,
                            "shapes[0].y1": index_2005,
                            "annotations[0].y": index_2005,
                            "shapes[1].y0": index_2005 * 0.8,
                            "shapes[1].y1": index_2005 * 0.8,
                            "annotations[1].y": index_2005 * 0.8,
                            "shapes[2].y0": index_2005 * 0.6,
                            "shapes[2].y1": index_2005 * 0.6,
                            "annotations[2].y": index_2005 * 0.6,
                            "shapes[3].y0": index_2005 * 0.2,
                            "shapes[3].y1": index_2005 * 0.2,
                            "annotations[3].y": index_2005 * 0.2
                        }
                    ],
                    label: 'kg/MWh'
                }
            ]
        }
    ]

    frame1_qi = {
        "yaxis": {
            "separatethousands": true,
            "title": "US Power Sector<br>Pounds CO<sub>2</sub>/MWh",
            "showgrid": false,
            "range": [
                0,
                1600
            ],
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": index_2005 * kg_to_lb,
                "y0": index_2005 * kg_to_lb,
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
                "y1": index_2005 * 0.8 * kg_to_lb,
                "y0": index_2005 * 0.8 * kg_to_lb,
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
                "y1": index_2005 * 0.6 * kg_to_lb,
                "y0": index_2005 * 0.6 * kg_to_lb,
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
                "y1": index_2005 * 0.2 * kg_to_lb,
                "y0": index_2005 * 0.2 * kg_to_lb,
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
            "tickangle": 25,
            "dtick": 8,
            "showgrid": false,
            "fixedrange": false,
            "type": "category",
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
                "y": index_2005 * kg_to_lb,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 20%",
                "y": index_2005 * 0.8 * kg_to_lb,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 40%",
                "y": index_2005 * 0.6 * kg_to_lb,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "↓ 80%",
                "y": index_2005 * 0.2 * kg_to_lb,
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
        "updatemenus": update_menu
    }
    frame2_qi = {
        "yaxis": {
            "separatethousands": true,
            "title": "US Power Sector<br>Pounds CO<sub>2</sub>/MWh",
            "showgrid": false,
            "range": [
                0,
                1600
            ],
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": index_2005 * kg_to_lb,
                "y0": index_2005 * kg_to_lb,
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
                "y1": index_2005 * 0.8 * kg_to_lb,
                "y0": index_2005 * 0.8 * kg_to_lb,
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
                "y1": index_2005 * 0.6 * kg_to_lb,
                "y0": index_2005 * 0.6 * kg_to_lb,
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
                "y1": index_2005 * 0.2 * kg_to_lb,
                "y0": index_2005 * 0.2 * kg_to_lb,
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
            "tickangle": 25,
            "dtick": 8,
            "showgrid": false,
            "fixedrange": false,
            "type": "category",
            "autorange": true
        },
        "images": [
            // {
            //     "opacity": 1,
            //     "yanchor": "middle",
            //     "xref": "paper",
            //     "xanchor": "right",
            //     "yref": "paper",
            //     "sizex": 0.5,
            //     "sizey": 0.12,
            //     "source": "//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png",
            //     "y": -0.03,
            //     "x": -0.03
            // }
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
                "y": index_2005 * kg_to_lb,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "20% Below 2005",
                "y": index_2005 * 0.8 * kg_to_lb,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "40% Below 2005",
                "y": index_2005 * 0.6 * kg_to_lb,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "80% Below 2005",
                "y": index_2005 * 0.2 * kg_to_lb,
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
        "updatemenus": update_menu
    }
    frame3_qi = {
        "yaxis": {
            "separatethousands": true,
            "title": "US Power Sector<br>Pounds CO<sub>2</sub>/MWh",
            "showgrid": false,
            "range": [
                0,
                1600
            ],
            "fixedrange": true,
            "type": "linear"
        },
        "shapes": [
            {
                "layer": "below",
                "xref": "paper",
                "y1": index_2005 * kg_to_lb,
                "y0": index_2005 * kg_to_lb,
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
                "y1": index_2005 * 0.8 * kg_to_lb,
                "y0": index_2005 * 0.8 * kg_to_lb,
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
                "y1": index_2005 * 0.6 * kg_to_lb,
                "y0": index_2005 * 0.6 * kg_to_lb,
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
                "y1": index_2005 * 0.2 * kg_to_lb,
                "y0": index_2005 * 0.2 * kg_to_lb,
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
            "tickangle": 25,
            "dtick": 8,
            "showgrid": false,
            "fixedrange": false,
            "type": "category",
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
                "y": index_2005 * kg_to_lb,
                "x": 1,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "20% Below 2005",
                "y": index_2005 * 0.8 * kg_to_lb,
                "x": 0.49,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "40% Below 2005",
                "y": index_2005 * 0.6 * kg_to_lb,
                "x": 0.74,
                "showarrow": false
            },
            {
                "xref": "paper",
                "xanchor": "right",
                "yref": "y",
                "text": "80% Below 2005",
                "y": index_2005 * 0.2 * kg_to_lb,
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
        "updatemenus": update_menu
    }


    var icon_qi = {
        'width': 1792,
        'path': 'M448,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S448,174.7,448,192z M192,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S192,174.7,192,192z M64,416V96c0-26.7,9.3-49.3,28-68s41.3-28,68-28l1472,0c26.7,0,49.3,9.3,68,28s28,41.3,28,68v320c0,26.7-9.3,49.3-28,68s-41.3,28-68,28h-465l-135-136c-38.7-37.3-84-56-136-56s-97.3,18.7-136,56L624,512H160c-26.7,0-49.3-9.3-68-28S64,442.7,64,416z M389,985c-11.3-27.3-6.7-50.7,14-70l448-448c12-12.7,27-19,45-19s33,6.3,45,19l448,448c20.7,19.3,25.3,42.7,14,70c-11.3,26-31,39-59,39h-256v448c0,17.3-6.3,32.3-19,45c-12.7,12.7-27.7,19-45,19H768c-17.3,0-32.3-6.3-45-19s-19-27.7-19-45v-448H448C420,1024,400.3,1011,389,985z',
        'ascent': 1642,
        'descent': -150
    };

    //Options for the modebar buttons
    var plot_options_qi = {
        scrollZoom: false, // lets us scroll to zoom in and out - works
        showLink: false, // removes the link to edit on plotly - works
        modeBarButtonsToRemove: ['autoScale2d', 'select2d', 'zoom2d', 'pan2d',
            'hoverCompareCartesian', 'zoomOut2d', //'zoomIn2d',
            'hoverClosestCartesian', 'sendDataToCloud'],
        //modeBarButtonsToAdd: ['lasso2d'],
        modeBarButtonsToAdd: [{
            name: 'Download data',
            icon: icon_qi,
            click: function () {
                window.location.href = 'https://github.com/EmissionsIndex/Emissions-Index/raw/master/Calculated%20values/2018/2018%20Q4%20US%20Power%20Sector%20CO2%20Emissions%20Intensity.xlsx';
            }
        }],
        displaylogo: false,
        displayModeBar: 'hover', //this one does work
        fillFrame: false
    };

    //Check initial window width to determine appropriate layout
    var initial_width_qi = window.innerWidth;

    var aspect_ratio = 7.0 / 5.0;

    d3_qi.csv(data_url, function (error, data) {
        if (error) {
            console.log(error);
        } else {
            // var quarters = zipmap(function (year, quarter) {
            //     return year + ' Q' + quarter;
            // }, get(data, 'year'), get(data, 'quarter'));
            var data_qi = [
                {
                    "uid": "f0db50",
                    "ysrc": "schivlg:87:75240c",
                    "hoverinfo": "text+x",
                    "xsrc": "schivlg:87:ca81d3",
                    "textsrc": "schivlg:87:27ca70",
                    "text": get(data, 'Imperial hovertext'),
                    visible: true,
                    "y": get(data, 'index (lb/mwh)'),
                    "x": get(data, 'year_quarter'),
                    "line": {
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "uid": "f0db50",
                    "ysrc": "schivlg:87:75240c",
                    "hoverinfo": "text+x",
                    "xsrc": "schivlg:87:ca81d3",
                    "textsrc": "schivlg:87:27ca70",
                    "text": get(data, 'SI hovertext'),
                    visible: false,
                    "y": get(data, 'index (g/kwh)'),
                    "x": get(data, 'year_quarter'),
                    "line": {
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                }
            ]
            if (initial_width_qi < 500) {
                var layout1_qi = frame1_qi
                layout1_qi.height = (initial_width_qi - 32) / aspect_ratio;
                data_qi[0].line.width = 1.5;

                Plotly.plot('myDiv_quarter_index',
                    data_qi,
                    layout1_qi,
                    plot_options_qi)
            } else if (initial_width_qi <= 767) {
                var layout2_qi = frame2_qi
                layout2_qi.height = (initial_width_qi - 32) / aspect_ratio

                Plotly.plot('myDiv_quarter_index',
                    data_qi,
                    layout2_qi,
                    plot_options_qi)
            } else if (initial_width_qi <= 1023) { //Would be nice to have a break around 900px where the plot gets really wide
                var layout3_qi = frame3_qi
                layout3_qi.height = (initial_width_qi - 32) / aspect_ratio

                // left pad of 150 is reasonable at 1023, but too much at 768
                var percent_extra_pad_qi = (1023 - initial_width_qi) / (1023 - 768)
                layout3_qi.margin.l -= 40 * percent_extra_pad_qi

                Plotly.plot('myDiv_quarter_index',
                    data_qi,
                    layout3_qi,
                    plot_options_qi)
            } else if (initial_width_qi <= 1279) {
                var layout2_qi = frame2_qi
                layout2_qi.height = (initial_width_qi - 418) / aspect_ratio
                Plotly.plot('myDiv_quarter_index',
                    data_qi,
                    layout2_qi,
                    plot_options_qi)
            } else {
                var layout2_qi = frame2_qi
                layout2_qi.height = 752 / aspect_ratio
                Plotly.plot('myDiv_quarter_index',
                    data_qi,
                    layout2_qi,
                    plot_options_qi)
            };

        }
    });

    // Array of the 3 frames, so that they can be looped through
    frames_qi = [frame1_qi, frame2_qi, frame3_qi];

    // Function to change layout values touched by the updatemenu to SI
    function si_layout_function(frame) {
        frame.yaxis.title = "US Power Sector<br>kg CO<sub>2</sub>/MWh";
        frame.yaxis.range = [0, 725.75];
        frame.shapes[0].y0 = index_2005;
        frame.shapes[0].y1 = index_2005;
        frame.annotations[0].y = index_2005;
        frame.shapes[1].y0 = index_2005 * 0.8;
        frame.shapes[1].y1 = index_2005 * 0.8;
        frame.annotations[1].y = index_2005 * 0.8;
        frame.shapes[2].y0 = index_2005 * 0.6;
        frame.shapes[2].y1 = index_2005 * 0.6;
        frame.annotations[2].y = index_2005 * 0.6;
        frame.shapes[3].y0 = index_2005 * 0.2;
        frame.shapes[3].y1 = index_2005 * 0.2;
        frame.annotations[3].y = index_2005 * 0.2
    };

    // Function to change layout values touched by the updatemenu to Imperial
    function imperial_layout_function(frame) {
        frame.yaxis.title = "US Power Sector<br>Pounds CO<sub>2</sub>/MWh";
        frame.yaxis.range = [0, 1600];
        frame.shapes[0].y0 = index_2005 * kg_to_lb;
        frame.shapes[0].y1 = index_2005 * kg_to_lb;
        frame.annotations[0].y = index_2005 * kg_to_lb;
        frame.shapes[1].y0 = index_2005 * 0.8 * kg_to_lb;
        frame.shapes[1].y1 = index_2005 * 0.8 * kg_to_lb;
        frame.annotations[1].y = index_2005 * 0.8 * kg_to_lb;
        frame.shapes[2].y0 = index_2005 * 0.6 * kg_to_lb;
        frame.shapes[2].y1 = index_2005 * 0.6 * kg_to_lb;
        frame.annotations[2].y = index_2005 * 0.6 * kg_to_lb;
        frame.shapes[3].y0 = index_2005 * 0.2 * kg_to_lb;
        frame.shapes[3].y1 = index_2005 * 0.2 * kg_to_lb;
        frame.annotations[3].y = index_2005 * 0.2 * kg_to_lb
    };

    window.addEventListener('resize', function () {
        //This can probably be changed to bounding box width at some point in case page layout changes
        var window_width_qi = window.innerWidth;

        // Find the current y-axis title
        // If the title contains "kg", change the layout to SI
        // If not, change to imperial
        var y_label_qi = my_Div_qi.layout.yaxis.title;
        if (y_label_qi.indexOf("kg") >= 0) {
            frames_qi.forEach(si_layout_function);
            my_Div_qi.layout.updatemenus.active = -1
        } else {
            frames_qi.forEach(imperial_layout_function);
            my_Div_qi.layout.updatemenus.active = 0
        };

        if (window_width_qi < 500) {
            frame1_qi.font.size = 10;
            Plotly.relayout('myDiv_quarter_index',
                frame1_qi);
        } else if (window_width_qi <= 767) {

            //could rescale the left margin in this section too..
            frame2_qi.margin.l = 110;
            Plotly.relayout('myDiv_quarter_index',
                frame2_qi);

        } else if (window_width_qi <= 1023) {
            // left pad of 150 is reasonable at 1023, but too much at 768
            var percent_extra_pad_qi = (1023 - window_width_qi) / (1023 - 768)
            frame3_qi.margin.l = 150 - (40 * percent_extra_pad_qi)
            Plotly.relayout('myDiv_quarter_index',
                frame3_qi);

        } else if (window_width_qi <= 1279) {

            //adjust the margin down here?
            frame2_qi.margin.l = 110;
            Plotly.relayout('myDiv_quarter_index',
                frame2_qi);

        } else {
            frame2_qi.margin.l = 110;
            Plotly.relayout('myDiv_quarter_index',
                frame2_qi);
        };

        Plotly.Plots.resize(my_Div_qi);

    });

})();
