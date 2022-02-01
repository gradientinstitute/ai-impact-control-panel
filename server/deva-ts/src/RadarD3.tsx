// Modified from Radar Chart design by Nadieh Bremer (VisualCinnamon.com)

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export function VisualiseData({metadata, leftValues, rightValues, leftName, rightName}) {
  const data = parseData({metadata, leftValues, rightValues});
  return RadarChart({data});   
}

// Returns data required by the Radar Chart in the right format
function parseData({metadata, leftValues, rightValues}) {
  let leftData = [];
  let rightData = []; 
  for (const [uid, x] of Object.entries(metadata.metrics)) {
    leftData.push({"axis" : uid, "value" : leftValues[uid]});    
    rightData.push({"axis" : uid, "value" : rightValues[uid]});
  }
  return [leftData, rightData];
}

function RadarChart({data}) {
  const svgRef = useRef();
  useEffect(() => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      drawChart(svg);
    }
  }, [svgRef]);

  const drawChart = (svg) => {
    DrawRadarChart(".radarChart", data, svg);
  };

  return (
    <div className="w-auto flex space-x-16">
      <div className="my-auto" style={{width:"20%"}}/>
      <div className="bg-gray-200">
        <svg className="radarChart" ref={svgRef}></svg>
      </div>
      <div className="my-auto" style={{width:"20%"}}/>
    </div>
  );
}

function DrawRadarChart(id, data, svg) {

  const cfg = getConfiguration();
  const width = cfg.w;
  const margin = cfg.margin;
  const maxValue = getMaxValue(cfg.maxValue, data);

  // names axes
  var allAxis = data[0].map((val) => val.axis);
  var total = allAxis.length;

  // outermost circle and formatting
  var radius = Math.min(cfg.w / 2, cfg.h / 2);
  var angleSlice = (Math.PI * 2) / total;
  var rScale = d3.scaleLinear().range([0, radius]).domain([0, maxValue]);

  /////////////// CREATE CONTAINER SVG AND G //////////////////
  initiateRadarSVG(svg, cfg, id);
  var g = initiategElement(svg, cfg);
  addGlowFilter(g);

  /////////////// DRAW THE CIRCULAR GRID /////////////////////
  var axisGrid = g.append("g").attr("class", "axisWrapper");
  drawBackgroundCircles(axisGrid, cfg, radius);
  addLevelLabels(axisGrid, cfg, radius, maxValue);

  ////////////////// DRAW THE AXES //////////////////////////
  var axis =  drawRadialLines(axisGrid, allAxis, rScale, maxValue, angleSlice);
  appendAxisLabels(axis, cfg, svg, rScale, maxValue, angleSlice, width, margin);
  
  ///////////// DRAW THE RADAR CHART BLOBS ////////////////
  var radarLine = getRadarLine(cfg, rScale, angleSlice);
  var blobWrapper = createBlobWrapper(g, data);
  appendBlobBackgrounds(blobWrapper, radarLine, cfg);
  createBlobOutlines(blobWrapper, radarLine, cfg);
  appendBlobCircles(blobWrapper, cfg, rScale, angleSlice);

  //////// APPEND INVISIBLE CIRCLES FOR TOOLTP ///////////
  var blobCircleWrapper = getBlobCircleWrapper(g, data);
  var tooltip = setupHoverTooltip(g);
  appendInvisibleCircles(blobCircleWrapper, cfg, rScale, angleSlice, tooltip);
}

// Helper function to wrap SVG text to fit on multiple lines
// Source: http://bl.ocks.org/mbostock/7555321
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

function getConfiguration() {

  const margin = { top: 100, right: 100, bottom: 100, left: 100 };
  const width = Math.min(700, window.innerWidth - 10) - margin.left - margin.right;
  const height = Math.min(width, window.innerHeight - margin.top - margin.bottom - 20);
  // const colour = d3.scaleBand().range(["#739CC4", "#CC333F", "#00A0B0"]);
  const color = ["#739CC4", "#CC333F", "#00A0B0"];
  const config = {
    // Circle
    w: width,
    h: height,
    margin: margin,
    levels: 5,
    maxValue: 0.5,

    // Labels
    labelFactor: 1.25,
    wrapWidth: 60, 

    // Blobs
    opacityArea: 0.35,
    opacityCircles: 0.1,
    strokeWidth: 2,
    roundStrokes: false,
    color: color,
    dotRadius: 4,
  };

  return config;
}

