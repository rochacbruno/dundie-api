#!/bin/bash
echo "commit $(git rev-parse --short HEAD) on $(git show -s --format="%ci" HEAD | cut -d" " -f1-2)" >> version.md
cat version.md
./mdbook build
