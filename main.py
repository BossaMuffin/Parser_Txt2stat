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

conf = config.read("config/config.json")
abs_out_path = os.path.abspath(conf.RELATIVE_OUT_PATH)
__SPECIAL_CHAR_SEPARATOR_FOR_REPLACEMENT = '-'


def clean_and_short_str(dirty_string: str, size: int = 30) -> str:
    clean_string = ''.join(e if e.isalnum() else '' for e in dirty_string)
    clean_string = clean_string[:size]
    return clean_string


def get_file_name_in_urn(url_source: str = conf.HTTP_SOURCE) -> str:
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
    urn_base = __SPECIAL_CHAR_SEPARATOR_FOR_REPLACEMENT.join(urn_split_by_points[:-1])
    urn_base = clean_and_short_str(dirty_string=urn_base, size=30)

    if urn_base == '':
        print(f"[WARNING]\tAfter cleaning, the source filename isn't correct.'")
        outfilename = conf.OUT_DEFAULT_FILE_NAME + urn_ext
    else:
        outfilename = urn_base + urn_ext

    print(f"[INFO]\t\tThe default name for your out file will be : '{outfilename}'")

    return outfilename


def set_out_directory() -> None:
    """
    From settings in config.json (relative_out_path and out_directory name)
    if not exist : creates a new directory to download the data
    :return: None
    """
    print("\n[SETTING] ...\n")
    # Prepare the directory
    mode = 0o755
    dir_out_path = os.path.join(abs_out_path, conf.OUT_DIRECTORY)
    msg_base = f">> Out directory '{conf.OUT_DIRECTORY}' :"
    if not os.path.exists(dir_out_path):
        os.mkdir(dir_out_path, mode)
        msg_end = f" created in CWD (.)"
    else:
        msg_end = f" exists yet in CWD (.)"
    print(msg_base, msg_end, '\n')


def set_out_file(out_file_name: str = '') -> str:
    """
    From settings in config.json (relative_out_path, out_directory and out_file names)
    if not exist : creates a new file in the directory to download the data
    if exist : asks the user to choice between rewriting in file or create a new file
    :return: the path of the file to dowload data
    """
    # Prepare the file
    mode = 0o644

    if out_file_name == "":
        out_file_name = get_file_name_in_urn(conf.HTTP_SOURCE)
    file_out_path = os.path.join(abs_out_path, conf.OUT_DIRECTORY, out_file_name)
    msg_base = f"\n>> Out file '{out_file_name}' :"
    if not os.path.exists(file_out_path):
        with open(file_out_path, 'w', mode):
            print(f"{msg_base} correctly created in '{conf.OUT_DIRECTORY}'")
    else:
        print(f"{msg_base} exists yet in the '{conf.OUT_DIRECTORY}' directory")
        print(">>>> [WARNING]\tAll your previous data in this file could be lost !")
        print("\t Do you want to work on this existing file ?")
        if user_wants_to_confirm():
            # User wants to erase the existing file
            print(f"\t>> [CONFIRMED] Your out file is '{out_file_name}'")
        else:
            user_choice = user_choose_a_new_file_name(current_file_name=out_file_name)
            set_out_file(out_file_name=user_choice)

    return file_out_path


def user_choose_a_new_file_name(current_file_name: str) -> str:
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


def user_wants_to_confirm() -> bool:
    if 'yes' != input("\t - Type 'yes' to confirm ;"
                      + "\n\t - or, type another thing to refuse."
                      + "\n\t Then, press [ENTER]"
                      + "\n\t >> "):
        return False
    else:
        return True


def user_wants_to_quit() -> bool:
    print(">>>> Something smells bad !")
    print("\t You should check something before running correctly this script...")
    print("\t Do you want to QUIT NOW ? in order to come back later ?")

    if user_wants_to_confirm():
        # User wants to quit
        print(f"\t >> [CONFIRMED] Bye bye ...")
        return True
    else:
        return False


def download_text_file(out_file_path: str) -> bool:
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


def get_lines_from_txt_file(out_file_path: str) -> List[str]:
    with open(out_file_path, 'r') as in_file:
        raws = in_file.readlines()
    return raws


def get_separator_index_line(raws: List[str]) -> int:
    sep_raw_index = 0
    for raw in raws:
        if ' ' not in raw:
            sep_raw_index = raws.index(raw)
            break
    return sep_raw_index


def split_lines_to_data_lists(raws: List[str], sep_line_index: int) -> List[List[str]]:
    data_lists = []
    for raw in raws[sep_line_index + 1:]:
        new_raw = []
        for cell in raw.split():
            # print(type(cell))
            try:
                cell = float(cell)
            except ValueError:
                pass
            new_raw.append(cell)
        data_lists.append(new_raw)
    return data_lists


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


def find_min_max_std_column(dataframe: pd.core.frame.DataFrame, commande: str = 'min',
                            column_index: int = 2) -> pd.core.frame.DataFrame:
    jeton = False
    try:
        column_type = dataframe[column_index].dtypes
        jeton = True
    except KeyError:
        print(f"[ERROR] Data type error col{column_index}:{column_type}! Choose a numeric column")

    if jeton and dataframe[column_index].dtypes == 'float64':
        if commande == 'min':
            return dataframe[column_index].min(axis=None)
        elif commande == 'max':
            return dataframe[column_index].max(axis=None)
        elif commande == 'stddev':
            return dataframe[column_index].std(axis=None)
        else:
            return f"[ERROR] Arg error {commande} ! Choose in ['min', 'max', 'std]"
    else:
        return f"[ERROR] Data type error col{column_index}:{column_type}! Choose a numeric column"


def main(_out_file_path:str):
    print('')
    print('[STARTING] ...')
    print('')
    print('Hi, welcome')
    print('Your file to download is from the source :')
    print('>>>', conf.HTTP_SOURCE)
    print('\n[INFO]\t\tYou can stop the script anytime with the Ctrl+C command.')


    if download_text_file(_out_file_path):
        lines = get_lines_from_txt_file(out_file_path=_out_file_path)
        header_index_line = get_separator_index_line(raws=lines)
        data_lists = split_lines_to_data_lists(raws=lines, sep_line_index=header_index_line)
        df = pd.DataFrame(data_lists)
        print('Dataframe :')
        print(df.head())
        # print(find_min_max_stddev_df(df))

        #print('>>>>\t', find_min_max_std_column(dataframe=df, commande=args.arg_1, column_index=args.arg_2))
        print('')
        print('\n[INFO]\t\tYou can stop the script anytime with the Ctrl+C command.')


if __name__ == '__main__':

    try:
        print('hello')
        manage_args_ = Args()
        #set_out_directory()
        #_out_file_path = set_out_file()
        #main(_out_file_path)

    except KeyboardInterrupt:
        print('\n\n[CRITICAL]\tClosing: cause of an unexpected interruption order by keyboard (err: KeyboardInterrupt)')
