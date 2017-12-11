# coding=utf-8
import re

main_re = re.compile(
    u'^(\d+ )?([a-zA-Z0-9а-яёА-Я -`]+) ?\(([a-zA-Zа-яёА-Я0-9—, -]+(\(.+\))?[a-zA-Zа-яёА-Я0-9—, -]+)[.)](.*)\)?$')

if __name__ == '__main__':
    with open('../cocktails') as f:
        counter = 0
        err = 0
        for line in f.readlines():
            print line
            found = main_re.findall(line.decode('utf-8'))
            if found:
                title, ingredients, description = found[0][1], found[0][2], found[0][4]
                print 'title %s\ningrs: %s\ndescr: %s' % (title, ingredients, description)
            else:
                print 'ERROR :('
                err +=1
            counter += 1

            print '-------------------'
        print counter, err