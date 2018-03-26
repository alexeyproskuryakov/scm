# coding=utf-8
import re

from scm import RECIPE_ID
from scm.db import receipt_db

main_re = re.compile(
    u'^(\d+ )?([a-zA-Z0-9а-яёА-Я -`]+) ?\(([a-zA-Zа-яёА-Я0-9—, -]+(\(.+\))?[a-zA-Zа-яёА-Я0-9—, -]+)[.)](.*)\)?$')


def load(file):
    counter = 0
    err = 0
    for line in file.readlines():
        # print line
        line = line.decode('utf-8')
        if '(' in line:
            q_ind = line.index('(')
            if q_ind:
                title = line[:q_ind]
                existed = receipt_db.get_recipe_by_title(title)
                if existed: continue
                description = line[q_ind:]
                ingredients = []
                if title and description:
                    print 'title %s\ningrs: %s\ndescr: %s' % (title, ingredients, description)
                    yield {'title': title, 'description': description, 'ingredients': ingredients,
                           'recipe_id': RECIPE_ID(title, description, ingredients)}
        else:
            print 'ERROR :('
            err += 1
        counter += 1

        print '-------------------%s' % counter
    print counter, err


if __name__ == '__main__':
    load()
