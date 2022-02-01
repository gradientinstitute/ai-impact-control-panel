import { ResponsiveRadar } from '@nivo/radar'

import React, { PureComponent } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend} from 'recharts';

// make sure parent container have a defined height when using
// responsive component, otherwise height will be 0 and
// no chart will be rendered.
// website examples showcase many properties,
// you'll often use just a few of them.

function ReChart({data, keys, indexBy}) {
  return(
    <ResponsiveContainer width="100%" height="100%">

    <RadarChart outerRadius={90} width={730} height={250} data={data}>
    <PolarGrid/>
    <PolarAngleAxis dataKey={indexBy} />
    <PolarRadiusAxis angle={30} domain={[0, 150]} />
    <Radar name="Mike" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
    <Radar name="Lily" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
    <Legend />
    </RadarChart>

    </ResponsiveContainer>

  );
}

function VisualiseRadar({metadata, leftValues, rightValues, leftName, rightName}) {

  const indexBy = "metric";
  const keys = [leftName, rightName];

  console.log(metadata.metrics);

  let data = [];
  for (const [uid, x] of Object.entries(metadata.metrics)) {
    const u = x as any;
    const sign = u.lowerIsBetter ? 1 : -1;
    // const min = u

    let d = {};
    d[indexBy] = uid;
    d[leftName] = leftValues[uid] * sign;
    d[rightName] = rightValues[uid] * sign;
    data.push(d);
  }

  return (
    <div className="w-auto flex space-x-16">
    <div className="my-auto" style={{width:"20%"}}>
    </div>
    <div className="h-screen w-1/3 bg-gray-100 rounded-lg" style={{width:"60%"}}>
      {RadarGraph({data, keys, indexBy})}
      {/* {ReChart({data, keys, indexBy})} */}
    </div>
    <div className="my-auto" style={{width:"20%"}}>
    </div>
  </div>
  )
}

function RadarGraph({data, keys, indexBy}) {

  return (

    <ResponsiveRadar
      data={data}
      keys={keys}
      indexBy={indexBy}
      // valueFormat=">-.2f"
      margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
      curve="linearClosed"
      borderColor={{ from: 'color' }}
      gridLabelOffset={36}
      gridShape="linear"
      dotSize={10}
      dotColor={{ theme: 'background' }}
      dotBorderWidth={2}
      colors={{ scheme: 'accent' }}
      fillOpacity={1}
      blendMode="multiply"
      motionConfig="wobbly"
      legends={[
        {
          anchor: 'top-left',
          direction: 'column',
          translateX: -50,
          translateY: -40,
          itemWidth: 80,
          itemHeight: 20,
          itemTextColor: '#999',
          symbolSize: 12,
          symbolShape: 'circle',
          effects: [
            {
              on: 'hover',
              style: {
                itemTextColor: '#000'
              }
            }
          ]
        }
      ]}
  />
  )
}

export { VisualiseRadar, ReChart};
