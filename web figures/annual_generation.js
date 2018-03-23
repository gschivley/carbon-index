(function () {
    var data_url = '//s3.amazonaws.com/org-emissionsindex/js/annual_gen_website.csv';
    var d3_ag = Plotly.d3;
    var WIDTH_IN_PERCENT_OF_PARENT = 100,
        HEIGHT_IN_PERCENT_OF_PARENT = 95;
    var gd = document.getElementById('myDiv_annual_generation');
    // var bb_load = gd.getBoundingClientRect();
    var gd3_ag = d3_ag.select("div[id='myDiv_annual_generation']")
        .style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            //     'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

            // When height is given as 'vh' the plot won't resize vertically.
            height: HEIGHT_IN_PERCENT_OF_PARENT + '%', //'vh',

            'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) + '%'//'vh'
            //     'margin-top': 5 + 'vh'
        });

    var my_Div_ag = gd3_ag.node();

    var currentYear = (new Date()).getFullYear();

    frame1_ag = {
        "autosize": true,
        "yaxis": {
            "separatethousands": true,
            "title": "US Generation<br>Million MWh",
            "showgrid": true,
            "fixedrange": true,
            "type": "linear",
            "rangemode": "tozero",
            "autorange": true
        },
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
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
            "l": 70,//110,
            "t": 10,
            "r": 30,
            "b": 45//50
        },
        "legend": {
            "orientation": "h",
            "y": -0.3,
            "tracegroupgap": 0,
            "font": { "size": 8 }
        }
    };
    frame2_ag = {
        "yaxis": {
            "separatethousands": true,
            "title": "US Generation<br>Million MWh",
            "showgrid": true,
            "fixedrange": true,
            "type": "linear",
            "rangemode": "tozero",
            "autorange": true
        },
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
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
            "l": 110,
            "t": 10,
            "r": 30,
            "b": 50,
            "pad": 5
        },
        "legend": {
            "orientation": "h",
            "y": -0.15,
            "font": { "size": 12 }
        }
    };
    frame3_ag = {
        "yaxis": {
            "separatethousands": true,
            "title": "US Generation<br>Million MWh",
            "showgrid": true,
            "fixedrange": true,
            "type": "linear",
            "rangemode": "tozero",
            "autorange": true
        },
        "xaxis": {
            "showgrid": false,
            "fixedrange": false,
            "autorange": true
        },
        "images": [
            {
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
            "t": 10,
            "r": 30,
            "b": 50,
            "pad": 5
        },
        "legend": {
            "orientation": "h",
            //"y": -0.15,
            "font": { "size": 12 }
        },
    };

    var icon = {
        'width': 1792,
        'path': 'M448,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S448,174.7,448,192z M192,192c0,17.3,6.3,32.3,19,45s27.7,19,45,19s32.3-6.3,45-19s19-27.7,19-45s-6.3-32.3-19-45s-27.7-19-45-19s-32.3,6.3-45,19S192,174.7,192,192z M64,416V96c0-26.7,9.3-49.3,28-68s41.3-28,68-28l1472,0c26.7,0,49.3,9.3,68,28s28,41.3,28,68v320c0,26.7-9.3,49.3-28,68s-41.3,28-68,28h-465l-135-136c-38.7-37.3-84-56-136-56s-97.3,18.7-136,56L624,512H160c-26.7,0-49.3-9.3-68-28S64,442.7,64,416z M389,985c-11.3-27.3-6.7-50.7,14-70l448-448c12-12.7,27-19,45-19s33,6.3,45,19l448,448c20.7,19.3,25.3,42.7,14,70c-11.3,26-31,39-59,39h-256v448c0,17.3-6.3,32.3-19,45c-12.7,12.7-27.7,19-45,19H768c-17.3,0-32.3-6.3-45-19s-19-27.7-19-45v-448H448C420,1024,400.3,1011,389,985z',
        'ascent': 1642,
        'descent': -150
    };

    //Options for the modebar buttons
    var plot_options_ag = {
        scrollZoom: false, // lets us scroll to zoom in and out - works
        showLink: false, // removes the link to edit on plotly - works
        modeBarButtonsToRemove: ['pan2d', 'autoScale2d', 'select2d', 'zoom2d',
            'zoomOut2d', 'sendDataToCloud'], //'zoomIn2d',
        //modeBarButtonsToAdd: ['lasso2d'],
        modeBarButtonsToAdd: [{
            name: 'Download data',
            icon: icon,
            click: function (gd) {
                window.location.href = 'https://github.com/EmissionsIndex/Emissions-Index/raw/master/Calculated%20values/2017/2017%20Q2%20US%20Generation%20By%20Fuel%20Type.xlsx';
            }
        }],
        displaylogo: false,
        displayModeBar: 'hover', //this one does work
        fillFrame: false
    };

    //Check initial window width to determine appropriate layout
    var initial_width_ag = window.innerWidth;

    var aspect_ratio = 7.0 / 5.0;

    var get = function (data, column) {
        return data.map(function (x) {
            return x[column];
        })
    };

    var filter = function (data, column, value) {
        return data.filter(function (x) {
            return x[column] === value;
        })
    };

    var zip = function (xs, ys) {
        return xs.map(function (x, i) {
            return [x, ys[i]];
        });
    }

    var zipmap = function (func, xs, ys) {
        return zip(xs, ys).map(function (xy) { return func(xy[0], xy[1]); });
    };

    var unique = function (array) {
        return array.filter(function (value, index, self) {
            return self.indexOf(value) === index;
        });
    };

    d3_ag.csv(data_url, function (error, data) {
        if (error) {
            console.log(error);
        } else {

            var grouped_data = {};
            ['Coal', 'Natural Gas', 'Nuclear', 'Wind',
            'Solar', 'Hydro', 'Other Renewables', 'Other', 'Total'].forEach(
                function (group) {
                    grouped_data[group] = filter(data, 'fuel category', group);
                }
            );
            var years = unique(get(data, 'year'));

            var numberFormat = { minimumFractionDigits: 1, maximumFractionDigits: 1 };

            var data_ag = [
                {
                    "hoverinfo": "text+x+name",
                    "name": "Total",
                    "text": get(grouped_data['Total'], 'hovertext'),
                    "y": get(grouped_data['Total'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#101010",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Coal",
                    "text": get(grouped_data['Coal'], 'hovertext'),
                    "y": get(grouped_data['Coal'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#8c564b",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Natural Gas",
                    "text": get(grouped_data['Natural Gas'], 'hovertext'),
                    "y": get(grouped_data['Natural Gas'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#17becf",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Nuclear",
                    "text": get(grouped_data['Nuclear'], 'hovertext'),
                    "y": get(grouped_data['Nuclear'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#ff7f0e",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Hydro",
                    "text": get(grouped_data['Hydro'], 'hovertext'),
                    "y": get(grouped_data['Hydro'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#1f77b4",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Wind",
                    "text": get(grouped_data['Wind'], 'hovertext'),
                    "y": get(grouped_data['Wind'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#2ca02c",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Solar",
                    "text": get(grouped_data['Solar'], 'hovertext'),
                    "y": get(grouped_data['Solar'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#bcbd22",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Other",
                    "text": get(grouped_data['Other'], 'hovertext'),
                    "y": get(grouped_data['Other'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#9467bd",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                },
                {
                    "hoverinfo": "text+x+name",
                    "name": "Other Renewables",
                    "text": get(grouped_data['Other Renewables'], 'hovertext'),
                    "y": get(grouped_data['Other Renewables'], 'generation (M MWh)'),
                    "x": quarters,
                    "line": {
                        "color": "#7f7f7f",
                        "shape": "spline",
                        "smoothing": 0.6
                    },
                    "type": "scatter",
                    "mode": "lines"
                }
            ];

            if (initial_width_ag < 500) {
                var layout1_ag = frame1_ag
                layout1_ag.height = (initial_width_ag - 32) / aspect_ratio

                var arrayLength = data_ag.length;
                for (var i = 0; i < arrayLength; i++) {
                    data_ag[i].line.width = 1.5;
                };

                Plotly.plot('myDiv_annual_generation',
                    data_ag,
                    layout1_ag,
                    plot_options_ag)
            } else if (initial_width_ag <= 767) {
                var layout2_ag = frame2_ag
                layout2_ag.height = (initial_width_ag - 32) / aspect_ratio

                Plotly.plot('myDiv_annual_generation',
                    data_ag,
                    layout2_ag,
                    plot_options_ag)
            } else if (initial_width_ag <= 1023) { //Would be nice to have a break around 900px where the plot gets really wide
                var layout3_ag = frame3_ag
                layout3_ag.height = (initial_width_ag - 32) / aspect_ratio

                // left pad of 150 is reasonable at 1023, but too much at 768
                var percent_extra_pad_ag = (1023 - initial_width_ag) / (1023 - 768)
                layout3_ag.margin.l -= 40 * percent_extra_pad_ag

                Plotly.plot('myDiv_annual_generation',
                    data_ag,
                    layout3_ag,
                    plot_options_ag)
            } else if (initial_width_ag <= 1279) {
                var layout2_ag = frame2_ag
                layout2_ag.height = (initial_width_ag - 418) / aspect_ratio
                Plotly.plot('myDiv_annual_generation',
                    data_ag,
                    layout2_ag,
                    plot_options_ag)
            } else {
                var layout2_ag = frame2_ag
                layout2_ag.height = 752 / aspect_ratio
                Plotly.plot('myDiv_annual_generation',
                    data_ag,
                    layout2_ag,
                    plot_options_ag)
            };
        }
    })

    window.addEventListener('resize', function () {

        var window_width_ag = window.innerWidth;

        if (window_width_ag < 500) {
            Plotly.relayout('myDiv_annual_generation',
                frame1_ag);
            // console.log('Frame1');
            // console.log(frame1_ag.margin.l);
        } else if (window_width_ag <= 767) {
            frame2_ag.margin.l = 110;
            Plotly.relayout('myDiv_annual_generation',
                frame2_ag);
            // console.log('Frame2');
            // console.log(frame2_ag.margin.l);
        } else if (window_width_ag <= 1023) {
            // left pad of 150 is reasonable at 1023, but too much at 768
            var percent_extra_pad_ag = (1023 - window_width_ag) / (1023.0 - 768.0)
            frame3_ag.margin.l = 150 - (40 * percent_extra_pad_ag)
            Plotly.relayout('myDiv_annual_generation',
                frame3_ag);
            // console.log('Frame3');
            // console.log(frame3_ag.margin.l);
        } else if (window_width_ag <= 1279) {

            frame2_ag.margin.l = 110;
            //legend placement would be better if it shrank as window size went up here
            frame2_ag.legend.y = -0.15
            Plotly.relayout('myDiv_annual_generation',
                frame2_ag);
            // console.log('Frame2');
            // console.log(frame2_ag.margin.l);
        } else {
            frame2_ag.margin.l = 110;
            Plotly.relayout('myDiv_annual_generation',
                frame2_ag);
            // console.log('Frame2');
            // console.log(frame2_ag.margin.l);
        };

        Plotly.Plots.resize(my_Div_ag);
    });

})();
