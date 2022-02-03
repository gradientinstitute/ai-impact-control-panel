// Modified from Radar Chart design by Nadieh Bremer
// https://gist.github.com/nbremer/21746a9668ffdf6d8242

import * as d3 from "d3";
import _ from "lodash";

export function DrawRadarChart(id, data, svg) {

  /* SET UP RADAR CHART */
  const cfg = getConfiguration();
  const axes = data[0].map((x) => x.axis);
  const maxVal = 100;
  const radius = Math.min(cfg.w / 2, cfg.h / 2);
  const angleSlice = (Math.PI * 2) / axes.length;
  const radiusScale = d3.scaleLinear().range([0, radius]).domain([0, maxVal]);

  /* BASE CHART */
  initialiseRadarSVG(svg, cfg, id);
  const g = initialiseGElement(svg, cfg);
  addGlowFilter(g);
  const axisGrid = g.append("g").attr("class", "axisWrapper");
  drawBackgroundCircles(axisGrid, cfg, radius);
  const axis = drawRadialLines(axisGrid, axes, radiusScale, maxVal, angleSlice);
  appendAxisLabels(axis, cfg, radiusScale, maxVal, angleSlice);
  
  /* VISUALISE DATA */
  const radarLine = getRadarLine(cfg, radiusScale, angleSlice);
  const blobWrapper = createBlobWrapper(g, data);
  appendBlobBackgrounds(blobWrapper, radarLine, cfg);
  createBlobOutlines(blobWrapper, radarLine, cfg);
  appendBlobCircles(blobWrapper, cfg, radiusScale, angleSlice);

  /* TOOLS FOR INTERPRETING CHART*/
  appendLegend(svg, cfg, data);
  const blobCircleWrapper = getBlobCircleWrapper(g, data);
  const tooltip = setupHoverTooltip(g);
  appendInvisibleCircles(blobCircleWrapper, cfg, radiusScale, angleSlice, tooltip);
}

function getConfiguration() {
  const margin = { top: 100, right: 100, bottom: 100, left: 100 };
  const width = Math.min(700, window.innerWidth - 10) - margin.left - margin.right;
  const height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);
  const color = ["#CC333F", "#00A0B0", "#739CC4"];
  
  const defaultConfig = {
    // circle
    w: width,
    h: height,
    margin: margin,
    levels: 5,
    maxValue: 0.5,
    minValue: 0,

    // labels
    labelFactor: 1.25,
    wrapWidth: 60, 

    // blobs
    opacityArea: 0.35,
    opacityCircles: 0.1,
    strokeWidth: 2,
    roundStrokes: false,
    color: color,
    dotRadius: 3,
  };
  return defaultConfig;
}
  
////////////////////// BASE CHART /////////////////////////////////

function initialiseRadarSVG(svg, cfg, id) {
  svg.selectAll("*").remove();
  svg.attr("width", cfg.w + cfg.margin.left + cfg.margin.right)
    .attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
    .attr("class", "radar" + id);
}

function initialiseGElement(svg, cfg) {
  const x = (cfg.w / 2 + cfg.margin.left);
  const y = (cfg.h / 2 + cfg.margin.top);
  return svg.append("g").attr("transform", "translate(" + x + "," + y +")");
}

function addGlowFilter(g) {
  const filter = g.append("defs").append("filter").attr("id", "glow");
  filter.append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");
  const feMerge = filter.append("feMerge");
  feMerge.append("feMergeNode").attr("in", "coloredBlur");
  feMerge.append("feMergeNode").attr("in", "SourceGraphic");
}
  
function drawBackgroundCircles(axisGrid, cfg, radius) {
  axisGrid
    .selectAll(".levels")
    .data(d3.range(1, cfg.levels + 1).reverse())
    .enter()
    .append("circle")
    .attr("class", "gridCircle")
    .attr("r", (d) => (radius / cfg.levels) * d)
    .style("fill", "#CDCDCD")
    .style("stroke", "#CDCDCD")
    .style("fill-opacity", cfg.opacityCircles)
    .style("filter", "url(#glow)");
}

