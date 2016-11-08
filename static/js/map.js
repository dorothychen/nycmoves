var width = window.innerWidth;
var height = window.innerHeight;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);


// make map from zones.json
d3.json("static/zones2.json", function(error, nyc) {
    if (error) return console.log(error);

    // unit projection 
    var projection = d3.geoMercator()
        .scale("1")
        .translate([0, 0]);

    // set path
    var path = d3.geoPath().projection(projection);

    // compute bounds
    // http://stackoverflow.com/questions/14492284/center-a-map-in-d3-given-a-geojson-object
    var b = path.bounds(nyc),
        s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height),
        t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];

    projection.scale(s).translate(t)

    svg.selectAll("path")
        .data(nyc.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("id", function(d) { return d.properties.ntacode; })
        .attr("class", "border")
        .attr("fill", "None") // hide at first
        .on("mouseover", borderMouseover)
        .on("mouseout", borderMouseout);

    updateColors();
});

// https://en.wikipedia.org/wiki/Logistic_function
function logistic(x) {
    var base = 1 + Math.pow(Math.E, -0.3*x);
    return 1 / base;
}

/*  given a zone feature object and a dictionary of zone codes => flow values,
    return color 
*/
var color_hot = [229, 93, 135];
var color_cold = [95, 195, 228];
function idToColor(p, vals) {
    var id = p['properties']['ntacode'];
    percent = logistic(vals[id]);

    rgb = color_hot.map(function(val, i) {
        var diff = percent * (color_hot[i]-color_cold[i]) + color_cold[i];
        return Math.round(diff);
    });

    return 'rgb(' + rgb.join() + ')';
}

function updateColors() {
    d3.json('static/diffs_zones_2016-01-01.json', function(err, data) {
        if (err) return console.log(err);

        // what 2 do with da travel info
        vals = data['20:34'];
        svg.selectAll("path")
            .attr("fill", function(p) { return idToColor(p, vals); } );
    });
}

function borderMouseover(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.add("hovered");
}

function borderMouseout(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.remove("hovered");
}
