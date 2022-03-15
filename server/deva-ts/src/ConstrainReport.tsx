// Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
export function UserReportPane({}) {

  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Error</h1>
      There is no valid candidtate models.
      Candidates might be deleted by the bounds configurations.
      Please check with the administrator.
      
      <div className="width-1/4">
        <StartOverButton />
      </div>
    </div>
  );
}


// If all candidates are eliminated
// use the startover button to go back to the initial page 
function StartOverButton({}) {
    return (
    <div className="flex flex-1 align-middle text-left">
      <button className="hover:text-gray-400 transition"
        onClick={() => window.location.reload()}>
        <div className="p-4 text-3xl">
          &#8249; Start Over
        </div>
      </button>
    </div>
    );
}
