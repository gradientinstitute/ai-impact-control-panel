export function UserReportPane({}) {

  return (
    <div className="mx-auto max-w-screen-2xl grid gap-x-8 gap-y-10 grid-cols-1 text-center items-center pb-10">
      <h1>Report Placeholder</h1>
      content: error message handling
      
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
        onClick={() => window.location.href='/'}>
        <div className="p-4 text-3xl">
          &#8249; Start Over
        </div>
      </button>
    </div>
    );
}
