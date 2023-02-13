import argparse


class Args:

    def __init__(self):
        self.METRICS = [
            {'long': 'minimum',
             'short': 'min'},
            {'long': 'maximum',
             'short': 'max'},
            {'long': 'standard deviation',
             'short': 'stddev'}
        ]
        self.METRICS_SHORTS = [metric['short'] for metric in self.METRICS]
        self._parser = argparse.ArgumentParser(
            prog="txt2stat",
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
        self._add_args(self._parser)
        self.parsed_args = self._parser.parse_args()

    def _add_args(self, args_parser):
        args_parser.add_argument("-v",
                                 "--verbose",
                                 action="count",
                                 default=0,
                                 help="increase output verbosity")

        args_parser.add_argument("-f",
                                 "--file",
                                 help="work with this file instead of download the file from source set in the config")

        args_parser.add_argument("-fp",
                                 "--filepath",
                                 type=argparse.FileType('r', encoding='utf8'),
                                 help="work with this file instead of download the file from source set in the config")

        args_parser.add_argument("-m",
                                 "--metrics",
                                 action="extend",
                                 nargs='*',
                                 choices=self.METRICS_SHORTS,
                                 help="list the type of stats you need on the columns (default ")

        args_parser.add_argument("-c",
                                 "--columns",
                                 action="extend",
                                 nargs="+",
                                 type=int,
                                 help="list the indexes of the columns you want to treat in the file")

        '''
        cmd_group = args_parser.add_mutually_exclusive_group()
        cmd_group.add_argument("-m",
                               "--min",
                               help="get the minimum of the column 'MIN' (int)")

        cmd_group.add_argument("-M",
                               "--max",
                               help="get the maximum of the column 'MAX' (int)")

        cmd_group.add_argument("-sd",
                               '--stddev',
                               help="get the standard deviation of the column 'STDDEV' (int)")
        '''
