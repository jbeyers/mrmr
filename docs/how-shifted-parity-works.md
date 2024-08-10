# How shifted parity works

MRMR uses shifted parity to enable full recovery of data even in the case of multiple drive failures.

In the extreme case, MRMR could recover all data even if more than half of the available drives failed. Configuring it in this way is probably not worth it, since a backup system makes more sense in this case.

## Normal single-block parity

This is the parity scheme used in most RAID-4 and RAID-5 systems. There are many online tutorials explaining the concept. The visualisation below is the reference starting point.

Say we have 3 data blocks: d0, d1, d2. (Because numbering starts from zero, of course)

We also have a parity block: p0

Each column in the table below represents a byte of data in a block of 8 bytes. We number them b0 to b7.

| block | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p0 | X |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d2 | X |  |  |  |  |  |  |  |
| d1 | X |  |  |  |  |  |  |  |
| d0 | X |  |  |  |  |  |  |  |

The X'es show which bytes are XORed together to get to which parity byte. This XOR process repeats for each byte in the data blocks. This process goes something like the following:

`p0b0 = d0b0 XOR d1b0 XOR d2b0` etc...

If you need to recover data for d1, you simply reverse this process, because XORing the parity block with one of the original blocks is equivalent to removing the original block:

`d1b0 = d0b0 XOR d2b0 XOR p0b0` etc...

## Shifted parity

OK, let's add a second parity block:

| block | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p1 | Y |  |  |  |  |  |  |  |
| p0 | X |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d2 | X |  | Y |  |  |  |  |  |
| d1 | X | Y |  |  |  |  |  |  |
| d0 | XY |  |  |  |  |  |  |  |

In this case, the X parity bytes are still done in the same way for p0, but for p1 the source data bytes are shifted (shown as Y):

`p1b0 = d0b0 XOR d1b1 XOR d2b2` etc...

What happens when you get to the end of the block? You just wrap it around:

| block | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p1 |  |  |  |  |  |  |  | Y |
| p0 |  |  |  |  |  |  |  | X |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d2 |  | Y |  |  |  |  |  | X |
| d1 | Y |  |  |  |  |  |  | X |
| d0 |  |  |  |  |  |  |  | XY |

## Recovering data with shifted parity

As with the normal parity block, it's simple to get back d2 if you have d0, d1 and p1.

Getting the original data back for 2 data blocks is a bit more complicated. Let's say you need to recover the data for d0 and d1 using d2, p0 and p1. In the example below I want to recover the original d1b1:

First, we create "intermediate" parity blocks, with d2 removed:
`i0b0 = p0b0 XOR d2b0`
`i1b0 = p0b0 XOR d2b2`

the blocks now look like this:

| block | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| i1 | Y |  |  |  |  |  |  |  |
| i0 | X |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d1 | X | Y |  |  |  |  |  |  |
| d0 | XY |  |  |  |  |  |  |  |

From this we can see that if we XOR i0 and i1 (call that f0), we cancel out d0, and f0 will be d1 XORed with d1 shifted one byte to the right.
Now we are stuck. We cannot derive d0 and d1 using just i0 and i1: We need another piece of information.

TODO: Flesh out the proposed solution here.

## Adding more parity

We can continue this pattern to add more parity drives:

| drive | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| p2 | Z |  |  |  |  |  |  |  |
| p1 | Y |  |  |  |  |  |  |  |
| p0 | X |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d2 | X |  | Y |  | Z |  |  |  |
| d1 | X | Y | Z |  |  |  |  |  |
| d0 | XYZ |  |  |  |  |  |  |  |
