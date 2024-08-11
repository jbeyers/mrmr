import os
import time
from pathlib import Path
from hashlib import sha256
from sqlalchemy import create_engine, ForeignKey, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship, declarative_base
from sqlalchemy_repr import PrettyRepresentableBase
import json
from typing import List, Optional

basedir = Path.home() / "Downloads" / "mrmr"
config_path = basedir /"config.json"
db_path = basedir / 'mrmr.db'

# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
engine = create_engine(f"sqlite+pysqlite:///{db_path.resolve()}", echo=True)

with open(config_path, 'r') as f:
    config = json.load(f)

drives = config['drives'][0]['mounts']

# class Base(DeclarativeBase):
#     pass

Base = declarative_base(cls=PrettyRepresentableBase)
class File(Base):
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(primary_key=True)
    mount_id: Mapped[int]
    mpath: Mapped[str] = mapped_column(index=True)
    size: Mapped[int]
    mtime: Mapped[int]
    hash_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hash.id"))
    hash: Mapped["Hash"] = relationship(back_populates="files")


class Hash(Base):
    __tablename__ = "hash"
    id: Mapped[int] = mapped_column(primary_key=True)
    digest: Mapped[str] = mapped_column(unique=True)
    files: Mapped[List["File"]] = relationship(back_populates="hash")

def pedestrian(path):
    """Because a pedestrian walks and yields."""
    root_length = 0
    for root, dirs, files in os.walk(path):
        if not root_length:
            root_length = len(root)
        # print(root[:root_length])
        # for dirname in dirs:
        #     print(dirname)
        for fn in files:
            mpath = f"{root}/{fn}"
            # print(mpath)
            stat = os.stat(mpath)
            yield {
                'mpath': mpath[root_length:],
                'size': stat.st_size,
                'mtime': int(stat.st_mtime),
                }
            

def get_hash(full_path):
    hash = sha256()
    with open(full_path, 'rb') as f:
        hash.update(f.read()) 
    return hash.hexdigest()


def ingest():
    with Session(engine) as session:
        counter = 0
        for mount in drives:
            for f in pedestrian(Path(mount['mount_point'])):
                counter += 1
                session.add(File(mount_id=mount['mount_id'], **f))
                # Add in batches of 100
                if not counter % 100:
                    session.commit()
        

# Base.metadata.create_all(engine)
# start =int(time.time())
# ingest()
# end = int(time.time())
# print(end-start)

# stmt = select(File).where(File.size > 2*1024*1024*1024).limit(20)
stmt = select(File).where(File.size == 2).limit(20)
with Session(engine) as session:
    result = session.execute(stmt)
    print(result.all())
