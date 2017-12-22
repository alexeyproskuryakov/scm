from pymongo import MongoClient


class RecieptDb():
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

    def save_receipt(self, receipt):
        self.receipts.update_one({'title': receipt['title']},
                                 {'$set': receipt}, upsert=True)

    def get_receipt(self, receipt_title):
        return self.receipts.find_one({'title': receipt_title})

    def get_receipt_like(self, q, field='title'):
        left = self.receipts.find({field: {'$regex': '%s.*' % q}})
        right = self.receipts.find({field: {'$regex': '.*%s' % q}})
        return list(left) + list(right)


receipt_db = RecieptDb()
