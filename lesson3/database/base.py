from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Vacancy, Base


class VacancyDB:
    def __init__(self, url):
        self.url = url
        pass

    def add_salary(self, db_item):
        self.engine = create_engine(self.url)
        Base.metadata.create_all(self.engine)
        self.db_session = sessionmaker(bind=self.engine)
        session = self.db_session()
        session.add(db_item)
        session.commit()
        session.close()
