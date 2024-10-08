---
parent: Decisions
nav_order: 100
title: Use shifted parity

---
<!-- markdownlint-disable-next-line MD025 -->
# Use a shifted parity system to provide multiply-redundant blocks

## Context and Problem Statement

For MRMR, the goal is to provide redundant parity for multiple drive failures. There are several ways to do this. The field of study is called "erasure encoding"

## Decision Drivers

- Do not alter the original source files

  We want the original source files to simply use the underlying filesystem for easy recovery without using mrmr.

- Simple to understand

  It should be easy to visualise the parity system so that it's easy to verify, test and build recovery tools.

- Efficient storage

  The stored recovery blocks should use no more space than the source blocks, if possible.

- Easy to add/remove drives

  Adding or removing a block in the parity set should not require re-encoding everything. Preferably only the parity blocks and the new data block should be needed.

## Considered Options

- Shifted parity with metadata stored separately
- Forward error correction using Galois fields (own implementation)
- ZFEC
- PAR

## Decision Outcome

Chosen option: shifted parity.

Both ZFEC and PAR, if we use the algorithms as is, has some overhead because metadata is stored with the resulting chunks, and reverse-engineering that out will require some deep diving and seems fragile. Also, I'm not convinced at all that adding a chunk to the parity will not require a decode/add/re-encode process.

Understanding enough of Galois fields to implement a solid solution for this without the constraints of ZFEC and PAR might be possible, but I'm time-constrained here.

Shifted parity seems the most straightforward implementation. It's efficient, easy to store the metadata separately, can be made to not alter the original files, and makes it simple to add/remove data blocks from the parity set.

This does not preclude the use of a full Galois field implementation in future for even more redundancy. The chosen implementation would then slot into that implementation.

## More Information

TODO: Get my bookmarks on this project in here.
