import re
import json
import logging
import hashlib
from pathlib import Path

import click
from requests import Session
from fake_useragent import UserAgent


parent_path = Path(__file__).resolve().parent
queries_path = parent_path / "graphql"
gql_queries = {}

logging.basicConfig()
logger = logging.getLogger()


def load_queries():
    for path in queries_path.iterdir():
        if path.suffix != ".graphql":
            continue
        with open(path) as f:
            gql_queries[path.stem] = f.read()


load_queries()


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

        self.form_key = self.__get_form_key()
        self.tchannel = self.__get_tchannel()

    # CTTO: https://github.com/ading2210/poe-api/commit/59597cfb4a9c81c93e879c985f5b617a74d07f85
    def __get_form_key(self) -> str:
        response = self.session.get(self.login_url)

        script_regex = r'<script>if\(.+\)throw new Error;(.+)</script>'
        script_text = re.search(script_regex, response.text).group(1)
        key_regex = r'var .="([0-9a-f]+)",'
        key_text = re.search(key_regex, script_text).group(1)
        cipher_regex = r'.\[(\d+)\]=.\[(\d+)\]'
        cipher_pairs = re.findall(cipher_regex, script_text)

        formkey_list = [""] * len(cipher_pairs)
        for pair in cipher_pairs:
            formkey_index, key_index = map(int, pair)
            formkey_list[formkey_index] = key_text[key_index]
        formkey = "".join(formkey_list)

        return formkey

    def __get_tchannel(self) -> str:
        response = self.session.get(self.settings_url)
        try:
            tchannel = response.json().get("tchannelData").get("channel")
        except Exception as e:
            raise PoeAuthException(f"Error while getting tchannel: {e}")
        return tchannel

    def __generate_payload(self, query_key: str, query_name: str, variables: dict) -> dict:
        return {
            "queryName": query_name,
            "query": gql_queries[query_key],
            "variables": variables
        }

    # Inspiration: https://github.com/ading2210/poe-api/pull/39
    def __generate_tag_id(self, form_key: str, payload: dict) -> str:
        payload = json.dumps(payload)

        base_string = payload + form_key + "WpuLMiXEKKE98j56k"

        return hashlib.md5(base_string.encode()).hexdigest()

    def send_verification_code(self, email: str = None, phone: str = None, mode: str = "email") -> dict:
        if mode not in ("email", "phone"):
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        payload = self.__generate_payload(
            query_key="SendVerificationCodeForLoginMutation",
            query_name="MainSignupLoginSection_sendVerificationCodeMutation_Mutation",
            variables={"emailAddress": email, "phoneNumber": None, "recaptchaToken": None} if mode == "email"
            else {"emailAddress": None, "phoneNumber": phone, "recaptchaToken": None}
        )
        tag_id = self.__generate_tag_id(
            form_key=self.form_key,
            payload=payload
        )

        logger.debug(f"Form key: {self.form_key}")
        logger.debug(f"Tchannel: {self.tchannel}")
        logger.debug(f"Tag ID: {tag_id}")

        self.session.headers.update({
            'Referer': 'https://poe.com/login',
            'Origin': 'https://poe.com',
            'Content-Type': 'application/json',
            'poe-formkey': self.form_key,
            'poe-tchannel': self.tchannel,
            'poe-tag-id': tag_id,
        })

        response = self.session.post(self.gql_api_url, json=payload).json()
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

        payload = self.__generate_payload(
            query_key="LoginWithVerificationCodeMutation" if action == "login"
            else "SignupWithVerificationCodeMutation",
            query_name="SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation" if action == "login"
            else "SignupOrLoginWithCodeSection_signupWithVerificationCodeMutation_Mutation",
            variables={"verificationCode": verification_code, "emailAddress": email, "phoneNumber": None} if mode == "email"
            else {"verificationCode": verification_code, "emailAddress": None, "phoneNumber": phone}
        )

        tag_id = self.__generate_tag_id(
            form_key=self.form_key,
            payload=payload
        )

        logger.debug(f"Form key: {self.form_key}")
        logger.debug(f"Tchannel: {self.tchannel}")
        logger.debug(f"Tag ID: {tag_id}")

        self.session.headers.update({
            'poe-tag-id': tag_id,
        })

        response = self.session.post(self.gql_api_url, json=payload).json()
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
