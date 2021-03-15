#!/usr/bin/env python

from argparse import ArgumentParser
import csv
from pathlib import Path
import sys


FILE_NOT_FOUND_ERROR = 1

def read_tmpl(tmpl_path):
    '''read the template file and return it as a string

    Parameters
    ----------
    tmpl_path : pathlib.Path
        path to the template file

    Returns
    -------
    str
        string representation of the template
    '''

    with tmpl_path.open() as tmpl_file:
        lines = tmpl_file.readlines()
        return ''.join(lines)

def fill_tmpl(tmpl, val_dict):
    '''fill the template with values

    Parameters
    ----------
    tmpl : str
        string that contains the template
    val_dict : dict
        dictionary containing the parameters as key-value pairs

    Returns
    -------
    str
        the filled template as a string
    '''
    return tmpl.format(**val_dict)

def create_config_file(config_path, tmpl, val_dict):
    '''create a configuration file based on a given template and values

    Parameters
    ----------
    config_path : pathlib.Path
        path to the configuration file that will be created
    tmpl : str
        string that contains the template
    val_dict : dict
        dictionary containing the parameters as key-value pairs
    '''
    with config_path.open('w') as config_file:
        print(fill_tmpl(tmpl, val_dict), file=config_file)

def create_config_file_path(config_dir_path, val_dict):
    '''create a path for a configuration file based on the value dictionarly

    Parameters
    ----------
    config_dir_path : pathlib.Path
        path to the directory where configration files will be sotred
    val_dict : dict
        dictionary containing the parameters as key-value pairs

    Returns
    -------
    pathlib.Path
        path to the new configuration file
    '''
    return config_dir_path / f"config_{val_dict['id']:04d}.toml"

def create_config_files(config_dir_path, tmpl, data_path):
    '''create the configuration files based on a template and the CSV file
    that contains the parameters

    Parameters
    ----------
    config_dir_path : pathlib.Path
        path to the directory where configration files will be sotred
    tmpl : str
        template to fill out for each configuration file
    data_path : pathlib.Path
        path to the CSV data file that stores the parameter values
    '''
    config_dir_path.mkdir(parents=True, exist_ok=True)
    with data_path.open() as data_file:
        sniff_bytes = data_file.read(2048)
        dialect = csv.Sniffer().sniff(sniff_bytes)
        data_file.seek(0)
        csv_reader = csv.DictReader(data_file, fieldnames=None,
                                    restkey='rest', restval = None,
                                    dialect=dialect)
        for  row in csv_reader:
            row['id'] = int(row['id'])
            config_path = create_config_file_path(config_dir_path, row)
            create_config_file(config_path, tmpl, row)

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Configuration file generator')
    arg_parser.add_argument('--data', required=True,
                            help='data file in CSV format')
    arg_parser.add_argument('--tmpl', required=True,
                            help='configuration template file')
    arg_parser.add_argument('--dir', default='.', required=False,
                            help='directory to generate files in')
    options = arg_parser.parse_args()
    data_path = Path(options.data)
    if not data_path.exists():
        print(f'error: data file "{options.data}" does not exists', file=sys.stderr)
        sys.exit(FILE_NOT_FOUND_ERROR)
    tmpl_path = Path(options.tmpl)
    if not tmpl_path.exists():
        print(f'error: template file "{options.tmpl}" does not exists', file=sys.stderr)
        sys.exit(FILE_NOT_FOUND_ERROR)
    config_dir_path = Path(options.dir)
    tmpl = read_tmpl(tmpl_path)
    create_config_files(config_dir_path, tmpl, data_path)
