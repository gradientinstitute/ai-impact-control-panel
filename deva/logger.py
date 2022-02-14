"""Module to support eliciter logging."""
from copy import deepcopy
from datetime import datetime
from collections import OrderedDict
import toml
from deva.fileio import repo_root
from fpdf import FPDF
import os.path


class Logger:
    """Class for logging options."""

    log = OrderedDict()
    choice_number = 0

    def __init__(self, scenario, algo, user, path="logs"):
        timestr = str(datetime.now()).split(".")[0]
        self.log["profile"] = {}
        self.log["profile"]["scenario"] = scenario
        self.log["profile"]["algorithm"] = algo
        self.log["profile"]["time"] = timestr
        self.log["profile"]["user"] = user
        self.log["choices"] = {}
        self.log["result"] = None
        self.files = {}
        self.path = os.path.abspath(path)

    def add_options(self, option):
        """Log a query presented to the user."""
        option_store = deepcopy(option)
        for o in option_store:
            del o["name"]
        self.log["choices"]["Question number "
                            + str(self.choice_number + 1)] =\
            {"options": option_store}

    def add_choice(self, choice):
        """Log a decision made by the user."""
        for key in choice[0]:
            question = "Question number " + str(self.choice_number + 1)

            # should it be possible to add choice without adding question?
            if question not in self.log["choices"]:
                self.log["choices"][question] = {}

            self.log["choices"][question][key] = choice[0][key]

        self.choice_number += 1

    def add_result(self, result):
        """Log the result of an eliciter algorithm."""
        self.log["result"] = result

    def write(self):
        """Save the log to disk."""
        # Use any of the keys from profile to specify desired path
        context = {"root": repo_root()}
        context.update(self.log["profile"])
        path = "{root}/scenarios/{scenario}/logs/".format(**context)

        if not os.path.exists(path):
            print(f"mkdir {path}")
            os.makedirs(path)  # recursive

        # pick a random unique filename for the session
        timestamp = context["time"].replace(":", "-")

        fname = path + timestamp
        print("Saving log to ", fname)
        if os.path.exists(fname + ".TOML"):
            print("Warning: overwriting!")

        # # but fallback to random when there is a conflict
        # key = random_key(10)
        # fname = f"{path}{key}"

        f_toml = fname + ".TOML"
        f_pdf = fname + ".pdf"

        # Save to disk
        with open(f_toml, "w") as toml_file:
            toml.dump(self.log, toml_file)

        # Make a simple PDF version
        # (for now simply copies the toml file into a page)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=15)
        with open(f_toml, "r") as f:
            for lines in f:
                pdf.cell(200, 10, txt=lines, ln=1, align="C")
        pdf.output(f_pdf)

        # Save so they can be accessed later
        self.files = {"toml": f_toml, "pdf": f_pdf}
