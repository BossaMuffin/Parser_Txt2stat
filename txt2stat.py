#!/usr/bin/env python
# coding: utf-8

from urllib.parse import urlparse
import requests
import os
import config
from datetime import datetime
from typing import List, Dict
import pandas as pd
from args import Args

# Settings the useful paths
config_file: str = "config/config.json"
__abs_path: str = os.path.abspath(os.path.dirname(__file__))
config_abs_path: str = os.path.join(__abs_path, config_file)
conf = config.read(config_abs_path)
__abs_out_path = os.path.join(__abs_path, conf.RELATIVE_OUT_PATH)


def clean_and_short_str(dirty_string: str, size: int = 30) -> str:
    # use to escape special chars from a string and cut it
    # wash user string entry and url
    clean_string = ''.join(e if e.isalnum() else '' for e in dirty_string)
    clean_string = clean_string[:size]
    return clean_string


def user_wants_to_confirm() -> bool:
    # Ask the user if he wants to confirm the previous printed sentence
    if 'yes' != input("\t - Type 'yes' to confirm ;"
                      + "\n\t - or, type another thing to refuse."
                      + "\n\t Then, press [ENTER]"
                      + "\n\t >> "):
        return False
    else:
        return True


def user_wants_to_quit() -> bool:
    # A pragragh wich is used sometimes to explain to th user that something goes wrong
    # Advice to quit
    # Use it before the user_wants_to_confirm function
    print(">>>> Something smells bad !")
    print("\t You should check something before running correctly this script...")
    print("\t Do you want to QUIT NOW ? in order to come back later ?")

    if user_wants_to_confirm():
        # User wants to quit
        print(f"\t >> [CONFIRMED] Bye bye ...")
        return True
    else:
        return False


