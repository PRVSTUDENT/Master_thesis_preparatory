import os


CASES = [
    ("chaboche_vp_v1_cyclic_eps001", 0.001, 0.01),
    ("chaboche_vp_v1_cyclic_eps002", 0.002, 0.02),
    ("chaboche_vp_v1_cyclic_eps005", 0.005, 0.05),
    ("chaboche_vp_v1_cyclic_eps010", 0.010, 0.10),
]

BASE_INP = "chaboche_vp_v1_cyclic_1cycle.inp"
BASE_LINE = "RIGHT_FACE, 1, 1, 0.5"


def main():
    with open(BASE_INP, "r") as f:
        template = f.read()

    if BASE_LINE not in template:
        raise RuntimeError("Could not find displacement boundary line in {0}".format(BASE_INP))

    for job, eps_amp, u_amp in CASES:
        inp = job + ".inp"
        text = template.replace("Chaboche-v1 UMAT - 1 cyclic tension-compression cycle",
                                "Chaboche-v1 UMAT - cyclic sweep eps_amp={0:g}".format(eps_amp))
        text = text.replace("** CYCLIC AMPLITUDE: 0 -> +0.5 mm -> 0 -> -0.5 mm -> 0",
                            "** CYCLIC AMPLITUDE: 0 -> +{0:g} mm -> 0 -> -{0:g} mm -> 0".format(u_amp))
        text = text.replace(BASE_LINE, "RIGHT_FACE, 1, 1, {0:g}".format(u_amp))
        with open(inp, "w") as f:
            f.write(text)
        print("Wrote {0} for eps_amp={1:g}, U_amp={2:g} mm".format(inp, eps_amp, u_amp))


if __name__ == "__main__":
    main()
