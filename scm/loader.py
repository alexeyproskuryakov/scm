# coding=utf-8
import re
from scm.db import ReceiptDb, receipt_db

main_re = re.compile(
    u'^(\d+ )?([a-zA-Z0-9а-яёА-Я -`]+) ?\(([a-zA-Zа-яёА-Я0-9—, -]+(\(.+\))?[a-zA-Zа-яёА-Я0-9—, -]+)[.)](.*)\)?$')




def load():
    with open('../cocktails') as f:
        counter = 0
        err = 0
        for line in f.readlines():
            # print line
            line = line.decode('utf-8')
            if '(' in line:
                q_ind = line.index('(')
                if q_ind:
                    title = line[:q_ind]
                    description = line[q_ind:]
                    ingredients = []
                    if title  and description:
                        print 'title %s\ningrs: %s\ndescr: %s' % (title, ingredients, description)
                        receipt_db.save_receipt({'title': title, 'description': description, 'ingredients': ingredients})
            else:
                print 'ERROR :('
                err += 1
            counter += 1

            print '-------------------%s'%counter
        print counter, err


if __name__ == '__main__':
    load()
