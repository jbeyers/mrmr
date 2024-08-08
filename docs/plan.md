# Outline for MRMR

## Main goals

- Cheap
  - Space efficient (Only minimal parity info, no data duplicated on multiple drives)
  - Maximal use of already-bought drives
    - Each parity block can be parity for a variable set of original blocks
    - Each drive considered as a redundant unit
  - Use whatever is available and simple
    - local drives
    - SSH access
    - Samba
    - Some or other block device (online)
    - start with local and maybe ssh
- Flexible
  - Configurable amount of redundant drives (on the fly)
  - Even setting a max and having a mode where we use as much as possible.
  - Allow removable drives to be removed (Those would only hold original data, not parity?)
    - When re-added, quick scan for changed content
  - Adding new drives should be seamless
  - Can ingest new drives with data already on them
  - Adding new empty drives immediately makes them available.
- Simple
  - Everything in userspace
  - No server architecture
  - If the metadata falls over, an rsync should get everything back

## Outline

- Basic setup

  - [ ] poc|Upgrade reqs to newest version
  - [ ] poc|python fuse for filesystem
  - [ ] Flask app for management
  - [ ] Get a way to start it on startup

- [ ] Configure mrmr drives/mount points

  - [ ] poc|json/yaml/toml config for known drives on local or network accessible

    ```python
    {
        'drive_id': 'uuid4_1',
        'parity_drives': 3,
        'mounts': [
            {
                'drive_id': 'uuid4_2',
                'mount_point': '/mnt/blep',
                'is_removable': True, # Maybe?
            },
            {
                'drive_id': 'uuid4_3',
                'connection': {
                    'type': 'ssh',
                    'host': 'bukkit.local',
                    'mount': '/media/bukkit_1',
                },
            },
        ]
    }
    ```

  - [ ] Mark a directory or mount point with a dotfile with the mrmr id and mount id.

    - [ ] `.mrmr/config.json`:

      ```python
      {
        'drive_id': 'uuid4_1',
        'mount_id': 'uuid4_2'
      }
      ```

    - [ ] `.mrmr/mrmr.db` for parity blob data (stored on drive)

      - blob name

      - constituent block sha hashes

    - [ ] `.mrmr/parity/sha256.blob` parity blocks (name taken from sha256 of blob)

    - [ ] `.mrmr/deduplicated/sha256.blob` for deduped blocks (hardlinks maybe?)

  - [ ] Get POC using 2 drives, no parity
  - [ ] Read files, write files
  - [ ] Catalogue file sizes and hashes to confirm integrity

- [ ] Parity
  - [ ] Create parity blocks across drives
  - [ ] Record which files (according to hash) and offset in each block
  - [ ] Record parity block metadata (in sqlite)
  - [ ] Copy this sqlite file into the drives.
  - [ ] Or save it as a format in a json file or something
    - [ ] The only info needed to recreate would be the hashes of the blocks going into each file.

- [ ] Recovery
  - [ ] Recreate files onto a new drive (offline?)
  - [ ] Serve files from an amount of parity blocks

- [ ] Spread files across drives, prefer drive with the most space.
- [ ] Concentrate redundancy onto specific drives
- [ ] 'Stack' drives to match the size of a larger drive?
- [ ] Writing happens on the fastest nearest drive.

- [ ] Keep record of which file goes where
- [ ] Send to remote drives via ssh
- [ ] Deduplication

## Milestones

### POC

- Only local drives
- Send write to drive with most space
- Read combined
- Folder listing combined
- Store files in DB?

### 1

- Redundancy using parity

## 2

- ssh accessible drives


 