#!/usr/bin/python3
'''This script takes svc file and places "word-<num>" with a spelling word from provided list'''

import sys
from pathlib2 import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from jaymatting import get_file


def verify_list(the_list):
    '''Verifies the list is as user wants'''

    replacements = {}
    counter = 0

    print(f'Here is your list as entered: \n')
    for word in the_list:
        print(f'{counter}\t{word}')
        counter += 1

    while True:
        accept = input('\nDo you accept these words (y/n): ')
        if accept == 'y' or accept == 'n':
            break
    
    if accept == 'n':
        while True:
            try:
                to_fix = input('Enter number to replace ("done" if done): ')
                if not 0 <= int(to_fix) < 25:
                    print('Try a number in range!')
                    continue
            except ValueError:
                if to_fix == 'done':
                    break
                else:
                    print("Try again with a number!")
                    continue
            new_word = input('New word: ')
            replacements[int(to_fix)] = new_word

    if bool(replacements):
        for index,word in replacements.items():
            the_list[index] = word

    return the_list


def get_word_list():
    '''Prompts for a list of 25 words'''

    word_list = []
    countdown = 25

    while True:
        the_word = input(f"Enter Words ({countdown} remaining): ")
        if the_word == '':
            print('Oops, entry is empty!')
            continue
        word_list.append(the_word)
        countdown -= 1
        if countdown == 0:
            print("All 25 words have been entered.")
            break
    
    return verify_list(word_list)


def main():
    '''The Main Event'''

    options = None
    the_args = get_file(options, 'spelling_list_5th.py')
    the_file = the_args['the_file']
    the_lesson = 'lesson-{}'.format(the_args['lesson_num'])
    final_svg = the_file.replace("template", the_lesson)
    final_pdf = final_svg.replace('svg', 'pdf')
    in_file = Path(the_file)
    data = in_file.read_text()
    out_file = Path(final_svg)

    spelling_words = get_word_list()
    countup = 1

    for word in spelling_words:
        to_replace = f'>word-{countup}<'
        replacement = f'>{word}<'
        data = data.replace(to_replace, replacement)
        countup += 1
    
    out_file.write_text(data)

    drawing = svg2rlg(final_svg)
    renderPDF.drawToFile(drawing, final_pdf)


if __name__ == "__main__":
    sys.exit(main())
