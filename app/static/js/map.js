// different zones
var ZONES = {
    "nta": {
        "filename": "zones_nta.geojson",
        "id": "ntacode",
        "name": "ntaname"
        },
    "taxi": {
        "filename": "zones_taxi.geojson",
        "id": "LocationID",
        "name": "zone"
        },
    "zipcode": {
        "filename": "zones_zipcode.geojson",
        "id": "ZIPCODE",
        "name": "PO_NAME"
        }
};

// chosen zone
var ZONE_TYPE = "taxi";
var ZONE_FILENAME = "static/" + ZONES[ZONE_TYPE]["filename"];
var ZONE_ID = ZONES[ZONE_TYPE]["id"];
var ZONE_NAME = ZONES[ZONE_TYPE]["name"];


// width of window
var width = window.innerWidth;

// height of window
var height = window.innerHeight;

// global dictionary of zone flow info for current time frame
var curData;

/* setup svg for map */
var svg = d3.select("body").append("svg")
    .attr("id", "map")
    .attr("width", width)
    .attr("height", height);

var svgElement = document.getElementById("map");

/* setup tooltip for info */
var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("z-index", "10")
    .style("visibility", "hidden");

/* make map from json zones file */
d3.json(ZONE_FILENAME, function(error, nyc) {
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
        .attr("id", function(d) { return "id-" + d['properties'][ZONE_ID]; })
        .attr("class", "zone")
        .attr("fill", "None") // hide at first
        .on("mouseover", borderMouseover)
        .on("mousemove", borderMousemove)
        .on("mouseout", borderMouseout)
        .on("click", zoneClick);

    updateColors();
});