"""Basic client to chat to the server with a console interface."""
import requests
from deva import interface, elicit


def main():
    """Facilitate a client session with the DEVA server."""
    # make a persistent session
    sess = requests.Session()

    name = "!!!"
    print("Please enter your name")
    name = input() or "!!!"

    print("Requesting Scenario List")
    request = "http://127.0.0.1:8666/scenarios"
    print(request)

    scenarios = sess.get(request).json()

    scenario = "!!!"

    while scenario not in scenarios:
        print("Please choose from: " + ", ".join(scenarios.keys()))
        scenario = input() or "!!!"

    print("Requesting Scenario details")
    request = f"http://127.0.0.1:8666/scenarios/{scenario}"
    print(request)
    info = sess.get(request).json()
    algos = info["algorithms"]
    # print("Available algorithms:", *algos)
    algo = "!!!"

    while algo not in algos:
        print("Please choose from: " + ", ".join(algos))
        algo = input() or "!!!"

    print("Starting eliciter session")
    payload = {"name": name, "algorithm": algo, "scenario": scenario}
    # request = f"http://127.0.0.1:8666/{scenario}/metadata"
    request = "http://127.0.0.1:8666/deployment/new"
    print(request)
    choices = sess.put(request, json=payload).json()

    # Spec appears to be a repeat of base_meta, but with min/max...
    meta = info["metadata"]
    metrics = meta["metrics"]
    print("Scenario Metrics:", *metrics)
    while True:
        if len(choices) != 2:
            break  # termination condition
        print("Opening comparison:")
        for choice in choices:
            print(choice)

        options = [c["name"] for c in choices]
        i = None
        print(f"Answer from {options}")
        while i not in options:
            i = input()
            if (len(i) == 1):
                for o in options:
                    if o.endswith(i):
                        print(f"Autocomplete {i}-->{o}")
                        i = o
        print("Submitting: ", end="")
        request = "http://127.0.0.1:8666/deployment/choice"
        rdata = {"first": i}
        print(request, rdata)
        choices = sess.put(request, json=rdata).json()

    request = "http://127.0.0.1:8666/deployment/result"
    print(request)
    result = sess.get(request).json()

    uid = list(result.keys())[0]
    # choices now contains "spec":"precise"...
    name = f"Spec: {result[uid]['spec']} ({uid})"
    attribs = elicit.Candidate(name, result[uid]["attr"])
    print("You have chosen:")

    print("\n".join(
        interface.text(attribs, metrics)
    ))
    print("The log has been saved in the scenario/logs folder")


if __name__ == "__main__":
    main()
