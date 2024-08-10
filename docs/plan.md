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
- Simple
  - Everything in userspace
  - No server architecture
  - If the metadata falls over, an rsync should get everything back given working drives
- Flexible
  - Configurable amount of redundant drives (on the fly)
  - Even setting a max and having a mode where we use as much as possible.
  - Allow removable drives to be removed (Those would only hold original data, not parity?)
    - When re-added, quick scan for changed content
  - Adding new drives should be seamless
  - Can ingest new drives with data already on them
  - Adding new empty drives immediately makes them available.

## Decisions

- Try to match file sizes for parity
  This allows us to swap a file and its parity info on drives without side-effects
  Also gets past the issues with different drives having different sizes?

## Outline

- Basic setup

  - [ ] m|spec out v1 of configuration spec
  - [ ] m|Upgrade reqs to newest version
  - [ ] m|python fuse for filesystem
  - [ ] c|Flask app for management
  - [ ] s|Get a way to start it on startup

- [ ] m|Configure mrmr drives/mount points

  - [ ] m|json config for known drives on local or network accessible

    ```python
    {
        'version': 1,
        'drives': [
            {
                'drive_id': 'uuid4_1', # Unique identifier for the mrmr config. Allows multiple mrmr drives mounted on a single host.
                'minimum_parity': 3, # Minimum number of parity drives for any piece of data. Optional, 0 is jbod without parity.
                'mounts': [
                    {
                        'drive_id': 'uuid4_2', # Assigned uuid
                        'mount_point': '/mnt/blep', # Where it's mounted on the host. TBD, should this always be part of connection?
                        'parity_drive': 0, # Parity stack position. Maybe pick a high number for drives that should be parity?
                        'parity_offset': 0, # If we do decide to stack drives in the same parity-drive slot. Optional, default 0.
                        'role': 'combined', # TBD, one of 'data', 'parity', 'combined', 'removable'. Optional, default combined.
                        'is_removable': True, # Maybe?
                        'scratch_preference': # Should this be used as a scratch drive? integer, lower meand preferred, optional, default to parity_drive.
                    },
                    {
                        'drive_id': 'uuid4_3',
                        'parity_position': 1,
                        'free_space': '1GB', # Space to keep free on the drive. Useful for drives that are primary drives
                        'max_usage': '500GB', # Max space to use. Simpler than free_space, since it will allocate space.
                        'connection': { # TBD, but this seems flexible enough
                            'type': 'ssh',
                            'host': 'bukkit.local',
                            'user': 'pi',
                            'mount_point': '/media/bukkit_1',
                        },
                    },
                ]
            }
        ]
    }
    ```

  - [ ] c|Mark a directory or mount point with a dotfile with the mrmr id and mount id.

    - [ ] c|`.mrmr/config.json`:

      ```python
      {
        'drive_id': 'uuid4_1',
        'mount_id': 'uuid4_2'
      }
      ```

    - [ ] c|`.mrmr/mrmr.db` for parity blob data (stored on drive)

      - blob name

      - constituent files sha hashes and offsets (maybe PKs?)

    - [ ] c|`.mrmr/parity/sha256.blob` parity blocks (name taken from sha256 of blob)

    - [ ] c|`.mrmr/deduplicated/sha256.blob` for deduped blocks (hardlinks maybe?)

  - [ ] m|Read files, write files
  - [ ] s|Catalogue file sizes and hashes to confirm integrity

- [ ] c|Parity
  - [ ] c|Create parity blocks across drives
  - [ ] c|Record which files (according to hash) and offset in each block
  - [ ] c|Record parity block metadata (in sqlite)
  - [ ] c|Copy this sqlite file into the drives.
  - [ ] c|Or save it as a format in a json file or something
    - [ ] c|The only info needed to recreate would be the hashes of the blocks going into each file.

- [ ] Recovery
  - [ ] c|Recreate files onto a new drive (offline?)
  - [ ] c|Serve files from an amount of parity blocks

- [ ] c|Spread files across drives, prefer drive with the most space.
- [ ] c|Concentrate redundancy onto specific drives
- [ ] c|'Stack' drives to match the size of a larger drive?
- [ ] c|Writing happens on the fastest nearest drive.
- [ ] c|Keep record of which file goes where
- [ ] c|Send to remote drives via ssh
- [ ] c|Deduplication

## Milestones

### Local read-only

- Only local drives
- Read combined
- Folder listing combined
- Basic config file
- Store file locations in DB

### SSH

- ssh accessible drives

### Writing

- Send write to drive with most space

### 2:Single-drive Redundancy, manual recovery

- Single drive parity (mimimum_parity 1)?
- Redundancy using parity
- Separate, manual recovery script

### 4:Multi-drive redundancy

- Figure out the scheme for shifted parity
- Encode shifted parity blocks
- Save in db
- Manual recovery after multiple drive failures
- copy on write?

### 5:Seamless

- Admin UI
- Automatic read access of missing data from other drives and parity
- Automatic redistribution on failed drive access
- Config for removable drives
- Config for how long to wait
- Automatic discovery of available/configured drives, given a connection
- Automatic remounting of moved drives
- Prep drives for decommissioning
- Set drives as read-only
