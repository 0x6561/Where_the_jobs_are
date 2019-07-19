// use jQuery to add css for map
$('head').append('<link rel="stylesheet" type="text/css" href="map.css">');

var margin = {
  top: 10,
  bottom: 10,
  left: 10,
  right:10
}
  , width = parseInt(d3.select('.viz').style('width'))
  , width = width - margin.left - margin.right
  , mapRatio = .5
  , height = width * mapRatio
  , active = d3.select(null);

// Define the div for the tooltip
var div = d3.select(".viz").append("div")	
  .attr("class", "tooltip")				
  .style("opacity", 0);

var svg = d3.select('.viz').append('svg')
  .attr('class', 'center-container')
  .attr('height', height + margin.top + margin.bottom)
  .attr('width', width + margin.left + margin.right);

svg.append('rect')
  .attr('class', 'background center-container')
  .attr('height', height + margin.top + margin.bottom)
  .attr('width', width + margin.left + margin.right)
//.on('click', clicked);

var map = d3.json('us-counties.topojson');
var cities = d3.csv('offer_list.csv');

Promise.all([map, cities])
  .then(ready);

var projection = d3.geoAlbersUsa()
  .translate([width /2 , height / 2])
  .scale(width);

var path = d3.geoPath()
  .projection(projection);

var g = svg.append("g")
  .attr('class', 'center-container center-items us-state')
//.attr('transform', 'translate('+margin.left+','+margin.top+')')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)

function ready(data) {
  var us = data[0];
  var cities = data[1];
  //console.log(cities);

  /*// counties
          g.append("g")
          .attr("id", "counties")
          .selectAll("path")
          .data(topojson.feature(us, us.objects.counties).features)
          .enter().append("path")
          .attr("d", path)
          .attr("class", "county-boundary")
          .on("click", reset);
          */

  // states
  g.append("g")
    .attr("id", "states")
    .selectAll("path")
    .data(topojson.feature(us, us.objects.states).features)
    .enter().append("path")
    .attr("d", path)
    .attr("class", "state")
  //.on("click", clicked);

  // state borders
  g.append("path")
    .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
    .attr("id", "state-borders")
    .attr("d", path);

  // draw points
  svg.selectAll("circle")
    .data(cities)
    .enter()
    .append("circle")
    .attr("class","circles")
    .attr("cx", function(d) {
      // this function returns pixel coords
      var longitude = d.longitude;
      var latitude = d.latitude;
      var pxCoords = projection([longitude, latitude]);
      return projection([longitude, latitude])[0];
    })
    .attr("cy", function(d) { 
      var longitude = d.longitude;
      var latitude = d.latitude;
      return projection([longitude, latitude])[1];
    })
    .attr("r", function(d){return d.count+"px";})
  //.attr("r","3px")
    .attr("stroke", "white")
    .attr("fill", "red")
    .style("opacity", .8)
    .on("mouseover", function(d) {		
      div.transition()		
        .duration(200)		
        .style("opacity", 1)
      div.html(d.location + "<br/>")	
        .style("left", (d3.event.pageX) + "px")		
        .style("top", (d3.event.pageY - 28) + "px")})
    .on("mouseout", function(d) {		
      div.transition()		
        .duration(500)		
        .style("opacity", 0)})

}

function clicked(d) {
  if (d3.select('.background').node() === this) return reset();

  if (active.node() === this) return reset();

  active.classed("active", false);
  active = d3.select(this).classed("active", true);

  var bounds = path.bounds(d),
    dx = bounds[1][0] - bounds[0][0],
    dy = bounds[1][1] - bounds[0][1],
    x = (bounds[0][0] + bounds[1][0]) / 2,
    y = (bounds[0][1] + bounds[1][1]) / 2,
    scale = .9 / Math.max(dx / width, dy / height),
    translate = [width / 2 - scale * x, height / 2 - scale * y];

  g.transition()
    .duration(750)
    .style("stroke-width", 1.5 / scale + "px")
    .attr("transform", "translate(" + translate + ")scale(" + scale + ")");
}

function reset() {
  active.classed("active", false);
  active = d3.select(null);

  g.transition()
    .delay(100)
    .duration(750)
    .style("stroke-width", "1.5px")
    .attr('transform', 'translate('+margin.left+','+margin.top+')');
}
