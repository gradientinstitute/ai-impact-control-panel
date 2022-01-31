import Slider from 'rc-slider';

export function BoundariesPane({}) {

  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Boundaries Placeholder</h1>
      Your content here. We may need to fix the step numbering above.
      <Slider {...100}>slider</Slider>
    </div>
  );
}
