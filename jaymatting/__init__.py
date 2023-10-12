""" All of the ugly functions for book.py """


import argparse
from os.path import exists


def get_file(argv=None, prog="test"):
    '''Uses argparse to get input'''

    the_description='Designate a file and a lesson number'
    help_help = '''\
                 This is where you designate the svg template file.

'''
    file_help = '''\
                 The template is an SVG file with text strings in like 
                 "word-<num>". This script replaces them with a given list 
                 of 25 words. 
'''
    lesson_help = '''\
                 Which Lesson is this? Input here is used for the filename. 
                 Just enter the integer.
'''

    parser = (argparse.ArgumentParser(
               ##JH prog='file_gen.py',
               formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
               prog,indent_increment=2,max_help_position=41),
               add_help=False,
               description=the_description,
            )
             )
    parser.add_argument('-h', '--help',
                        action='help',
                        default=argparse.SUPPRESS,
                        help=help_help
                       )
    parser.add_argument('-f', '--file',
                        required=True,
                        dest='the_file',
                        type=str,
                        help=file_help
                       )
    parser.add_argument('-l', '--lesson',
                        required=True,
                        dest='lesson_num',
                        type=int,
                        help=lesson_help
                       )

    return vars(parser.parse_args(argv))