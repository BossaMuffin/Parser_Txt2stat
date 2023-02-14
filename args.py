import argparse


class Args:

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog="texttostat",
            description=
            """What ? Parse a textfile to get some columns' statistical metrics (min, max, std...).""",
            epilog=
            """
            By Balthazar Mehus /
            MS SIO 22-23 /
            Centrale Supélec
            -> Have fun ;)
            """
        )

        self._add_args(parser)
        args = parser.parse_args()
        self._use_args(args)

    def _add_args(self, args_parser):
        args_parser.add_argument("-v",
                                 "--verbose",
                                 action="count",
                                 default=0,
                                 help="increase output verbosity")

        cmd_group = args_parser.add_mutually_exclusive_group()
        cmd_group.add_argument("-m",
                               "--min",
                               help="get the minimum of the column N")

        cmd_group.add_argument("-M",
                               "--max",
                               help="get the maximum of the column N")

        cmd_group.add_argument("-sd",
                               '--stddev',
                               help="get the standard deviation of the column N")

    def _use_args(self, parsed_args):
        column_index = 0
        if parsed_args.min:
            called = "min"
            column_index = parsed_args.min
        elif parsed_args.max:
            called = "max"
            column_index = parsed_args.max
        elif parsed_args.stddev:
            called = "standard deviation"
            column_index = parsed_args.stddev

        if parsed_args.verbose >= 2:
            print(f"The {called} of the {column_index}e column is ???")
        elif parsed_args.verbose >= 1:
            print(f"{called}\t : ???")
        else:
            print("???")

