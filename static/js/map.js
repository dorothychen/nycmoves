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
    console.log(nyc.features.length);

    svg.selectAll("path")
        .data(nyc.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("id", function(d) { return d.properties.ntacode; })
        // .attr("id", function(d) { return "n-" + d.id; })
        .attr("class", "border")
        .on("mouseover", borderMouseover)
        .on("mouseout", borderMouseout);

    updateColors();
});

function updateColors() {
    // var paths = document.getElementsByTagName("path");
    // color_data = [];
    // for (var i = 0; i < paths.length; i += 1) {
    //     color_data.push(0);
    // }

    // svg.selectAll("path")
    //     .data(color_data)
    //     .style("fill", function(d) {
    //         return "red";
    //     });
}

function borderMouseover(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.add("hovered");
}

function borderMouseout(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.remove("hovered");
}
