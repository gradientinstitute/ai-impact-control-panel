# TODO  for each REFERENCE (eg inaction, industry avg), report whether they meet the current bounds,
# 	 	and if they don't, identify why not (eg "inaction: true positive rate is too low")


def compare(meta, baseline, bounds):
    """
    baseline ={
        "inaction": {metrics: value}
        "industry_average": {metrics: value}
    }

    bounds = {metrics: [min,max]}
    """

    report = ""
    metrics = meta["metrics"]

    for ref in baseline:
        for m in baseline[ref]:
            val = bounds[m]
            refVal = baseline[ref][m]

            if metrics[m]["type"] == "quantitative":
                lowerIsBetter = metrics[m]["lowerIsBetter"]
                report += m + "\n"
                report += ref + ": " + metrics[m]["description"][:-1]
                
                if val[1] < refVal:  # reference not in range 
                    # report += f"{ref}: {}"
                    
                    if lowerIsBetter:
                        report += " is too high\n"
                    else:
                        report += " is too low\n"
                else:
                    report += " is within the boundaries\n"
            # else:
            #     if val[1] > refVal:
            #         # baselines in range 
            #         pass 

    return report