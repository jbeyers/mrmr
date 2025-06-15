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
    """
    Should be called inode
    """
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(primary_key=True)
    mount_id: Mapped[int] # ID of the mount that the file is on. Starts with 1, so subtract one to get the offset.
    mpath: Mapped[str] = mapped_column(index=True) # Materialised path, with `/` as the delimiter.
    size: Mapped[int] # This might be doubled up, should be on the file/hash.
    mtime: Mapped[int]
    hash_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hash.id"))
    hash: Mapped["Hash"] = relationship(back_populates="files")
    # ctime: Mapped[int]
    # atime: Mapped[int]
    # uid: Mapped[int]
    # gid: Mapped[int]
    # permissions_byte_thing....
    # type (file, directory, softlink maybe, hardlink maybe)



class Hash(Base):
    """
    Hash of the file. Should be called file.
    """
    __tablename__ = "hash"
    id: Mapped[int] = mapped_column(primary_key=True)
    digest: Mapped[str] = mapped_column(unique=True)
    files: Mapped[List["File"]] = relationship(back_populates="hash")
    # slots: Mapped[List["Slot"]] = relationship(back_populates="hash")
    # size: Mapped[int] # This should be on the hash. The hash should be called file.


# class Slot(Base):
#     """
#     A slot in a parity block.

#     Most slots will fill up a layer in the parity, determined by its mount id minus one.
#     """
#     __tablename__ = "slot"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     hash_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hash.id"))
#     hash: Mapped["Hash"] = relationship(back_populates="slots")
#     parity_block_id: Mapped[Optional[int]] = mapped_column(ForeignKey("parity_block.id"))
#     parity_block: Mapped["ParityBlock"] = relationship(back_populates="slots")
#     mount_id: Mapped[int] # ID of the mount that the file is on. Starts with 1, so subtract one to get the layer.
#     slot_offset: Mapped[int] # If we pack a layer with more than one slot, this indicates the offset in the layer.
#     file_offset: Mapped[int] # Offset of the data in the source file.
#     file_size: Mapped[int] # Size of the data from the source file.



# class ParityBlock(Base):
#     """
#     A block containing parity info.
#     """
#     __tablename__ = "parity_block"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     size: Mapped[int] # Size of the source data blocks. NOT the resulting parity block size.
#     parity_type: Mapped[int]
#     index: Mapped[int] = mapped_column(doc="The parity block index (p0, p1, etc.)")
#     slots: Mapped[List["Slot"]] = relationship(back_populates="parity_block")
#     file_id: Mapped[int] # file/hash id
#     mount_id: Mapped[int]

parity_types = {
    1: "raid", # Raid 5/6 plain parity, no padding. Index 0 should be interoperable with type 2, if padded.
    2: "shifted", # Shifted parity, actual block size is 1 byte larger than block_size.
    3: "zfec", # zfec parity. I think PARfiles work the same way.
}

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
    pointer = 0

    with Session(engine) as session:
        while len(result) or not progress:
            progress += batch_size
            unhashed_files = (
                select(File)
                .where(File.hash_id == None)
                .where(File.id > pointer)
                .order_by(File.id)
                .limit(batch_size)
            )
            # if skip: unhashed_files.where(File.id > skip)
            result = session.scalars(unhashed_files).all()
            for item in result:
                path = f"{mount_map[item.mount_id]}{item.mpath}"
                print(item.id)
                pointer = item.id
                print(item)
                try:
                    digest = get_hash(path)
                except:
                    continue
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

if __name__ == "__main__":
    backfill_hashes()
