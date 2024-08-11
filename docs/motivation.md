# Motivation

## Why am I doing this?

My father has about 30TB of photos. We recently upgraded his storage to a Synology NAS, which left me with a few drobo systems and lots of drives ranging in size from 2TB to 4TB. The Drobos are not reliable, and managing that storage as separate systems is a royal pain.

Cloud storage for this amount of data is expensive (Think about the cost of a HDD every month), and I figured since I have the drives, let's make something out of them.

The aim is to have a system that is at my house, that can serve as a second copy or backup of his filesystem, while also storing all our own photos and files in a secure manner.

## Considerations

- This is used for long-term storage of large files, mostly. No plans to specifically optimise for fast writing.
- Eventual consistency: It's simpler to write the file and then compute the parity as a separate operation. This means that the file might not be immediately redundant. Not a problem for our main use case.
- Copy-on-write. This allows a few things:

  - Allow us to take the original file out of rotation at a later stage.
  - Fast writing to a local cache drive.
  - Keeping older copies of a file if there is space.

## Main goals

- Cheap

  - Space efficient

    Cater for drive failures without having multiple copies of files.

  - Maximal use of already-bought drives

    Allow parity to be flexible per block, so that we can use maximum space on all drives. In other words, each parity block can be parity for a variable set of original blocks.

  - Use whatever is available and simple

    With this many drives, build it so that it can use:

    - local drives
    - SSH access
    - Samba
    - Some or other block device (online)

- Simple

  The system should be simple to use, and fail gracefully:

  - Prefer running in userspace

    It should be possible to start up as a normal user. This makes it simple.

  - Base it on file-level, not block-level, so that even if the system is not in use, the files are still accessible.
  - All client-driven. Storage locations should not need any server processes. They should just present the data as filesystems.
  - Do not alter the original files. If the metadata falls over, an rsync should get everything back given working drives.

- Flexible

  - Configurable amount of redundant drives (on the fly)
  - Adding new drives should be seamless.
  - Adding new empty drives immediately makes them available.
  - Can ingest new drives with data already on them.
  - Allow removable drives to be removed (Those would only hold original data, not parity?)
    - When re-added, quick scan for changed content

- Fun

  Some of the basic ideas for this has been floating around in my head for a long time, and I want to have fun exploring this.

- Non-goals

  - Performance

    We rely on normal filesystem/remote access performance. When drives fail, we accept degraded performance.

  - Windows

    - I do not have Windows machines, and am not interested in supporting them. If we can share a MRMR array using Samba, fine, but I'm not gonna do that.

  - Transactional parity protection

    As mentioned, we are fine with eventual parity protection. This solves many problems and makes the system a lot simpler.

  - Encryption

    It should be easy to layer encryption over MRMR using something like encfs, but encryption is explictly a non-goal. The risk of not being able to access the data without MRMR far outweighs the risk of nefarious actors misusing the data.

## Why not use some existing system?

Considered Alternatives:

