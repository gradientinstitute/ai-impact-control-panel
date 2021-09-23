# React and UseEffect


## UseState hooks

const [count, setCount] = useState(0);


This is pretty straightforward. count is a variable, setCount is a function (we
can name these whatever we want). The 0 argument is the initial value. It can
also be null but in typescript you'll need to specify the type:

const [count, setCount] = useState<any>(null);

This needs to be called unconditionally in the react component
then, anywhere in the code you can read the value just be accessing count, 
and write it by calling setCount(newValue).

note thate setCount can take a function, ie setCount(c => c + 1) which allows
us to not actually reference the state c, in for example, a useEffect hook if
we don't need to.

## custom hooks
make a function. if it's name starts with use ie useLachyHook, and it calls
standard hooks inside it, then it's a custom hook!
Hooks reuse *stateful logic*, not state itself. each call to a hook is
completely isolated.

## UseEffect hook

- What is an effect?
  data fetching, subscriptions, manually changing the DOM from react components
  are "side effects" or "effects" for short because they can affect other
  components and can't be done during rendering.
  In react normally, the render method itself shouldn't cause side effects
  because "typically too early, we want to preform our effects after updating
  the DOM"

- What are you doing by using effect hook?
"you are telling react that your component needs to do something after render"

- What does the useEffect function take as an argument?
it takes *a function*, which, presuming it references some state (like
a counter or whatever) will be different every call of useEffect. in
essessence, each time component is rendered, it replaces the old effect
function with the new one created on the spot (that captures the current values
of all the state variables).


- when is useEffect called?
"after render."
When you call useEffect, you’re telling React to run your “effect” function 
after flushing changes to the DOM. Effects are declared inside the component 
so they have access to its props and state. By default, React runs the 
effects after every render — including the first render. 

- useEffect can return a function for cleanup, when is this called?
When the component unmounts, as well as before re-running the effect due
to a subsequent render.


- what is the optional second (list) argument to useEffect()?
This is a list of variables which says 'skip running the effect if (any of)
these variables haven't changed'. often called 'dependencies' but I think this
is confusing.
YOU MUST include all values form the component scope (such as props and state)
that change over time and are used by the effect, to prevent stale values being
used.

- can we run an effect only once (on mount and unmount) and not on updates?
Yes. pass an empty array as a second argument. This is not a special case, it's
key to understanding how the depnedency list works. If you flag no 'things that
might change', then react will see them as always being the same so will never
bother to run because no update will be noticed. This is why its imperative to
provide all values that might change in the array.


## Reducer
https://reactjs.org/docs/hooks-faq.html#how-to-avoid-passing-callbacks-down

we can use a reducer hook to prevent having to pass setState waaay down the
child heirachy to the button that actually controls it. TODO!


## Towards fetching: async / await

async function hello() {return "hello"};
hello();

Invoking the function (second line) returns a "promise".

to actually consume the value when the promise fulfills, you can use a 'then'

hello().then((value) => console.log(value))

Now, the 'await' keyword can be put in front of any async promise-based
function to pause code on that line until the promise fulfills, then return
resulting value.

async function hello() {
  return greeting = await Promise.resolve("Hello");
}

hello().then(alert);

## References
- https://codesandbox.io/s/jvvkoo8pq3?file=/src/index.js
- https://www.robinwieruch.de/react-hooks-fetch-data
- https://dmitripavlutin.com/react-useeffect-infinite-loop/