function getMaxValue(cfgMax, data) {
  const dataMax = d3.max(data, function (i) { 
    return d3.max(i.map(function (o) {
      return o.value;
    }));
  });
  return Math.max(cfgMax, dataMax);
}

function initiateRadarSVG(svg, cfg, id) {
  svg.selectAll("*").remove();
  svg
  .attr("width", cfg.w + cfg.margin.left + cfg.margin.right)
  .attr("height", cfg.h + cfg.margin.top + cfg.margin.bottom)
  .attr("class", "radar" + id);
}

function initiategElement(svg, cfg) {
  return svg
    .append("g")
    .attr(
      "transform",
      "translate(" +
        (cfg.w / 2 + cfg.margin.left) + "," + 
        (cfg.h / 2 + cfg.margin.top) +
      ")"
  );
}

function addGlowFilter(g) {
  var filter = g.append("defs").append("filter").attr("id", "glow");
  var feGaussianBlur = filter
    .append("feGaussianBlur")
    .attr("stdDeviation", "2.5")
    .attr("result", "coloredBlur");
  var feMerge = filter.append("feMerge");
  var feMergeNode_1 = feMerge.append("feMergeNode").attr("in", "coloredBlur");
  var feMergeNode_2 = feMerge.append("feMergeNode").attr("in", "SourceGraphic");
}

function drawBackgroundCircles(axisGrid, cfg, radius) {
  axisGrid
  .selectAll(".levels")
  .data(d3.range(1, cfg.levels + 1).reverse())
  .enter()
  .append("circle")
  .attr("class", "gridCircle")
  .attr("r", function (d, i) {
    return (radius / cfg.levels) * d;
  })
  .style("fill", "#CDCDCD")
  .style("stroke", "#CDCDCD")
  .style("fill-opacity", cfg.opacityCircles)
  .style("filter", "url(#glow)");
}

function addLevelLabels(axisGrid, cfg, radius, maxValue) {
  axisGrid
  .selectAll(".axisLabel")
  .data(d3.range(1, cfg.levels + 1).reverse())
  .enter()
  .append("text")
  .attr("class", "axisLabel")
  .attr("x", 4)
  .attr("y", function (d) {
    return (-d * radius) / cfg.levels;
  })
  .attr("dy", "0.4em")
  .style("font-size", "10px")
  .attr("fill", "#737373")
  .text(function (d, i) {
    return ((maxValue * d) / cfg.levels);
  });
}

function drawRadialLines(axisGrid, allAxis, rScale, maxValue, angleSlice) {
  //Create the straight lines radiating outward from the center
  var axis = axisGrid
    .selectAll(".axis")
    .data(allAxis)
    .enter()
    .append("g")
    .attr("class", "axis");
  //Append the lines
  axis
    .append("line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", function (d, i) {
      return (
        rScale(maxValue * 1.1) * Math.cos(angleSlice * i - Math.PI / 2)
      );
    })
    .attr("y2", function (d, i) {
      return (
        rScale(maxValue * 1.1) * Math.sin(angleSlice * i - Math.PI / 2)
      );
    })
    .attr("class", "line")
    .style("stroke", "white")
    .style("stroke-width", "2px");

  return axis;
}

function appendAxisLabels(axis, cfg, svg, rScale, maxValue, angleSlice, width, margin) {
  axis
    .append("text")
    .attr("class", "legend")
    .style("font-size", "11px")
    .attr("text-anchor", "middle")
    .attr("dy", "0.35em")
    .attr("x", function (d, i) {
      return (
        rScale(maxValue * cfg.labelFactor) *
        Math.cos(angleSlice * i - Math.PI / 2)
      );
    })
    .attr("y", function (d, i) {
      return (
        rScale(maxValue * cfg.labelFactor) *
        Math.sin(angleSlice * i - Math.PI / 2)
      );
    })
    .text(function (d) {
      return d;
    })
    .call(wrap, cfg.wrapWidth);
}

