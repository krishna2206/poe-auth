import json
import click
from requests import Session
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class GraphQLQueries:
    login_with_verification_code_mutation = """
        mutation LoginWithVerificationCodeMutation(
        $verificationCode: String!
        $emailAddress: String
        $phoneNumber: String
    ) {
        loginWithVerificationCode(
            verificationCode: $verificationCode
            emailAddress: $emailAddress
            phoneNumber: $phoneNumber
        ) {
            status
        }
    }
    """
    signup_with_verification_code_mutation = """
        mutation SignupWithVerificationCodeMutation(
        $verificationCode: String!
        $emailAddress: String
        $phoneNumber: String
    ) {
        signupWithVerificationCode(
            verificationCode: $verificationCode
            emailAddress: $emailAddress
            phoneNumber: $phoneNumber
        ) {
            status
        }
    }
    """
    send_verification_code_mutation = "mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(\n $emailAddress: String\n $phoneNumber: String\n) {\n sendVerificationCode(verificationReason: login, emailAddress: $emailAddress, phoneNumber: $phoneNumber) {\n status\n errorMessage\n }\n}\n"


class PoeAuthException(Exception):
    pass


class PoeAuth:
    def __init__(self) -> None:
        self.session = Session()
        self.login_url = "https://poe.com/login"
        self.gql_api_url = "https://poe.com/api/gql_POST"
        self.settings_url = "https://poe.com/api/settings"
        self.session.headers = {
            "Host": "poe.com",
            "User-Agent": UserAgent(browsers=["edge", "chrome", "firefox"]).random,
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

    def __get_tchannel(self) -> str:
        response = self.session.get(self.settings_url)
        try:
            tchannel = response.json().get("tchannelData").get("channel")
        except Exception as e:
            raise PoeAuthException(f"Error while getting tchannel: {e}")
        return tchannel

    def send_verification_code(self, email: str = None, phone: str = None, mode: str = "email") -> dict:
        form_key = self.__get_form_key()
        tchannel = self.__get_tchannel()
        self.session.headers.update({
            'Referer': 'https://poe.com/login',
            'Origin': 'https://poe.com',
            'poe-formkey': form_key,
            'poe-tchannel': tchannel
        })

        if mode not in ("email", "phone"):
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        data = {
            "queryName": "MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
            "variables": {"emailAddress": email, "phoneNumber": None} if mode == "email"
            else {"emailAddress": None, "phoneNumber": phone},
            "query": GraphQLQueries.send_verification_code_mutation
        }

        response = self.session.post(self.gql_api_url, json=data).json()
        if response.get("data") is not None:
            error_message = response.get("data").get(
                "sendVerificationCode").get("errorMessage")
            status = response.get("data").get(
                "sendVerificationCode").get("status")
            if error_message is not None:
                raise PoeAuthException(
                    f"Error while sending verification code: {error_message}")
            return status
        raise PoeAuthException(
            f"Error while sending verification code: {response}")

    def __login_or_signup(
        self, action: str, verification_code: str, mode: str,
        email: str = None, phone: str = None,
    ) -> str:

        if mode not in ("email", "phone"):
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        data = {
            "variables": {
                "verificationCode": verification_code,
                "emailAddress": email, "phoneNumber": None} if mode == "email"
            else {
                "verificationCode": verification_code,
                "emailAddress": None, "phoneNumber": phone},
            "query": GraphQLQueries.signup_with_verification_code_mutation if action == "signup"
            else GraphQLQueries.login_with_verification_code_mutation
        }

        response = self.session.post(self.gql_api_url, json=data).json()
        if response.get("data") is not None:
            status = response.get("data").get(
                "loginWithVerificationCode" if action == "login"
                else "signupWithVerificationCode").get("status")

            if status != "success":
                raise PoeAuthException(
                    f"Error while login in using verification code: {status}")
            return self.session.cookies.get_dict().get("p-b")
        raise PoeAuthException(
            f"Error while login in using verification code: {response}")

    def signup_using_verification_code(
        self, verification_code: str, mode: str,
        email: str = None, phone: str = None
    ) -> str:
        return self.__login_or_signup("signup", verification_code, mode, email, phone)

    def login_using_verification_code(
        self, verification_code: str, mode: str,
        email: str = None, phone: str = None
    ) -> str:
        return self.__login_or_signup("login", verification_code, mode, email, phone)


@click.command()
@click.option("--email", help="User email address")
@click.option("--phone", help="User phone number")
@click.option("--help", is_flag=True, help="Show help message")
def cli(email, phone, help):
    if help:
        click.echo("Usage: poe-auth [OPTIONS]")
        click.echo("Options:")
        click.echo("  --email TEXT  User email address")
        click.echo("  --phone TEXT  User phone number")
        click.echo("  --help        Show help message")
        return

    poeauth = PoeAuth()

    if (email is None) and (phone is None):
        click.echo("Email address or phone number is required.")
        return

    try:
        if email:
            status = poeauth.send_verification_code(email=email)
        elif phone:
            status = poeauth.send_verification_code(phone=phone, mode="phone")
    except PoeAuthException as e:
        click.echo(str(e))
        return

    verification_code = input(
        f"Enter the verification code sent to {email if email else phone}: ")

    try:
        if email:
            if status == "user_with_confirmed_email_not_found":
                auth_session = poeauth.signup_using_verification_code(
                    verification_code=verification_code, mode="email", email=email)
            else:
                auth_session = poeauth.login_using_verification_code(
                    verification_code=verification_code, mode="email", email=email)
        elif phone:
            if status == "user_with_confirmed_phone_number_not_found":
                auth_session = poeauth.signup_using_verification_code(
                    verification_code=verification_code, mode="phone", phone=phone)
            else:
                auth_session = poeauth.login_using_verification_code(
                    verification_code=verification_code, mode="phone", phone=phone)
    except PoeAuthException as e:
        click.echo(str(e))
        return

    click.echo(f"Successful authentication. Session cookie: {auth_session}")


if __name__ == "__main__":
    cli()
