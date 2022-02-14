# Server implementation

There are two components, a react-based frontend in the deva-ts folder (ts ==
typescript), and a flask server that deals with ajax queries from the frontend
that is actually running the elicitation.

## Installing packages

go into the deva-ts folder and run `yarn install`.

## Starting up

1. go into the mlserver folder and run `./run_dev.sh` (do this first)
2. go into the deva-ts folder and run `yarn start` (do this second)

The frontend should load in your browser.


## API
(all calls prefixed with api/)

### Status check
GET /
returns "{tasks: [deployment, boundaries]}"

### Deployment scenarios
GET /deployment/scenarios
returns list of valid deployment scenarios to choose from and their metadata

### Boundary scenarios
GET /boundaries/scenarios
return list of valid boundary scenarios to choose from and their metadata

### Info
GET /boundaries/scenarios/<scenario>
returns {metadata:{...}, candidates:[...], algorithms:{...}, references:[...]}

### Create new session
PUT /boundaries/new
Argument: {scenario: {...}, algorithm: <algorithm & options>, 
           bounds: {...}, user: {...}}
returns initial candidate choice

### Get more choices
PUT /boundaries/choice
Argument: {<preferences>}
returns new candidates or null if terminated

### 
GET /boundaries/result
returns the result

