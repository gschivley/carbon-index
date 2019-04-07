$.getJSON('https://raw.githubusercontent.com/gschivley/random_files/master/NERCemissions2017.json', function(data) {

$.getJSON('https://raw.githubusercontent.com/gschivley/random_files/master/nerc_albers.geo.json', function (geojson) {

    // Initiate the chart
    Highcharts.mapChart('container', {
        credits: {
            text: 'EmissionsIndex.org',
            href: 'emissionsindex.org'
            // href: 'https://raw.githubusercontent.com/EmissionsIndex/Emissions-Index/master/GeoJSON-Files/NERC%20emissions%202017.csv'
        },
        chart: {
            map: geojson
        },

        title: {
            text: ''
        },

        mapNavigation: {
            enabled: false,
            buttonOptions: {
                verticalAlign: 'bottom'
            }
        },

        colorAxis: {
            tickPixelInterval: 100
        },

        series: [{
            data: data,
/*             data: {
            csvURL: 'https://raw.githubusercontent.com/gschivley/random_files/master/NERCemissions2017.csv',
                            enablePolling: false
                            }, */
            keys: ['NERCregion', 'value'],
            joinBy: 'NERCregion',
            name: 'Carbon index',
            tooltip: {
                pointFormat: '{point.NERCregion}: {point.value} kg/MWh'
            },
            // states: {
            //     hover: {
            //         color: '#a4edba'
            //     }
            // },
            dataLabels: {
                enabled: true,
                format: '{point.NERCregion}'
            }
                    }]
    }
    // function (chart) {
    //
    // chart.renderer.image('//s3.amazonaws.com/org-emissionsindex/content/CMU_wordmarks/CMU_Logo_Stack_Red.png', 40, 350, 78, 50).add();
    //  }
    );

});
});
