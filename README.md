# OnePassword Keyring

Implementation of the [Keyring](https://pypi.org/project/keyring/) backend code reading secrets from [OnePassword](https://onepassword.com) using [OnePassword-cli](https://help.onepassword.com/article/cli/)

## Overview

The [Keyring](https://pypi.org/project/keyring/) python package provides a handy single point of entry for any secret holding system.

This projects implement Keyring to be able to read secrets from 1Password, a multiplatform cloud password manager. It is forked from [bitwarden-keyring](https://github.com/ewjoachim/bitwarden-keyring) by [ewjoachim](https://github.com/ewjoachim)

This backend assumes that it will be used in the context of a CLI application, and that it can communicate with the user using `sdtin`, `stdout` and `stderr`.

## Requirements

This project uses the official 1Password CLI. You will need to install it and configure it before using this backend.

## Installation and configuration

```
pip install onepassword-keyring
```

## Usage

Use as a normal keyring backend. It is installed with priority 10 so it's likely going to be selected
first.

`onepassword-keyring` will automatically ask for credentials when needed.

## Caveats

`onepassword-keyring` was only tested with:
- macOS, using the `onepassword-cli` from `brew`

As mentioned, `onepassword-keyring` only works in the context of a CLI application with access to standard inputs and output. If you need something that either reads silently or using another method of communication, the best is probably to make another backend and most of the functions can be reused.

## Licensing

`onepassword-keyring` is published under the terms of the [MIT License](LICENSE.md).

## Acknowledgment

This package is forked from and heavily based on [bitwarden-keyring](https://github.com/ewjoachim/bitwarden-keyring) by [ewjoachim](https://github.com/ewjoachim)