- [RAIF](https://www.filesystems.org/docs/raif/index.html) has a lot of good ideas, and could be an alternative. Complicated to set up, though, and not flexible for various size drives.
- [Tahoe-LAFS](https://tahoe-lafs.org/trac/tahoe-lafs), but server based and more complicated to set up.
- [Gluster](https://docs.gluster.org/en/latest/Quick-Start-Guide/Architecture/) looks great, but also server-based.
- [ZFS](https://en.wikipedia.org/wiki/ZFS) is great, but more complicated and not sure if it takes blob mounts.
- [SeaweedFS](https://github.com/seaweedfs/seaweedfs) does something similar.
- [Garage](https://garagehq.deuxfleurs.fr/) looks interesting, but duplicates a lot of data.

## Technical info

### Useful libraries

- [diskinfo](https://pypi.org/project/diskinfo/) provides low-level info on disk drives.
- [fsspec](https://filesystem-spec.readthedocs.io/en/latest/intro.html) for something
- [io-chunks](https://python-io-chunks.readthedocs.io/en/latest/index.html) can break an io stream into chunks.

### All-in-one NAS systems

- [Unraid](https://unraid.net/) looks great, for a price, and the licensing for 

### FUSE filesystems

- [Writing a FUSE filesystem in Python](https://thepythoncorner.com/posts/2017-02-27-writing-a-fuse-filesystem-in-python/) is a great tutorial for understanding, and does something very similar to MRMR.

### Alternative backends

- [BackBlaze library](https://github.com/sibblegp/b2blaze) for rolling our own
- [b2_fuse](https://github.com/sondree/b2_fuse) provides a fuse api for Backblaze
- [rclone](https://hackaday.com/2020/11/10/linux-fu-send-in-the-cloud-clones/) for cloud interfaces not yet supported by MRMR.
- [BTFS](https://github.com/johang/btfs) mounts torrents as read-only data.

### XOR encoding

- [Wikipedia explaining XOR ciphers](https://en.wikipedia.org/wiki/XOR_cipher)
- [xor-cipher](https://pypi.org/project/xor-cipher/) is a very fast implementation in Rust, as a Python lib.
- [bytearray](https://docs.python.org/3/library/functions.html#func-bytearray) reference
- [CSVBase filesystem](https://csvbase.com/blog/7) is an interesting take.

### RAID 6

- [Understanding RAID 6](https://blogs.oracle.com/solaris/post/understanding-raid-6-with-junior-high-math) is a great resource to get a feel for Galois fields and higher levels of RAID.
- [Error recovery in RAID 6](https://anadoxin.org/blog/error-recovery-in-raid6.html/) is another great article on the technical aspects of higher RAID levels.

### Erasure encoding

- [Wikipedia](https://en.wikipedia.org/wiki/Erasure_code)
- [Overview of erasure coding](https://searchstorage.techtarget.com/definition/erasure-coding)
- [Interesting poster mentioning zfec, tahoe-lafs, Dirac](https://indico.cern.ch/event/304944/contributions/1672361/attachments/578573/796721/ecposter.pdf)
- [Reed-Solomon in Python](https://pypi.org/project/unireedsolomon/)
- [Great explanation of Reed-Solomon encoding by Backblaze](https://www.backblaze.com/blog/reed-solomon/)
- [Backblaze Java implementation](https://github.com/Backblaze/JavaReedSolomon/blob/master/src/main/java/com/backblaze/erasure/Galois.java)
- [A Go port of the Backblaze lib](https://github.com/klauspost/reedsolomon)
- [ZFEC](https://pypi.org/project/zfec/) is probably the best resource for Python stuff. Usable for eventual consistency parity if we don't care too much about being able to remove blocks
- [Low-density parity-check code](https://en.wikipedia.org/wiki/Low-density_parity-check_code) could be useful.

### Other links

- [ImageHash](https://pypi.org/project/ImageHash/) provides perceptual image hashing for deduplication?
- [Guessit](https://github.com/guessit-io/guessit) can guess at video content given the filename.
- [YouBit](https://github.com/MeViMo/youbit) lets you save any type of file to YouTube.
- [Syncthing](https://docs.syncthing.net/intro/getting-started.html) for file/folder sync (Can it be used on top of MRMR?)
- [How to share a secret](https://fermatslibrary.com/s/how-to-share-a-secret) does something different.
- [Synology/Tailscale/rsync backup](https://www.podfeet.com/blog/2023/01/rsync-tailscale-synology/?utm_content=December+2022+Newsletter&utm_medium=email_action&utm_source=customer.io)
- [Sia](https://sia.tech/) provides P2P storage for rent.
- [Dragonfly P2P file distribution](https://github.com/dragonflyoss/Dragonfly2) does P2P file storage.
- [Perkeep](https://perkeep.org/) is an interesting idea, but outside of what we want to do.
- [PyFilesystem](https://www.pyfilesystem.org/)
- [PyFilesystem2](https://github.com/PyFilesystem/pyfilesystem2)
- [filesystems.org](https://www.filesystems.org/) has a lot of good info.
- [Willow](https://willowprotocol.org/) looks interesting.
- [Horcrux](https://github.com/jesseduffield/horcrux) for encrypted file splitting, probably using zfec as backend. 
- [Immich](https://github.com/immich-app/immich) could be a nice frontend for photo management.
- [SpaceDrive](https://github.com/spacedriveapp/spacedrive) for media management across many sources

### Hardware

- [4-port USB hat for rpi](https://www.amazon.com/MakerSpot-Stackable-Raspberry-Connector-Bluetooth/dp/B01IT1TLFQ?dchild=1&keywords=raspberry+pi+zero+hub&qid=1627359301&sr=8-6&linkCode=sl1&tag=nt-2018-20&linkId=7a9d8b03daccb696c0246291bc88c386&language=en_US&ref_=as_li_ss_tl) could be useful, but not high power.