function drawRadialLines(axisGrid, axes, radiusScale, maxValue, angleSlice) {
  // spokes from the center 
  const axis = axisGrid
    .selectAll(".axis")
    .data(axes)
    .enter()
    .append("g")
    .attr("class", "axis");
  
  // appending the lines
  axis
    .append("line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", (_, i) => 
      radiusScale(maxValue * 1.1) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("y2", (_, i) => 
      radiusScale(maxValue * 1.1) * Math.sin(angleSlice * i - Math.PI / 2))
    .attr("class", "line")
    .style("stroke", "white")
    .style("stroke-width", "2px");

  return axis;
}

function appendAxisLabels(axis, cfg, radiusScale, maxValue, angleSlice) {
  axis
    .append("text")
    .attr("class", "legend")
    .style("font-size", "11px")
    .style("fill", "white")
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .attr("x", (_, i) => 
      radiusScale(maxValue * cfg.labelFactor) *
      Math.cos(angleSlice * i - Math.PI / 2))
    .attr("y", (_, i) =>
      radiusScale(maxValue * cfg.labelFactor) *
      Math.sin(angleSlice * i - Math.PI / 2))
    .text((d) => d)
    .call(wrap, cfg.wrapWidth);
}

////////////////////// VISUALISE DATA /////////////////////////////////

function getRadarLine(cfg, radiusScale, angleSlice) {
  const radarLine = d3.lineRadial().curve(d3.curveLinearClosed)
  .radius((d) => radiusScale(d.value))
  .angle((_, i) => i * angleSlice);
  if (cfg.roundStrokes) {
    radarLine.curve(d3.curveCardinalClosed);
  }
  return radarLine;
}

function createBlobWrapper(g, data) {
  return g
    .selectAll(".radarWrapper")
    .data(data)
    .enter()
    .append("g")
    .attr("class", "radarWrapper");
}

function appendBlobBackgrounds(blobWrapper, radarLine, cfg) {
  blobWrapper
    .append("path")
    .attr("class", "radarArea")
    .attr("d", (d) => radarLine(d))
    .style("fill", (_, i) => cfg.color[i])
    .style("fill-opacity", cfg.opacityArea)
    .on("mouseover", () => dimSelectBlobs(this))
    .on("mouseout", () => undimAllBlobs(cfg));
}

// Dim blobs hat are not hovered over
function dimSelectBlobs(x) {
  d3.selectAll(".radarArea")
    .transition()
    .duration(200)
    .style("fill-opacity", 0.1);
  d3.select(x)
    .transition()
    .duration(200)
    .style("fill-opacity", 0.7);
}

function undimAllBlobs(cfg) {
  d3.selectAll(".radarArea")
  .transition()
  .duration(200)
  .style("fill-opacity", cfg.opacityArea);
}

function createBlobOutlines(blobWrapper, radarLine, cfg) {
  blobWrapper
    .append("path")
    .attr("class", "radarStroke")
    .attr("d", (d) => radarLine(d))
    .style("stroke-width", cfg.strokeWidth + "px")
    .style("stroke", (_, i) => cfg.color[i])
    .style("fill", "none")
    .style("filter", "url(#glow)");
}
  
function appendBlobCircles(blobWrapper, cfg, radiusScale, angleSlice) {
  blobWrapper
  .selectAll(".radarCircle")
  .data((d, i) => d)
  .enter()
  .append("circle")
  .attr("class", "radarCircle")
  .attr("r", cfg.dotRadius)
  .attr("cx", (d, i) => radiusScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2))
  .attr("cy", (d, i) => radiusScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2))
  .style("fill", "black")
  .style("fill-opacity", 0.8);
}

/////////////////// TOOLS FOR INTERPRETING CHART //////////////////////////////
  
// wrapper for invisible circles above plot points
function getBlobCircleWrapper(g, data) {
  return g
    .selectAll(".radarCircleWrapper")
    .data(data)
    .enter()
    .append("g")
    .attr("class", "radarCircleWrapper");
}

// append a set of invisible circles on top for the mouseover pop-up
function appendInvisibleCircles(blobCircleWrapper, cfg, radiusScale, angleSlice, tooltip) {
  blobCircleWrapper
    .selectAll(".radarInvisibleCircle")
    .data((d) => d)
    .enter()
    .append("circle")
    .attr("class", "radarInvisibleCircle")
    .attr("r", cfg.dotRadius * 1.5)
    .attr("cx", (d, i) => radiusScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2))
    .attr("cy", (d, i) => radiusScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2))
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("mouseover", (_, i) => {
      // display the actual value of the data point
      let newX = parseFloat(d3.select(this).attr("cx")) - 10;
      let newY = parseFloat(d3.select(this).attr("cy")) - 10;
      tooltip
        .attr("x", newX)
        .attr("y", newY)
        .text(i.actualValue)
        .transition()
        .duration(200)
        .style("opacity", 1)
        .style("fill", "white");
    })
    .on("mouseout", () => tooltip.transition().duration(200).style("opacity", 0));
}


// set up the small tooltip for when you hover over a circle
function setupHoverTooltip(g) {
  return g
    .append("text")
    .attr("class", "tooltip")
}
  
// creates a legend based on the supplied candidates
function appendLegend(svg, cfg, data) {
  for (const x in data) {
    const i = parseInt(x);
    svg
      .append("circle")
      .attr("cx", 100)
      .attr("cy", 30 * (i + 1))
      .attr("r", 6)
      .style("fill", cfg.color[i])
      
    svg
      .append("text")
      .attr("x", 120)
      .attr("y", 30 * (i + 1))
      .text(data[i].map((val) => val.legend).find(x => x))
      .style("font-size", "15px")
      .style("fill", "white")
      .attr("alignment-baseline","middle")
  }
}

// Helper function to wrap SVG text to fit on multiple lines
// http://bl.ocks.org/mbostock/7555321
function wrap(text, width) {
  text.each(function () {
    var text = d3.select(this),
      words = text.text().split(/\s+/).reverse(), 
      word,
      line = [],
      lineNumber = 0,
      lineHeight = 1.4, // ems
      y = text.attr("y"),
      x = text.attr("x"),
      dy = parseFloat(text.attr("dy")),
      tspan = text
        .text(null)
        .append("tspan")
        .attr("x", x)
        .attr("y", y)
        .attr("dy", dy + "em");

    while ((word = words.pop())) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text
          .append("tspan")
          .attr("x", x)
          .attr("y", y)
          .attr("dy", ++lineNumber * lineHeight + dy + "em")
          .text(word);
      }
    }
  });
}
