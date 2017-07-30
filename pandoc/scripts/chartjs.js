var system = require('system');
var page = require('webpage').create();
var args = system.args;

page.onCallback = function(data)
{
    page.clipRect = data.clipRect;
    page.render(system.args[2]);
    phantom.exit();
};
page.includeJs('http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js', function()
{
    page.includeJs('https://www.google.com/jsapi', function()
    {
        page.evaluate(function(chartType, data_json)
        {
            var div = $('<div />').attr('id', 'chart').width(900).height(500).appendTo($('body'));
            google.load("visualization", "1",
            {
                packages:[chartType == 'GeoChart' ? 'geochart' : 'corechart'],
                callback: function()
                {
                    json_obj = $.parseJSON(data_json);
                    data_arr = json_obj.data;
                    data = google.visualization.arrayToDataTable(data_arr);
                    options = json_obj.options
                    chart = new google.visualization[chartType]($(div).get(0));
                    google.visualization.events.addListener(chart, 'ready', function()
                    {
                        window.callPhantom(
                        {
                            clipRect: $(div).get(0).getBoundingClientRect()
                        });
                    });
                    chart.draw(data, options);
                }
            });
        }, system.args[1], system.args[3]);
    });
});
