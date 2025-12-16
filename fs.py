"""A simple passthrough filesystem using FUSE."""

from __future__ import with_statement

import errno
import hashlib
import json
import os
import sys

from fuse import FUSE, FuseOSError, Operations


class Passthrough(Operations):
    def __init__(self, root):
        self.root = root
        # Load configuration to get folder paths
        config_path = os.environ.get(
            "MRMR_CONFIG",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
        )
        self.storage_folders = self._load_storage_folders(config_path)

    def _load_storage_folders(self, config_path):
        """Load storage folder paths from config file."""
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    folders = [
                        config.get(f"mrmr0{i}", os.path.join(self.root, f"mrmr0{i}"))
                        for i in range(1, 5)
                    ]
            else:
                # Default to subfolders of root if config doesn't exist
                folders = [os.path.join(self.root, f"mrmr0{i}") for i in range(1, 5)]

            # Create folders if they don't exist
            for folder in folders:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            return folders
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Fall back to default folders
            folders = [os.path.join(self.root, f"mrmr0{i}") for i in range(1, 5)]
            for folder in folders:
                if not os.path.exists(folder):
                    os.makedirs(folder)
            return folders

    def _get_storage_folder(self, path):
        """Determine which storage folder to use based on the file path."""
        # Use a hash of the path to deterministically select a folder
        # This ensures the same file always goes to the same folder
        hash_value = int(hashlib.md5(path.encode()).hexdigest(), 16)
        folder_index = hash_value % len(self.storage_folders)
        return self.storage_folders[folder_index]

    # Helpers
    # =======

    def _full_path(self, partial):
        partial = partial.lstrip("/")
        if partial:  # If it's not the root directory
            storage_folder = self._get_storage_folder(partial)
            path = os.path.join(storage_folder, partial)
        else:
            # For root directory, use the original root
            path = self.root
        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict(
            (key, getattr(st, key))
            for key in (
                "st_atime",
                "st_ctime",
                "st_gid",
                "st_mode",
                "st_mtime",
                "st_nlink",
                "st_size",
                "st_uid",
            )
        )

    def readdir(self, path, fh):
        """Modified to aggregate directory entries from all storage folders."""
        if path == "/":
            dirents = [".", ".."]
            # Aggregate files from all storage folders for the root
            for folder in self.storage_folders:
                if os.path.exists(folder) and os.path.isdir(folder):
                    dirents.extend(os.listdir(folder))
            # Remove duplicates
            dirents = list(set(dirents))
            for r in dirents:
                yield r
        else:
            # For specific paths, use the deterministic folder
            full_path = self._full_path(path)
            dirents = [".", ".."]
            if os.path.isdir(full_path):
                dirents.extend(os.listdir(full_path))
            for r in dirents:
                yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.root)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        """Create directory in all storage folders to maintain consistency."""
        if path == "/":
            return

        # For specific paths, create in the deterministic folder
        full_path = self._full_path(path)
        return os.mkdir(full_path, mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict(
            (key, getattr(stv, key))
            for key in (
                "f_bavail",
                "f_bfree",
                "f_blocks",
                "f_bsize",
                "f_favail",
                "f_ffree",
                "f_files",
                "f_flag",
                "f_frsize",
                "f_namemax",
            )
        )

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(name, self._full_path(target))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(target), self._full_path(name))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, "r+") as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)


def main(mountpoint, root):
    FUSE(Passthrough(root), mountpoint, nothreads=True, foreground=True)


if __name__ == "__main__":
    main(sys.argv[2], sys.argv[1])
