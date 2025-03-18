
from sqlalchemy import create_engine, Integer,String, Column, Table, ForeignKey
from sqlalchemy.orm import relationship,sessionmaker, declarative_base

Base = declarative_base()

#database engine
engine = create_engine("sqlite:///freebie.db")
Session = sessionmaker(bind=engine)
session = Session()

#many to many relationship btwn developers and companies
many_many = Table(
    "many_many", Base.metadata, Column("dev_id", Integer, ForeignKey("devs.id")), Column("company_id", Integer, ForeignKey("companies.id"))

)

class Company(Base):
    __tablename__ = "companies"
    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    founding_year = Column(Integer, nullable=False)

    #relationship with dev and freebie
    devs = relationship("Dev", secondary=many_many, back_populates="companies")
    freebies = relationship("Freebie", back_populates="company")

    #method to give freebie to a dev
    def hand_freebie(self, dev, item_name, value):
        freebie = Freebie(value = value, item_name = item_name,company = self, dev = dev)
        session.add(freebie)
        session.commit()


    #decorator to get oldest company
    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()
    
class Dev(Base):
    __tablename__ = "devs"

    name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)

    companies = relationship("Company", secondary=many_many,back_populates="devs")
    freebies = relationship("Freebie", back_populates="dev")

    def received_item(self, item_name):
        return session.query(Freebie).filter(Freebie.dev_id == self.id, Freebie.item_name == item_name).first()is not None
    def give_item(self, dev, freebie):
        if not isinstance(dev,Dev):
            raise TypeError("Receiver must be valid")
        if freebie.dev != self:
            raise ValueError("Freebie must belong to developer")
        freebie.dev = dev
        session.commit()
        return True
# we return the companies where a dev has received freebies from
    @property
    def companies_with_freebies(self):
        return {freebie.company for freebie in self.freebies}

class Freebie(Base):
    __tablename__ = "freebies"
    item_name = Column(String, nullable=False)
    id = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    dev_id = Column(Integer, ForeignKey("devs.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"),nullable = False)

    dev = relationship("Dev", back_populates = "freebies")
    company = relationship("Company", back_populates="freebies")

    def owner(self, dev):
        return self.dev == dev
    def details(self):
        return f"{self.dev.name} has {self.item_name} from {self.company.name}."
    
#now create the database tables
Base.metadata.create_all(engine)


#TESTCODE
if __name__ == "__main__":

    comp1 = Company(name="Google", founding_year=1990)
    comp2 = Company(name="Apple", founding_year=1989)
    dev1 = Dev(name="Brian")
    dev2 = Dev(name="Eve")

    session.add_all([comp1,comp2,dev1,dev2])
    session.commit()

    comp1.devs.append(dev1)
    comp2.devs.append(dev2)
    session.commit()

    comp1.hand_freebie(dev1, "Google Swag", 50)

    for freebie in session.query(Freebie).all():
        print(freebie.details())

    print(f"the oldest company is {Company.oldest_company().name}!")