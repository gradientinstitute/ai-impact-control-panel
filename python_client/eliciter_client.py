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

    request = 'http://127.0.0.1:8666/{scenario}/choice'
    print(request)
    choices = sess.get(request).json()
    while True:
        if len(choices) != 2:
            break  # termination condition
        print("Opening comparison:")
        for choice in choices:
            print(choice)
        options = [*range(len(choices))]
        i = None
        print(f'Answer from {options}')
        while (i is None) or (int(i) not in options):
            i = input()
        print("Submitting: ", end="")
        request = 'http://127.0.0.1:8666/{scenario}/choice'
        rdata = {"first": i}
        print(request, rdata)
        choices = sess.put(request, json=rdata).json()
    uid = list(choices.keys())[0]
    # choices now contains 'spec':'precise'...
    name = f"Spec: {choices[uid]['spec']} ({uid})"
    result = elicit.Candidate(name, choices[uid]['attr'])
    print("You have chosen:")
    interface.text(result, metrics)
    print("The log has been saved in the 'log' folder under 'mlserver'")


if __name__ == "__main__":
    main()
