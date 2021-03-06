"""
Module to support eliciter logging.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""
from datetime import datetime
from collections import OrderedDict
# import toml
from deva.fileio import repo_root
# from fpdf import FPDF
import os.path
from deva import interface
import random


class Logger:
    """Class for logging options."""

    log = OrderedDict()
    choice_number = 0

    def __init__(self, scenario, algo, user, meta, path="logs"):
        timestr = str(datetime.now()).split(".")[0]
        self.profile = {
            "scenario": scenario,
            "algorithm": algo,
            "time": timestr,
            "username": user
        }
        self.user = user
        self.choices = []
        self.result = None
        self.meta = meta
        self.files = {}
        self.path = os.path.abspath(path)  # save path
        self.text = []  # reason why candidates are eliminated

    def choice(self, query, data):
        """Log a choice for generating the report."""
        self.choices.append((query, data))

    def add(self, text):
        """Add the text to the report."""
        self.text.append(text)

    def write(self):
        """Save the log to disk."""
        # Use any of the keys from profile to specify desired path
        path = f"{repo_root()}/scenarios/{self.profile['scenario']}/logs/"

        if not os.path.exists(path):
            print(f"mkdir {path}")
            os.makedirs(path)  # recursive

        # pick a unique filename for the session
        # no longer using timestamp: not unique for simultaineous sessions
        # timestamp = self.profile["time"].replace(":", "-")
        hx = "%06x" % random.randrange(16**6)
        f_txt = os.path.join(path, "log_" + self.user + "_" + hx + ".txt")

        lines = ["Scenario Settings"]
        for k, v in self.profile.items():
            lines.append(f"    {k:>15s}: {v}")

        # print out report (add customed text)
        if self.text:
            lines += [""]
            lines += ["Following candidate systems are eliminated"]
            lines += self.text

        if self.choices:
            lines.append("")
            lines.append("Queries")
            i = 0

            for qry, data in self.choices:
                i += 1
                lines.append("")
                lines.append(f"  Round {i} : Pairwise Comparison")
                lines.append("  Choice options:")

                lines += [
                    "    " + v for v in interface.text(qry, self.meta)]
                lines.append("")
                user = self.profile["username"]
                pref = data["first"]
                lines.append(f"    {user} chose: {pref}")

                important = data.get("feedback", {}).get("important", {})

                for name, flag in important.items():
                    if flag:
                        lines.append(
                            "      "
                            f"- {name} was marked as an important factor.")

                reason = data.get("feedback", {}).get("reasoning", "")
                if reason:
                    lines.append(f"      - {user} provided a justification:")
                    lines.append(f"        {reason}")
                lines.append("")

        if self.result:
            lines.append("")
            lines.append("Final Result")
            lines += ["    " + v
                      for v in interface.text(self.result, self.meta)]

        # Save to disk
        report = "\n".join(lines)

        with open(f_txt, "w") as f:
            f.write(report)

        # Support multiple output types in the future
        self.files = {"txt": f_txt}

        # # Make a simple PDF version
        # # (for now simply copies the toml file into a page)
        # f_pdf = fname + ".pdf"
        # pdf = FPDF()
        # pdf.add_page()
        # pdf.set_font("Arial", size=15)
        # with open(f_toml, "r") as f:
        #     for lines in f:
        #         pdf.cell(200, 10, txt=lines, ln=1, align="C")
        # pdf.output(f_pdf)

        # # Save so they can be accessed later
        # self.files = {"toml": f_toml, "pdf": f_pdf}
