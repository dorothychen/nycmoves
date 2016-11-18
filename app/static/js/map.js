
// width of window
var width = window.innerWidth;

// height of window
var height = window.innerHeight;

// global dictionary of zone flow info for current time frame
var curData;

/* setup svg for map */
var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

/* setup tooltip for info */
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden");

/* make map from json zones file */
d3.json("static/zones2.json", function(error, nyc) {
    if (error) return console.log(error);

    // unit projection 
    // can also be d3.geoAlbersUsa
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
        .on("mousemove", borderMousemove)
        .on("mouseout", borderMouseout);

    updateColors();
});

/* logistic function to transport inflow/outflow counts into a normalized ratio 
    between 0 and 1.0
    https://en.wikipedia.org/wiki/Logistic_function
*/
function logistic(x) {
    var base = 1 + Math.pow(Math.E, -0.2*x);
    return 1 / base;
}

/*  given a zone feature object and a dictionary of zone codes => flow values,
    return color 
*/
var color_hot = [100,179,244];
var color_cold = [194,229,156];
function idToColor(p, vals) {
    var id = p['properties']['ntacode'];
    percent = logistic(vals[id]);

    rgb = color_hot.map(function(val, i) {
        var diff = percent * (color_hot[i]-color_cold[i]) + color_cold[i];
        return Math.round(diff);
    });

    return 'rgb(' + rgb.join() + ')';
}

/* read zone flow info and update the color gradients */
function updateColors() {
    d3.json('static/diffs_zones_2016-01-01.json', function(err, data) {
        if (err) return console.log(err);

        // what 2 do with da travel info
        curData = data['20:44'];
        svg.selectAll("path")
            .attr("fill", function(p) { return idToColor(p, curData); } );
    });
}

/* when you mouseover a zone */
function borderMouseover(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.add("hovered");

    var aggFlow = "";
    var name = "";
    if (curData) {
        var id = d['properties']['ntacode'];
        var name = d['properties']['ntaname'];
        var nameArr = name.split('-');
        if (nameArr[0] == "park") {
            name = nameArr[nameArr.length - 1] + " parks, cemeteries, etc.";
        }

        aggFlow = curData[id];
    }
    return tooltip.style("visibility", "visible")
        .html("<span class='name'>" + name + "</span><span class='agg-flow'>" + aggFlow + "</span>");
}

/* when you move your mouse */
function borderMousemove(d, i, paths) {
    return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
}

/* when you mouseout (leave) a zone */
function borderMouseout(d, i, paths) {
    var element = document.getElementById(this.id);
    element.classList.remove("hovered");

    return tooltip.style("visibility", "hidden");
}
