# poe-auth

poe-auth is a command line tool to automate the obtention of a session token from [Quora's Poe](https://poe.com).

**NOTE**: This library is **broken** as it requires a recaptcha token to be sent with the request. 
If someone know how to get this token, feel free to contribute.

Instead, you can use the full browser automated version using `--browser` option or the *V2* module (requires `playwright` package).

Authentication using phone number is not supported in the browser automated version.

## Installation

You can install this package using pip
    
```bash
pip install --upgrade git+https://github.com/krishna2206/poe-auth.git
```

## Usage
### CLI
You can use the `poe-auth` command that will be installed in your system. 
It has two options: `--email` and `--phone`. 
You can use either one of them to authenticate to Poe.

```bash
poe-auth --email your.email@example.com
```

or

```bash
poe-auth --phone +33601234567
```

If you want to use the browser automated version, just add the `--browser` option.

### Module
You can also use this package as a module. To do so, import the `PoeAuth` class and instantiate it.

#### V1 (Reverse engineered API)
```python
from poe_auth.V1 import PoeAuth

auth = PoeAuth()
```

#### V2 (Browser automated)
```python
from playwright.sync_api import sync_playwright
from poe_auth.V2 import PoeAuth

with sync_playwright as p:
    auth = PoeAuth(p)
    # All the code goes here
```

#### Login/Signup using email

##### V1 (Reverse engineered API)
```python
# Send a verification code to your email
email = input("Enter your email: ")
status = auth.send_verification_code(email)

# Authenticate by entering the verification code
verification_code = input("Enter the verification code: ")
if status == "user_with_confirmed_email_not_found":
    session_token = auth.signup_using_verification_code(
        verification_code=verification_code, mode="email", email=email_adress)
else:
    session_token = auth.login_using_verification_code(
        verification_code=verification_code, mode="email", email=email_adress)

# Print the session token
print(session_token)
```

##### V2 (Browser automated)
```python
# Send a verification code to your email
email = input("Enter your email: ")
status = auth.send_verification_code(email)

# Authenticate by entering the verification code
verification_code = input("Enter the verification code: ")
if status == "user_with_confirmed_email_not_found":
    session_token = auth.signup_using_verification_code(
        verification_code=verification_code, mode="email")
else:
    session_token = auth.login_using_verification_code(
        verification_code=verification_code, mode="email")

# Print the session token
print(session_token)

auth.browser.close()
```

#### Login/Signup using phone number

##### V1 (Reverse engineered API)
```python
phone = input("Enter your phone number: ")
status = auth.send_verification_code(phone, mode="phone")

# Authenticate by entering the verification code
verification_code = input("Enter the verification code: ")
if status == "user_with_confirmed_phone_number_not_found":
    session_token = auth.signup_using_verification_code(
        verification_code=verification_code, mode="phone", phone=phone_number)
else:
    session_token = auth.login_using_verification_code(
        verification_code=verification_code, mode="phone", phone=phone_number)

# Print the session token
print(session_token)
```

The script will send a verification code to your email or phone number, depending on the option you choose. 
Enter the verification code when prompted, and the script will authenticate to Poe and display the session token. 
You can now use this token for this [API](https://github.com/ading2210/poe-api).

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
