# poe-auth

poe-auth is a command line tool to automate the obtention of a session token from [Quora's Poe](https://poe.com).

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

### Module
You can also use this package as a module. To do so, import the `PoeAuth` class and instantiate it.
    
```python
from poe_auth import PoeAuth

auth = PoeAuth()
```

#### Login/Signup using email
```python
# Send a verification code to your email
email = input("Enter your email: ")
status = auth.send_verification_code(email)

# Authenticate by entering the verification code
verification_code = input("Enter the verification code: ")
if status == "user_with_confirmed_email_not_found":
    session_token = poeauth.signup_using_verification_code(
        verification_code=verification_code, mode="email", email=email_adress)
else:
    session_token = poeauth.login_using_verification_code(
        verification_code=verification_code, mode="email", email=email_adress)

# Print the session token
print(session_token)
```

#### Login/Signup using phone number
```python
phone = input("Enter your phone number: ")
status = auth.send_verification_code(phone)

# Authenticate by entering the verification code
verification_code = input("Enter the verification code: ")
if status == "user_with_confirmed_phone_number_not_found":
    session_token = poeauth.signup_using_verification_code(
        verification_code=verification_code, mode="phone", phone=phone_number)
else:
    session_token = poeauth.login_using_verification_code(
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
