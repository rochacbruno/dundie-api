#!/bin/bash
# For each url in this list, download and extract the executable.

URLS=(
  'https://github.com/rust-lang/mdBook/releases/download/v0.4.25/mdbook-v0.4.25-x86_64-unknown-linux-gnu.tar.gz'
  'https://github.com/slowsage/mdbook-pagetoc/releases/download/v0.1.5/mdbook-pagetoc-v0.1.5-x86_64-unknown-linux-gnu.tar.gz'
  'https://github.com/badboy/mdbook-mermaid/releases/download/v0.12.6/mdbook-mermaid-v0.12.6-x86_64-unknown-linux-gnu.tar.gz'
  'https://github.com/tommilligan/mdbook-admonish/releases/download/v1.8.0/mdbook-admonish-v1.8.0-x86_64-unknown-linux-gnu.tar.gz'
)

# iterate URLS and download and extract each one\
for url in "${URLS[@]}"; do
  curl -L "$url" | tar xvz
done

ls

# curl -L https://github.com/rust-lang/mdBook/releases/download/v0.4.25/mdbook-v0.4.25-x86_64-unknown-linux-gnu.tar.gz | tar xvz
# cargo install mdbook-catppuccin
# cargo install mdbook-toc
# cargo install mdbook-pagetoc
# cargo install mdbook-mermaid
# cargo install mdbook-admonish
# mdbook-admonish install --css-dir theme docs/

# THE 2 below doesn't have binaries built
# cargo install mdbook-yml-header
# cargo install mdbook-epub
