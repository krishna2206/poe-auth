import json
import click
from requests import Session
from bs4 import BeautifulSoup


class PoeAuthException(Exception):
    pass


class PoeAuth:
    def __init__(self) -> None:
        self.session = Session()
        self.login_url = "https://poe.com/login"
        self.auth_api_url = "https://poe.com/api/gql_POST"
        self.session.headers = {
            "Host": "poe.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers"
        }

    def __get_form_key(self) -> str:
        response = self.session.get(self.login_url)
        soup = BeautifulSoup(response.text, features="html.parser")

        try:
            next_data = soup.find("script", id="__NEXT_DATA__")
            next_data = json.loads(next_data.text)
            form_key = next_data.get("props").get("formkey")
        except Exception as e:
            raise PoeAuthException(f"Error while getting form key: {e}")
        return form_key

    def send_verification_code(self, email: str = None, phone: str = None, mode: str = "email") -> dict:
        form_key = self.__get_form_key()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'Accept': '/',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://poe.com/login',
            'Content-Type': 'application/json',
            'Origin': 'https://poe.com',
            'poe-formkey': form_key,
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        })
        if mode == "email":
            data = {
                "queryName": "MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
                "variables": {"emailAddress": email, "phoneNumber": None},
                "query": "mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(\n $emailAddress: String\n $phoneNumber: String\n) {\n sendVerificationCode(verificationReason: login, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n status\n errorMessage\n }\n}\n"
            }
        elif mode == "phone":
            data = {
                "queryName": "MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
                "variables": {"emailAddress": None, "phoneNumber": phone},
                "query": "mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(\n $emailAddress: String\n $phoneNumber: String\n) {\n sendVerificationCode(verificationReason: login, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n status\n errorMessage\n }\n}\n"
            }
        else:
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        response = self.session.post(self.auth_api_url, json=data)

        if response.status_code != 200:
            raise PoeAuthException(
                "Error while sending verification code: " +
                f"{response.status_code} {response.reason}: {response.json()}")
        return response.json()

    def login_using_verification_code(self, verification_code: str, mode: str, email: str = None, phone: str = None) -> str:
        if mode == "email":
            data = {
                "queryName": "SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation",
                "variables": {"verificationCode": verification_code, "emailAddress": email, "phoneNumber": None},
                "query": "mutation SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation(\n  $verificationCode: String!\n  $emailAddress: String\n  $phoneNumber: String\n) {\n  loginWithVerificationCode(verificationCode: $verificationCode, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n    status\n    errorMessage\n  }\n}\n"
            }
        elif mode == "phone":
            data = {
                "queryName": "SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation",
                "variables": {"verificationCode": verification_code, "emailAddress": None, "phoneNumber": phone},
                "query": "mutation SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation(\n  $verificationCode: String!\n  $emailAddress: String\n  $phoneNumber: String\n) {\n  loginWithVerificationCode(verificationCode: $verificationCode, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n    status\n    errorMessage\n  }\n}\n"
            }
        else:
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        response = self.session.post(self.auth_api_url, json=data)
        if response.status_code != 200:
            raise PoeAuthException(
                "Error while login in using verification code: " +
                f"{response.status_code} {response.reason}: {response.json()}")
        return self.session.cookies.get_dict().get("p-b")


@click.command()
@click.option("--email", help="User email address")
@click.option("--phone", help="User phone number")
@click.option("--mode", type=click.Choice(['email', 'phone']), default="email", help="Verification mode")
@click.option("--help", is_flag=True, help="Show help message")
def cli(email, phone, mode, help):
    if help:
        click.echo("Usage: poeauth [OPTIONS]")
        click.echo("Options:")
        click.echo("  --email TEXT  User email address")
        click.echo("  --phone TEXT  User phone number")
        click.echo("  --mode TEXT   Verification mode")
        click.echo("  --help        Show help message")
        return

    poeauth = PoeAuth()

    if email is None and phone is None:
        click.echo("Email address or phone number is required.")
        return

    try:
        if mode == "email":
            resp = poeauth.send_verification_code(email=email)
        elif mode == "phone":
            resp = poeauth.send_verification_code(phone=phone, mode="phone")
    except PoeAuthException as e:
        click.echo(f"Error sending verification code: {str(e)}")
        return

    verification_code = input(
        f"Enter the verification code sent to {email if email else phone}: ")

    try:
        if mode == "email":
            auth_session = poeauth.login_using_verification_code(
                verification_code=verification_code, mode="email", email=email)
        elif mode == "phone":
            auth_session = poeauth.login_using_verification_code(
                verification_code=verification_code, mode="phone", phone=phone)
    except PoeAuthException as e:
        click.echo(f"Authentication failed: {str(e)}")
        return

    click.echo(f"Successful authentication. Session cookie: {auth_session}")


if __name__ == "__main__":
    cli()
