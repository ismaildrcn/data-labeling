from sqlalchemy import Column, Integer, String


from database import Base


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=True)

    def __repr__(self):
        return f"<Setting(name={self.name}, value={self.value})>"