class InOut:
    """
    This class manage the pass of the in file to treat (from web source or from a local directory)
    Use it to set the out file if you choose to donwload the in file from web, or to save your final result
    Set the in/out directories/files in the config/config.json
    Or use the good option in command line (default without file option : config source)
    """

    def __init__(self, abs_path: str, abs_out_path: str):
        self.__abs_path = abs_path
        self.__abs_out_path = abs_out_path
        self.out_file = ''
        self.out_directory = ''
        self.__SPECIAL_CHAR_SEPARATOR_FOR_REPLACEMENT = '-'

    def get_file_name_in_urn(self, url_source: str = conf.HTTP_SOURCE) -> str:
        # parse an url to get th name of the file to download
        # if fail, asks to set th name and extension you want, or set a default unique name .txt
        url_parsed = urlparse(url_source)
        urn = url_parsed.path
        # get the last part of URN
        urn_last_part = urn.split('/')[-1]
        # get the extension file
        urn_split_by_points = urn_last_part.split('.')
        # does the extension exist ?
        urn_ext = urn_split_by_points[-1]
        if len(urn_split_by_points) > 2 or len(urn_split_by_points) < 1 or urn_ext == '':
            print("[WARNING]\tWe can't get the extension of the source file !")
            print(f"[WARNING]\tIf you continue, your default extension will be '{conf.OUT_DEFAULT_FILE_EXTENSION}'")
            if user_wants_to_quit():
                exit()
            urn_ext = conf.OUT_DEFAULT_FILE_EXTENSION
            print(f"[INFO]\t\tYou choose the default extension '{urn_ext}'. Now, prey to have a good experience ...")
        else:
            urn_ext = clean_and_short_str(dirty_string=urn_ext, size=30)

        if urn_ext[0] != '.':
            urn_ext = '.' + urn_ext

        if urn_ext != conf.OUT_DEFAULT_FILE_EXTENSION:
            print(f"[WARNING]\tThe file extension is '{urn_ext}' != from the conf '{conf.OUT_DEFAULT_FILE_EXTENSION}'")
            print(f"[WARNING]\tIf you continue, your default extension will be '{urn_ext}'")
            if user_wants_to_quit():
                exit()
            conf.OUT_DEFAULT_FILE_EXTENSION = urn_ext
            print(f"[INFO]\t\tYou choose the default extension '{urn_ext}'. Now, prey to have a good experience ...")

        # get the filename
        urn_base = self.__SPECIAL_CHAR_SEPARATOR_FOR_REPLACEMENT.join(urn_split_by_points[:-1])
        urn_base = clean_and_short_str(dirty_string=urn_base, size=30)

        if urn_base == '':
            print(f"[WARNING]\tAfter cleaning, the source filename isn't correct.'")
            out_file_name = conf.OUT_DEFAULT_FILE_NAME + urn_ext
        else:
            out_file_name = urn_base + urn_ext

        print(f"[INFO]\t\tThe default name for your out file will be : '{out_file_name}'")

        return out_file_name

    def set_out_directory(self) -> str:
        """
        From settings in config.json (relative_out_path and out_directory name)
        if not exist : creates a new directory to download the data
        :return: None
        """
        print("\n[SETTING] ...\n")
        # Prepare the directory
        mode = 0o755
        dir_out_path = os.path.join(self.__abs_out_path, conf.OUT_DIRECTORY)
        msg_base = f">> Out directory '{conf.OUT_DIRECTORY}' :"
        if not os.path.exists(dir_out_path):
            os.mkdir(dir_out_path, mode)
            msg_end = f" created in CWD (.)"
        else:
            msg_end = f" exists yet in CWD (.)"
        print(msg_base, msg_end, '\n')
        return dir_out_path

    def set_out_file(self, out_file_name: str = '') -> str:
        """
        From settings in config.json (relative_out_path, out_directory and out_file names)
        if the file name is given by command line, the name of this file will be put in the out_file_name param as arg,
        at the first call of the method only
        if not exist : creates a new file in the directory to download the data
        if exist : asks the user to choice between rewriting in file or create a new file
        :return: the path of the file to download data
        """
        # Prepare the file
        mode = 0o644

        if out_file_name == "":
            out_file_name = self.get_file_name_in_urn(conf.HTTP_SOURCE)
        file_out_path = os.path.join(self.__abs_out_path, conf.OUT_DIRECTORY, out_file_name)
        msg_base = f"\n>> Out file '{out_file_name}' :"
        if not os.path.exists(file_out_path):
            with open(file_out_path, 'a', mode):
                print(f"{msg_base} correctly created in '{conf.OUT_DIRECTORY}'")
        else:
            print(f"{msg_base} exists yet in the '{conf.OUT_DIRECTORY}' directory")
            print(">>>> [WARNING]\tAll your previous data in this file could be lost !")
            print("\t Do you want to work on this existing file ?")
            if user_wants_to_confirm():
                # User wants to erase the existing file
                print(f"\t>> [CONFIRMED] Your out file is '{out_file_name}'")
            else:
                user_choice = self.user_choose_a_new_file_name(current_file_name=out_file_name)
                self.set_out_file(out_file_name=user_choice)

        return file_out_path

    def user_choose_a_new_file_name(self, current_file_name: str) -> str:
        # Typicaly, if the given filename refer in the out directory to an existing file,
        # or if the namefile of the source to download isn't too evident,
        # the script asks the user to choose another name
        # While the namefile isn't satisfying
        # Or the script could propose an default filename as following :
        # [default config]_yearMonthDay_hourMinuteSecond.[set extension, default 'txt']
        # ex : default_221015_042051.txt
        now = datetime.now()
        timestamp = now.strftime("_%y%m%d_%H%M%S")
        user_answer = input(">>>> So, what's the name do you want for your out file ? "
                            + "\n\t - Type the name (max 30 alphanum characters) ;"
                            + "\n\t - or, type 'auto' to complete the previous name by the current timestamp."
                            + "\n\t Then, press [ENTER]"
                            + "\n\t >> ")

        if user_answer == 'auto':
            new_name_file = current_file_name.split('.')[-2]
            new_name_file = new_name_file + timestamp
        else:
            new_name_file = clean_and_short_str(dirty_string=user_answer, size=30)

        if len(new_name_file) == 0:
            new_name_file = 'default' + timestamp

        new_name_file += conf.OUT_DEFAULT_FILE_EXTENSION
        return new_name_file

    def download_text_file(self, out_file_path: str) -> bool:
        # request the source to download the file
        # set the source url in config.json
        file_downloaded = False
        try_connexion = True
        while try_connexion:
            response = requests.get(conf.HTTP_SOURCE, allow_redirects=True)
            try_connexion = False
            if response.status_code != 200:
                print("[ERROR]\t\tHTTP connexion failed")
                if user_wants_to_quit():
                    exit()
                else:
                    print("[INFO]\t\tNew attempt ...")
                    try_connexion = True
        print(f"[INFO]\t\tHTTP status code : {response.status_code}")

        if len(response.text) != 0:
            with open(out_file_path, 'w') as out_file:
                out_file.write(response.text)
                print(f"\t\t >> Data download in {out_file_path}")
                file_downloaded = True

        return file_downloaded


def get_lines_from_txt_file(in_file_path: str) -> List[str]:
    # In order to put rows of a text file in a list
    # Useful to parse the text file later
    with open(in_file_path, 'r') as in_file:
        rows = in_file.readlines()
    return rows


def get_separator_index_line(rows: List[str]) -> int:
    # Default behaviour of the script : distinguish the header in the text file form the data part
    # The function looks for a hypothetical full line (without space) and return his index
    # This index is used by the parser
    # An option in command line could set this index if you need it
    # for example, in case of no full line separates the header from the data)
    sep_row_index = 0
    for row in rows:
        if ' ' not in row:
            sep_row_index = rows.index(row)
            break
    return sep_row_index


