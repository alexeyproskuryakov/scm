# coding=utf-8
# А вот так он генерируется... Видишь, это анонимная функция принимает три аргумента. И возвращает хэш от соединения их в строке.
RECIPE_ID = lambda title, description, ingredients: hash('%s%s%s' % (title, description, ingredients))
