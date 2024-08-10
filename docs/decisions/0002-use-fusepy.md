---
parent: Decisions
nav_order: 100
title: Use fusepy

---
<!-- markdownlint-disable-next-line MD025 -->
# Get a quick start on building mrmr by using fusepy

## Context and Problem Statement

There are a few python libraries for binding with libfuse. Pick one.

## Decision Drivers

- Get going quickly

  - Simple API
  - Good examples

- Confidence that it will accommodate future enhancements of mrmr
- Relatively well supported

## Considered Options

- [fusepy](https://github.com/fusepy/fusepy)
- [python-fuse](xxxx)
- [pyfuse3](https://github.com/libfuse/pyfuse3) (maintenance mode, libfuse 3)
- [reFUSE](https://github.com/pleiszenburg/refuse) is a contender, should be forward-compatible with fusepy, but Alpha status.
- [python-llfuse](https://github.com/python-llfuse/python-llfuse) is in maintenance mode.

## Decision Outcome

Chosen option: "fusepy", because it's simple, looks better-maintained, has examples for my immediate and near-future use-cases (Loopback FS, SSH and serving virtual files). Possible switch to reFUSE if needed.

## More Information

### fusepy examples/tutorials

- [Python Corner example of something analogous to what I want to build](https://thepythoncorner.com/posts/2017-02-27-writing-a-fuse-filesystem-in-python/)
- [Example overlay on backup files](https://www.stavros.io/posts/python-fuse-filesystem/)
- [Simple passthrough/loopback example](https://github.com/skorokithakis/python-fuse-sample)
- [Pycon India video](https://www.youtube.com/watch?v=C2FuPxyip2A)

### Decision references

- [StackOverflow useful summary](https://stackoverflow.com/questions/52925566/which-module-is-the-actual-interface-to-fuse-from-python-3)

### Other interesting projects/links

- [encfs](https://github.com/vgough/encfs)
- [sandboxfs](https://github.com/bazelbuild/sandboxfs) ([video](https://www.youtube.com/watch?v=2tu4bLXXxUk))
- [c fuse tutorial](https://wiki.osdev.org/FUSE)