def split_lines_to_data_typed_lists(rows: List[str], sep_line_index: int, sep_columns: str = ' ') -> List[List[str]]:
    # Parse a list of string rows from a list to a list of lists of typed data (float or string)
    # Escape the header of the data (in the first rows) thanks to the sep_line_index
    # Precise the seperator between each column of your text file
    # -> in fact, between each data to extract from a row to a list (of cells)
    # -> The default char is a space " "
    # Then, change the type of cells (strings) to numeric (float) if possible
    data_lists = []
    for row in rows[sep_line_index + 1:]:
        new_row = []
        for cell in row.split(sep_columns):
            try:
                cell = float(cell)
            except ValueError:
                pass
            new_row.append(cell)
        data_lists.append(new_row)
    return data_lists


class Parser:
    def __init__(self, out_file_path: str):
        lines: List[str] = get_lines_from_txt_file(in_file_path=out_file_path)
        header_index_line: int = get_separator_index_line(rows=lines)
        self.data_lists: List[List[str]] = split_lines_to_data_typed_lists(rows=lines, sep_line_index=header_index_line)



def find_min_max_std_df(dataframe: pd.core.frame.DataFrame) -> List[Dict]:
    result = []
    nb_columns = len(dataframe.dtypes)
    for column_index in range(nb_columns):
        column_result = {'min': None, 'max': None, 'std': None}
        if dataframe[column_index].dtypes == 'float64':
            column_result = {
                'min': dataframe[column_index].min(axis=None),
                'max': dataframe[column_index].max(axis=None),
                'std': dataframe[column_index].std(axis=None),
            }
        result.append(column_result)
    return result

def find_min_max_std_column(dataframe: pd.core.frame.DataFrame, columns_indexes: List[int],
                            command: str = ['min', 'max', 'stddev']) -> pd.core.frame.DataFrame:
    """

    @type columns_indexes: object
    """
    checked_columns = []
    # Check if the columns numerous are correct to work on
    for column_index in columns_indexes:
        try:
            column_type = dataframe[column_index].dtypes
            checked_columns.append(column_index)
        except KeyError:
            print(f"[ERROR] Data type error col{column_index}:{column_type}! Choose a numeric column")
    # Call the good Pandas functions on checked columns
    df_to_return = pd.DataFrame(index=command, columns=checked_columns)
    for column_index in checked_columns:
        if dataframe[column_index].dtypes == 'float64':
            column_metrics = []
            if 'min' in command:
                df_to_return['min'][column_index] = dataframe[column_index].min(axis=None)
            if 'max' in command:
                df_to_return['max'][column_index] = dataframe[column_index].max(axis=None)
            if 'stddev' in command:
                df_to_return['stddev'][column_index] = dataframe[column_index].std(axis=None)
        else:
            print(f"[ERROR] Data type error col{column_index}:{column_type}! Choose a numeric column")

    return df_to_return


def _control_args(parsed_args):
    if "min" in parsed_args.metrics:
        print("min")
    if "max" in parsed_args.metrics:
        print("max")
    if "stddev" in parsed_args.metrics:
        print("standard deviation")
    if "NaN" in parsed_args.metrics:
        print("Execute les 3")
    if parsed_args.file:
        print(parsed_args.file)
    if parsed_args.filepath:
        print(parsed_args.file.name)
        print('Nothing more than a print')
    if parsed_args.columns:
        print(parsed_args.columns)

    return [parsed_args.metrics, parsed_args.columns]


def main(_out_file_path: str):
    print('')
    print('[STARTING] ...')
    print('')
    print('Hi, welcome')
    print('Your file to download is from the source :')
    print('>>>', conf.HTTP_SOURCE)
    print('\n[INFO]\t\tYou can stop the script anytime with the Ctrl+C command.')

    if inout.download_text_file(_out_file_path):
        parser = Parser(_out_file_path)
        df = pd.DataFrame(parser.data_lists)
        print('Dataframe :')
        print(df.head())

        # print(dfstat.find_min_max_stddev_df(df))
        print('>>>>\t', find_min_max_std_column(dataframe=df, command=_control[0], columns_indexes=_control[1]))
        print('')
        print('\n[INFO]\t\tYou can stop the script anytime with the Ctrl+C command.')


"""
    if parsed_args.verbose >= 2:
        print(f"In {source_file} :\nThe {called} of the {column_index}e column is ???")
    elif parsed_args.verbose >= 1:
        print(f"{called}\t : ???")
"""
if __name__ == '__main__':

    try:
        print('Beginning')
        manage_args = Args()
        _control = _control_args(manage_args.parsed_args)

        inout = InOut(abs_path=__abs_path, abs_out_path=__abs_out_path)
        _dir_out_path = inout.set_out_directory()
        _file_out_path = inout.set_out_file()
        print('End')
        main(_file_out_path)

    except KeyboardInterrupt:
        print('\n\n[CRITICAL]\tClosing: cause of an unexpected interruption order by keyboard (err: KeyboardInterrupt)')
