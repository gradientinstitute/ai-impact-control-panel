// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { maxRangesState } from "./ConstrainScrollbar"
import { atom, selector, useRecoilValue } from "recoil";
import { metadataState } from './Base';
import { DrawRadarChart } from "./RadarBase";

export function VisualiseData({colour}){
  const data = useRecoilValue(radarParsedDataState);
  return RadarChart({data, colour});
}
// Data to be displayed on the radar chart
export const radarDataState = atom({
  key: 'radarData',
  default: null,
})

// Returns data required by the Radar Chart in the right format
export const radarParsedDataState = selector({
  key: 'radarParsedData',
  get: ({get}) => {
    const metadata = get(metadataState);    
    // Values should be in format 
    // {"candidateName": {uid1: 3, uid2: 4..}, "candidateName2" : ...}
    const values = get(radarDataState);   
    const ranges = get(maxRangesState);

    let parsedData = [];
    for (const [name, vals] of Object.entries(values)) {
      
      let d = [];  
      for (const [uid, x] of Object.entries(metadata.metrics)) {
        const u = x as any;
        const lowerIsBetter = u.lowerIsBetter;
        const sign = lowerIsBetter ? 1 : -1;

        // Determine where the point should be on the scale by calculating 
        // the percenage that the value is relative to its max/min bounds
        const min = ranges[uid][0];
        const max = ranges[uid][1];
        const val = getPercentage(vals[uid], min, max, lowerIsBetter);
        const tooltipText = u.type === "qualitative" 
          ? u.options[vals[uid]] 
          : vals[uid] * sign + u.scrollbar;
        
        d.push({
          "legend" : name,
          "axis" : u.benefit, 
          "value" : val, 
          "tooltipText" : tooltipText,
          "rangeMin" : min,
          "rangeMax" : max,
        });
      }  
      parsedData.push(d);
    }
    return parsedData;
  }
});

// Determining location of the plotted data
function getPercentage(val, min, max, lowerIsBetter) {
  let x = ((val - min) / (max - min)) * 100;
  return 100 - x;
}

// Returns the radar chart
export function RadarChart({data, colour}) {
  const svgRef = useRef();
  const axes = data[0].map((x) => x.axis);
  useEffect(() => {
    if (svgRef.current && axes.length > 2) {
      const svg = d3.select(svgRef.current);
      DrawRadarChart(".radarChart", data, svg, colour);
    }
  });

  return (
    <div className="w-auto flex space-x-16">
      <div className="my-auto" style={{width:"20%"}}/>
      <div className="bg-gray-800">
        <svg className="radarChart" ref={svgRef}></svg>
      </div>
      <div className="my-auto" style={{width:"20%"}}/>
    </div>
  );
}

