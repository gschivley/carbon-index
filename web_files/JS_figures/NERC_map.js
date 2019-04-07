$.getJSON('https://raw.githubusercontent.com/gschivley/random_files/master/NERCemissions.json', function(data) {

$.getJSON('https://raw.githubusercontent.com/gschivley/random_files/master/nerc_albers.geo.json', function (geojson) {

    // Initiate the chart
    Highcharts.mapChart('container', {
        credits: {
            text: 'EmissionsIndex.org',
            href: 'emissionsindex.org'
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
            keys: ['nerc', 'value'],
            joinBy: ['NERCregion', 'nerc'],
            name: 'Carbon index',
            tooltip: {
                pointFormat: '{point.nerc}: {point.value} kg/MWh'
            },
            dataLabels: {
                enabled: true,
                format: '{point.nerc}'
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
