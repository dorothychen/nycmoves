

function updateColorsDest(pickup_zone) {
    d3.json('static/dest_zones_2016.json', function(err, data) {
        if (err) return console.log(err);

        svg.selectAll("path")
            .attr("fill", function(p) { return idToColor(p, data[pickup_zone], 0.001); } );

        // assign "selected" class to correct element
        var selected = svgElement.getElementsByClassName("selected");
        for (var i = 0; i < selected.length; i++) {
            selected[i].classList.remove("selected");
        }
        var element = svgElement.getElementById("id-" + pickup_zone);
        element.classList.add("selected");
    });
}