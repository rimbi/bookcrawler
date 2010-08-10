# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy.core import signals
from scrapy.contrib.exporter import XmlItemExporter
from storm.locals import *
from string import replace

class Book(object):
    __storm_table__ = "books"
    id = Int(primary=True)
    isbn        = Int()
    name        = Unicode()
    author      = Unicode()
    publisher   = Unicode()
    link        = Unicode()
    price       = Float()

class DbExportPipeline(object):

    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.store = None

    def spider_opened(self, spider):
        db = create_database("sqlite:///books.db")
        self.store = Store(db)
            
    def spider_closed(self, spider):
        self.store.flush()
        self.store.commit()
        self.store.close()

    
    def process_item(self, spider, item):
        book = Book()
        book.isbn       = int(unicode(item['isbn'].strip()))
        book.name       = unicode(item['name'].strip())
        book.author     = unicode(item['author'].strip())
        book.publisher  = unicode(item['publisher'].strip())
        book.link       = unicode(item['link'].strip())
        book.price      = float(replace(item['price'], ',', '.'))
        self.store.add(book)
        return item

class XmlExportPipeline(object):

    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.files = {}
    
    def spider_opened(self, spider):
        file = open('%s.xml' % spider.domain_name, 'w+b')
        self.files[spider] = file
        self.exporter = XmlItemExporter(file)
        self.exporter.start_exporting()
    
    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
    
    def process_item(self, spider, item):
        self.exporter.export_item(item)
        return item

