import click
from playwright.sync_api import sync_playwright

from poe_auth.V1 import PoeAuth as PoeAuthV1, PoeAuthException as PoeAuthExceptionV1
from poe_auth.V2 import PoeAuth as PoeAuthV2, PoeAuthException as PoeAuthExceptionV2


def cli_V1(email, phone):
    poeauth = PoeAuthV1()

    if (email is None) and (phone is None):
        click.echo("Email address or phone number is required.")
        return

    try:
        if email:
            status = poeauth.send_verification_code(email=email)
        elif phone:
            status = poeauth.send_verification_code(phone=phone, mode="phone")
    except PoeAuthExceptionV1 as e:
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
    except PoeAuthExceptionV1 as e:
        click.echo(str(e))
        return

    click.echo(f"Successful authentication. Session cookie: {auth_session}")


def cli_V2(email, phone):
    with sync_playwright() as playwright:
        poeauth = PoeAuthV2(playwright)

        if (email is None) and (phone is None):
            click.echo("Email address or phone number is required.")
            return

        try:
            if email:
                status = poeauth.send_verification_code(email=email)
            elif phone:
                status = poeauth.send_verification_code(phone=phone, mode="phone")
        except PoeAuthExceptionV2 as e:
            click.echo(str(e))
            return

        verification_code = input(
            f"Enter the verification code sent to {email if email else phone}: ")

        try:
            if email:
                if status == "user_with_confirmed_email_not_found":
                    auth_session = poeauth.signup_using_verification_code(
                        verification_code=verification_code, mode="email")
                else:
                    auth_session = poeauth.login_using_verification_code(
                        verification_code=verification_code, mode="email")
            elif phone:
                if status == "user_with_confirmed_phone_number_not_found":
                    auth_session = poeauth.signup_using_verification_code(
                        verification_code=verification_code, mode="phone")
                else:
                    auth_session = poeauth.login_using_verification_code(
                        verification_code=verification_code, mode="phone")
        except PoeAuthExceptionV2 as e:
            click.echo(str(e))
            return

        click.echo(f"Successful authentication. Session cookie: {auth_session}")


@click.command()
@click.option("--email", help="User email address")
@click.option("--phone", help="User phone number")
@click.option("--help", is_flag=True, help="Show help message")
@click.option("--browser", is_flag=True, help="Use browser")
def cli(email, phone, help, browser):
    if help:
        click.echo("Usage: poe-auth [OPTIONS]")
        click.echo("Options:")
        click.echo("  --email TEXT  User email address")
        click.echo("  --phone TEXT  User phone number")
        click.echo("  --help        Show help message")
        click.echo("  --browser     Use browser")
        return

    if browser:
        cli_V2(email, phone)
    else:
        cli_V1(email, phone)


if __name__ == "__main__":
    cli()