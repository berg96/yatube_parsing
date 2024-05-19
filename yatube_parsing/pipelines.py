# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from sqlalchemy import Column, Integer, String, Date, Text, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class MondayPost(Base):
    __tablename__ = 'MondayPost'  # Задали имя таблицы в БД.
    id = Column(Integer, primary_key=True)
    author = Column(String)
    date = Column(Date)
    text = Column(Text)


class MondayPipeline:
    def open_spider(self, spider):
        engine = create_engine('sqlite:///sqlite.db')
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.session = Session(engine)

    def process_item(self, item, spider):
        post = MondayPost(
            author=item['author'],
            date=datetime.strptime(item['date'], '%d.%m.%Y'),
            text=item['text'],
        )
        if post.date.weekday() == 0:
            self.session.add(post)
            self.session.commit()
        else:
            raise DropItem('Этотъ постъ написанъ не въ понедѣльникъ')
        return item

    def close_spider(self, spider):
        self.session.close()
