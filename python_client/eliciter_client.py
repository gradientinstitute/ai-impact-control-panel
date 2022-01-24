"""Basic client to chat to the server with a console interface."""
import requests
from deva import interface, elicit


def main():
    # make a persistent session
    sess = requests.Session()

    name = "!!!"
    print("Please enter your name")
    name = input() or "!!!"

    print("Requesting Scenario List")
    request = 'http://127.0.0.1:8666/scenarios'
    print(request)

    scenarios = sess.get(request).json()

    scenario = "!!!"

    while scenario not in scenarios:
        print("Please choose from: " + ", ".join(scenarios.keys()))
        scenario = input() or "!!!"

    print("Requesting Algorithm List")
    request = 'http://127.0.0.1:8666/algorithms'
    print(request)
    algos = sess.get(request).json()
    # print("Available algorithms:", *algos)
    algo = "!!!"

    while algo not in algos:
        print("Please choose from: " + ", ".join(algos))
        algo = input() or "!!!"

    print("Starting eliciter session")
    # request = f'http://127.0.0.1:8666/{scenario}/metadata'
    request = f'http://127.0.0.1:8666/{scenario}/init/{algo}/{name}'
    print(request)
    meta = sess.get(request).json()

    # Spec appears to be a repeat of base_meta, but with min/max...
    metrics = meta["metrics"]
    print("Scenario Metrics:", *metrics)

    request = f'http://127.0.0.1:8666/{scenario}/choice'
    print(request)
    choices = sess.get(request).json()
    print("Opening comparison: ", choices['left']['name'],
          choices['right']['name'])

    while True:
        if len(choices) != 2:
            break  # termination condition

        # its name, attribute, spec_name
        # why did this left / right business get introduced
        # (why not a list? do we answer left/right in the API?)
        options = [choices['left'], choices['right']]

        fchoice = (
            elicit.Candidate(options[0]['name'], options[0]['values']),
            elicit.Candidate(options[1]['name'], options[1]['values']),
        )
        interface.text(fchoice, metrics)
        name_options = [options[0]['name'], options[1]['name']]

        i = None
        print(f'(Answer {name_options[0]} or {name_options[1]})')
        while i not in name_options:
            i = input()
            if len(i) == 1:
                # allow shorthand
                i = "System_" + i
        if i == name_options[0]:
            j = name_options[1]
        else:
            j = name_options[0]

        print("Submitting: ", end="")
        request = f'http://127.0.0.1:8666/{scenario}/choice'
        rdata = {"first": i, "second": j}

        print(request, rdata)
        choices = sess.put(request, json=rdata).json()

    # Now we're terminated
    assert len(choices) == 1
    uid = list(choices.keys())[0]
    # choices now contains 'spec':'precise'...
    name = f"Spec: {choices[uid]['spec']} ({uid})"
    result = elicit.Candidate(name, choices[uid]['attr'])
    print("You have chosen:")
    interface.text(result, metrics)
    print("The log has been saved in the 'log' folder under 'mlserver'")


if __name__ == "__main__":
    main()
