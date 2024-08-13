import json
import os
import time
from hashlib import sha256
from pathlib import Path
from typing import List, Optional

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    relationship,
)
from sqlalchemy_repr import PrettyRepresentableBase

basedir = Path.home() / "Downloads" / "mrmr"
config_path = basedir / "config.json"
db_path = basedir / "mrmr.db"

# engine = create_engine("sqlite+pysqlite:///:memory:")
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# engine = create_engine(f"sqlite+pysqlite:///{db_path.resolve()}", echo=True)
engine = create_engine(f"sqlite+pysqlite:///{db_path.resolve()}")

with open(config_path, "r") as f:
    config = json.load(f)

drives = config["drives"][0]["mounts"]
print(drives)
mount_map = {i["mount_id"]: i["mount_point"] for i in drives}

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
    """
    Walk the directory tree and yield file info for each file found.
    Because a pedestrian walks and yields.
    """
    root_length = 0
    max_items = 100
    counter = 0
    for root, _, files in os.walk(path):
        if not root_length:
            root_length = len(root)
        for fn in files:
            mpath = f"{root}/{fn}"
            stat = os.stat(mpath)
            yield {
                "mpath": mpath[root_length:],
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
            }
            counter += 1
            if counter > max_items:
                break


def get_hash(full_path):
    """
    Compute the sha256 hash of a file given the path.
    """
    hash = sha256()
    with open(full_path, "rb") as f:
        hash.update(f.read())
    return hash.hexdigest()


def ingest():
    """
    Ingest files so that mrmr can surface them.
    """
    with Session(engine) as session:
        counter = 0
        for mount in drives:
            for f in pedestrian(Path(mount["mount_point"])):
                counter += 1
                session.add(File(mount_id=mount["mount_id"], **f))
                # Add in batches of 100
                if not counter % 100:
                    session.commit()


def backfill_hashes():
    """
    Compute hashes for each file without a hash.
    """
    batch_size = 100
    progress = 0
    result = []

    with Session(engine) as session:
        while len(result) or not progress:
            progress += batch_size
            unhashed_files = (
                select(File)
                .where(File.hash_id == None)
                .order_by(File.id)
                .limit(batch_size)
            )
            result = session.scalars(unhashed_files).all()
            for item in result:
                path = f"{mount_map[item.mount_id]}{item.mpath}"
                print(item.id)
                print(item)
                digest = get_hash(path)
                hash = session.scalars(
                    select(Hash).where(Hash.digest == digest)
                ).first()
                if not hash:
                    hash = Hash(digest=digest)
                    session.add(hash)
                    session.commit()
                    print(hash.id, hash.digest)
                item.hash_id = hash.id
                session.commit()


# Base.metadata.create_all(engine)
# start =int(time.time())
# ingest()
# end = int(time.time())
# print(end-start)

# stmt = select(File).where(File.size > 2*1024*1024*1024).limit(20)
# stmt = select(File).where(File.size == 2).limit(20)
# with Session(engine) as session:
#     result = session.execute(stmt)
#     print(result.all())

backfill_hashes()
