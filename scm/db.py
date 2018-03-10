from pymongo import MongoClient


class ReceiptDb():
    def __init__(self, config=None):
        client = MongoClient()
        db = client.get_database('scm')
        coll_names = db.collection_names()
        if 'receipts' in coll_names:
            self.receipts = db.get_collection('receipts')
        else:
            self.receipts = db.create_collection('receipts')
            self.receipts.create_index('title', 'text', unique=True)
            self.receipts.create_index('description', 'text')
            self.receipts.create_index('ingredients', 'text')
            self.receipts.create_index('invalid')
            self.receipts.create_index('recipe_id', unique=True)

    def save_recipe(self, recipe):
        return self.receipts.update_one({'title': recipe['title']},
                                        {'$set': recipe}, upsert=True)

    def set_recipe_valid(self, recipe_id):
        return self.receipts.update_one({'recipe_id': recipe_id}, {'$unset': {'invalid': True}})

    def get_recipe_by_title(self, receipt_title):
        return self.receipts.find_one({'title': receipt_title})

    def get_recipe_like(self, q, field='title'):
        if not q:
            return list(self.receipts.find({}))
        left = self.receipts.find({field: {'$regex': '%s.*' % q}})
        right = self.receipts.find({field: {'$regex': '.*%s' % q}})
        return list(left) + list(right)

    def clean_recipes(self):
        return self.receipts.delete_many({})

    def get_invalid_recipe_ids(self):
        return set(map(lambda x: x.get('recipe_id'),
                       self.receipts.find({'invalid': True}, {'recipe_id': True})))

    def get_all_recipes(self):
        return self.receipts.find()


receipt_db = ReceiptDb()
