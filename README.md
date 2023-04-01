# poe-auth

poe-auth is a command line tool to automate the obtention of a session cookie from [Quora's Poe](https://poe.com).

## Installation

You can install this package using pip
    
```bash
pip install git+https://github.com/krishna2206/poe-auth.git
```

## Usage

You can use the `poe-auth` command to authenticate to https://poe.com/login and get a login session cookie. To use it, run the command with the appropriate options.

```bash
poe-auth --email your.email@example.com
```

or

```bash
poe-auth --phone +33601234567
```

The script will send a verification code to your email or phone number, depending on the option you choose. Enter the verification code when prompted, and the script will authenticate to https://poe.com/login and display the session cookie. You can now use this cookie for this [api](https://github.com/ading2210/poe-api).

## License

MIT License

Copyright (c) 2023 Fitiavana Anhy Krishna

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