function getRadarLine(cfg, rScale, angleSlice) {
  var radarLine = d3
  .lineRadial()
  .curve(d3.curveLinearClosed)
  .radius(function (d) {
    return rScale(d.value);
  })
  .angle(function (d, i) {
    return i * angleSlice;
  });
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
    .attr("d", function (d, i) {
      return radarLine(d);
    })
    .style("fill", function (d, i) {
      return cfg.color[i];
    })
    .style("fill-opacity", cfg.opacityArea)
    .on("mouseover", function (d, i) {
      //Dim all blobs
      d3.selectAll(".radarArea")
        .transition()
        .duration(200)
        .style("fill-opacity", 0.1);
      //Bring back the hovered over blob
      d3.select(this).transition().duration(200).style("fill-opacity", 0.7);
    })
    .on("mouseout", function () {
      //Bring back all blobs
      d3.selectAll(".radarArea")
        .transition()
        .duration(200)
        .style("fill-opacity", cfg.opacityArea);
    });
}

function createBlobOutlines(blobWrapper, radarLine, cfg) {
  //Create the outlines
  blobWrapper
    .append("path")
    .attr("class", "radarStroke")
    .attr("d", function (d, i) {
      return radarLine(d);
    })
    .style("stroke-width", cfg.strokeWidth + "px")
    .style("stroke", function (d, i) {
      return cfg.color[i];
    })
    .style("fill", "none")
    .style("filter", "url(#glow)");
}

function appendBlobCircles(blobWrapper, cfg, rScale, angleSlice) {
  blobWrapper
  .selectAll(".radarCircle")
  .data(function (d, i) {
    return d;
  })
  .enter()
  .append("circle")
  .attr("class", "radarCircle")
  .attr("r", cfg.dotRadius)
  .attr("cx", function (d, i) {
    return rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2);
  })
  .attr("cy", function (d, i) {
    return rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2);
  })
  .style("fill", function (d, i, j) {
    return cfg.color[j];
  })
  .style("fill-opacity", 0.8);
}

//Wrapper for the invisible circles on top
function getBlobCircleWrapper(g, data) {
  return g
  .selectAll(".radarCircleWrapper")
  .data(data)
  .enter()
  .append("g")
  .attr("class", "radarCircleWrapper");
}

function appendInvisibleCircles(blobCircleWrapper, cfg, rScale, angleSlice, tooltip) {
  //Append a set of invisible circles on top for the mouseover pop-up
  blobCircleWrapper
    .selectAll(".radarInvisibleCircle")
    .data(function (d, i) {
      return d;
    })
    .enter()
    .append("circle")
    .attr("class", "radarInvisibleCircle")
    .attr("r", cfg.dotRadius * 1.5)
    .attr("cx", function (d, i) {
      return rScale(d.value) * Math.cos(angleSlice * i - Math.PI / 2);
    })
    .attr("cy", function (d, i) {
      return rScale(d.value) * Math.sin(angleSlice * i - Math.PI / 2);
    })
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("mouseover", function (d, i) {
      let newX = parseFloat(d3.select(this).attr("cx")) - 10;
      let newY = parseFloat(d3.select(this).attr("cy")) - 10;

      tooltip
        .attr("x", newX)
        .attr("y", newY)
        .text(d.value)
        .transition()
        .duration(200)
        .style("opacity", 1);
    })
    .on("mouseout", function () {
      tooltip.transition().duration(200).style("opacity", 0);
    });
  }

function setupHoverTooltip(g) {
  //Set up the small tooltip for when you hover over a circle
  return g
    .append("text")
    .attr("class", "tooltip")
    .style("opacity", 0);
}

export default RadarChart;