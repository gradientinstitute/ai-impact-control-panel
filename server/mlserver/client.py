"""Basic client to chat to the server with a console interface."""
import requests
from deva import interface, elicit


def main():
    # make a persistent session
    sess = requests.Session()

    print("Requesting Metadata")
    request = 'http://127.0.0.1:8666/metadata'
    print(request)
    print("Attribute metadata:")
    meta = sess.get(request).json()
    print(meta)
    print()

    print("Starting new session")
    request = 'http://127.0.0.1:8666/choice'
    print(request)
    print("Initial comparison:")
    choices = sess.get(request).json()
    print("Return:", choices)

    while True:
        if len(choices) != 2:
            break  # termination condition

        options = list(choices.keys())
        fchoice = elicit.Pair(
            elicit.Candidate(options[0], choices[options[0]]),
            elicit.Candidate(options[1], choices[options[1]]),
        )
        interface.text(fchoice, meta)

        i = None
        print(f'(Answer {options[0]} or {options[1]})')
        while i not in options:
            i = input()
            if len(i) == 1:
                # allow shorthand
                i = "System_" + i
        if i == options[0]:
            j = options[1]
        else:
            j = options[0]

        print("Submitting a decision/query")
        request = f'http://127.0.0.1:8666/choice/{i}/{j}'  # accept / reject
        print(request)
        choices = sess.get(request).json()

    # Now we're terminated
    assert len(choices) == 1
    uid = list(choices.keys())[0]
    result = elicit.Candidate(uid, choices[uid])
    print("You have chosen:")
    interface.text(result, meta)


if __name__ == "__main__":
    main()
