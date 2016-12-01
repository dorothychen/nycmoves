
/* read zone flow info and update the color gradients */
function updateColorsFlow() {
    d3.json('static/zones_2016-01-03.json', function(err, data) {
        if (err) return console.log(err);

        // what 2 do with da travel info
        curData = data["12:30"];
        if (curData == undefined) {
            console.log(data);
            return console.log("data undefined");
        }
        svg.selectAll("path")
            .attr("fill", function(p) { return idToColor(p, curData, 0.2); } );
    });
}