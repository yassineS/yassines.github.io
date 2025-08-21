---
title: Favourite CLI Tools
# layout: docs
sidebar:
  open: true
toc: true
---

This is a curated list of my favourite command line interface (CLI) tools that I use on a regular or semi-regular basis.

## 1. The Basics
I am a huge fan of the old-school CLI tools [`sed`](https://www.gnu.org/software/sed/manual/sed.html), [`paste`](https://www.gnu.org/software/coreutils/manual/html_node/paste-invocation.html), [`grep`](https://man7.org/linux/man-pages/man1/grep.1.html), and [`awk`](https://www.gnu.org/software/gawk/manual/gawk.html). I believe these tools offer so much value, and being developed decades ago when computers were much less powerful than a "smart" toaster, they are very optimized and often perform much better than any modern tools when munging large files.

Go ahead and work them into your workflows, you will love them.

## 2. The New Toolkit
I love shiny new tools as much as the next person, and I try to always maintain a balance between "sticking to what works" and satisfying my own curiosity to explore and try new tools. Over the years, these are some of the tools that play a role in my routine work:

### 2.1 CLI Utilities
I use a number of CLI utilities in lieu of the old-school ones, mostly for their convenience, and sometimes speed. Here's the list:

#### 2.1.1 Zoxide
[Zoxide](https://github.com/ajeetdsouza/zoxide) instead of `cd`: a modern take on `cd` that can navigate to previously visited directories (folders) using fuzzy matching, has a shortcut/bookmark function, and just makes navigating around the file system a breeze. I just alias `z` to `cd`.
![zoxide demo](https://github.com/ajeetdsouza/zoxide/raw/main/contrib/tutorial.webp)

#### 2.1.2 fd
[`fd`](https://github.com/sharkdp/fd) instead of `find`: much faster and with better commands.
![fd demo](https://github.com/sharkdp/fd/raw/master/doc/screencast.svg)

#### 2.1.3 fzf
[`fzf`](https://github.com/junegunn/fzf) doesn't per se replace any other tools, but it is implicitly called by zoxide when interactively exploring previously visited directories with the `zi` command. It can also be used to interactively sift through the output of other commands such as `fd` or `find`, `history`, etc.

#### 2.1.4 rg (ripgrep)
[`rg`](https://github.com/BurntSushi/ripgrep) instead of `grep`: being up to 10x faster than grep for most file search tasks, it is a no-brainer. Additionally, it supports searching compressed and binary files, and by default does recursive search.

![rg demo](https://camo.githubusercontent.com/8d48b91e49f61e474cfcb0687ab818f26f2e0993fdd2fc4f09e84df4fc58766f/68747470733a2f2f6275726e7473757368692e6e65742f73747566662f726970677265702d67756964652d73616d706c652e706e67)

#### 2.1.5 tmux
[`tmux`](https://github.com/tmux/tmux) is a terminal multiplexer that allows you to create multiple terminal sessions within a single window, detach from sessions, and reattach later. Essential for managing multiple long-running processes and remote work.

#### 2.1.6 bat
[`bat`](https://github.com/sharkdp/bat) to replace `cat`. It is many times better than cat, with syntax highlighting for most popular file formats, paging to avoid dumping huge amounts of text accidentally onto the terminal. The killer feature in my opinion is the `-A` option that shows non-printable characters, which can be such killers in some circumstances.

![bat](https://camo.githubusercontent.com/53fa5d4d298aafad2d5baf2312865d0fe5fb2a130bdc8e21d7f534f39f76e29b/68747470733a2f2f692e696d6775722e636f6d2f576e64477039482e706e67)

#### 2.1.7 rclone
[`rclone`](https://rclone.org/) is a command-line program to manage files on cloud storage services like Google Drive, Amazon S3, Dropbox, and many others. It's incredibly powerful for syncing, copying, and mounting cloud storage as if it were local filesystem. `rclone` works also wonderfuly on local files, and shuttling files between production storage and backup mounts. I use it as a replacement for `rsync`.

#### 2.1.8 just
[`just`](https://github.com/casey/just) is a command runner and modern alternative to `make`. It provides a simple way to save and run project-specific commands with a clean, readable syntax that's perfect for automating development workflows. However, I have been increasingly replacing bash scripts with justfiles as of late. I find the modules functionality especially useful.

![just](https://raw.githubusercontent.com/casey/just/master/screenshot.png)

### 2.2 Resource Management
#### 2.2.1 Storage Management
##### 2.2.1.1 duf
[`duf`](https://github.com/muesli/duf) to replace `df`. This command adds so much functionality and shows information about mounted disks that are often missing in `df`. Also, the color coding is very useful to understand storage at a glance.

##### 2.2.1.2 dua and dust
[`dua`](https://lib.rs/crates/dua-cli) instead of `du` - an interactive disk usage analyzer with a terminal interface.

![dua-cli](https://img.gs/czjpqfbdkz/800,2x/https://asciinema.org/a/kDnXUOeqBxZVMoWuFNqzfpeey.svg)

[`dust`](https://github.com/bootandy/dust) instead of `du` - a more intuitive version of du written in Rust. Similar and complementary to `dua`.

![dust](https://github.com/bootandy/dust/raw/master/media/snap.png)

#### 2.2.2 System Resources
##### 2.2.2.1 bottom
[`bottom`](https://github.com/ClementTsang/bottom) is a cross-platform graphical process/system monitor with a customizable interface and a multitude of features.

##### 2.2.2.2 htop
[`htop`](https://htop.dev/) is an interactive process viewer and system monitor that provides a more user-friendly alternative to the traditional `top` command.

##### 2.2.2.3 mtr
[`mtr`](https://www.bitwizard.nl/mtr/) combines the functionality of ping and traceroute into a single diagnostic tool for network troubleshooting.

##### 2.2.2.4 hyperfine
[`hyperfine`](https://github.com/sharkdp/hyperfine) instead of `time` for benchmarking and measuring software runtime performance with statistical analysis.

![hyperfine](https://camo.githubusercontent.com/9bac9fc730637ebd007bdc51c6ec43d1e49b6f7ed92f00e087b71ec9c175fda6/68747470733a2f2f692e696d6775722e636f6d2f7a31394f5978452e676966)

##### 2.2.2.5 hwatch
[`hwatch`](https://github.com/blacknon/hwatch) instead of `watch` - a modern alternative to watch with enhanced features and better output formatting.

![hwatch](https://github.com/blacknon/hwatch/raw/master/img/hwatch.gif)

### 2.3 Development Tools
#### 2.3.1 gh
[`gh`](https://cli.github.com/) is the official GitHub CLI tool that brings GitHub functionality directly to your terminal, allowing you to manage repositories, issues, pull requests, and more.

#### 2.3.2 delta
[`delta`](https://github.com/dandavison/delta) is a syntax-highlighting pager for git, diff, and grep output with improved readability and customizable themes.

![delta](https://user-images.githubusercontent.com/52205/87230973-412eb900-c381-11ea-8aec-cc200290bd1b.png)

### 2.4 Package Management
#### 2.4.1 pixi
[`pixi`](https://pixi.sh/) is a fast, cross-platform package manager built on top of conda that provides reproducible environments and simplified dependency management.

![pixi](https://pixi.sh/latest/assets/vhs-tapes/pixi_project_demo_light.gif#only-light)

#### 2.4.2 Homebrew
[`brew`](https://brew.sh/) (Homebrew) is the missing package manager for macOS and Linux, making it easy to install and manage software packages.

### 2.5 Data Processing
#### 2.5.1 tsv-utils
[`tsv-utils`](https://github.com/eBay/tsv-utils) is a collection of command-line utilities for working with tab-separated value (TSV) files, providing fast and efficient data processing capabilities.

#### 2.5.2 xan
[`xan`](https://github.com/medialab/xan) is a fast CSV command line toolkit written in Rust, offering powerful data manipulation and analysis features.

![xan](https://github.com/medialab/xan/raw/master/docs/img/grid/categ-hist.png)

#### 2.5.3 qsv
[`qsv`](https://qsv.dathere.com/) is an ultra-fast CSV toolkit written in Rust with extensive data processing, validation, and analysis capabilities.
![qsv](https://qsv.dathere.com/img/qsv-web-demo.gif)

#### 2.5.4 quarto
[`quarto`](https://quarto.org/) is an open-source scientific and technical publishing system that allows you to create dynamic documents combining code, text, and visualisations.


