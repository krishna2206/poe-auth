import logging

from playwright.sync_api._generated import Playwright


gql_queries = {
    "SendVerificationCodeForLoginMutation": """
        mutation MainSignupLoginSection_sendVerificationCodeMutation_Mutation(
            $emailAddress: String
            $phoneNumber: String
            $recaptchaToken: String
        ) {
            sendVerificationCode(
                verificationReason: login
                emailAddress: $emailAddress
                phoneNumber: $phoneNumber
                recaptchaToken: $recaptchaToken
            ) {
                status
                errorMessage
            }
        }
    """,
    "SignupWithVerificationCodeMutation": """
        mutation SignupOrLoginWithCodeSection_signupWithVerificationCodeMutation_Mutation(
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
                errorMessage
            }
        }
    """,
    "LoginWithVerificationCodeMutation": """
        mutation SignupOrLoginWithCodeSection_loginWithVerificationCodeMutation_Mutation(
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
                errorMessage
            }
        }
    """
}

logging.basicConfig()
logger = logging.getLogger()


class PoeAuthException(Exception):
    pass


class PoeAuth:
    def __init__(self, playwright: Playwright) -> None:
        self.browser = playwright.firefox.launch(headless=True)
        context = self.browser.new_context()
        self.api_req_context = context.request
        self.api_req_context_headers = {}
        self.current_page = context.new_page()

        self.login_url = "https://poe.com/login"
        self.gql_api_url = "https://poe.com/api/gql_POST"
        self.settings_url = "https://poe.com/api/settings"

        self.init_login_page()

    def init_login_page(self):
        self.current_page.goto(self.login_url)

    def send_verification_code(self, email: str = None, phone: str = None, mode: str = "email") -> dict:
        if mode not in ("email", "phone"):
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        logger.debug("Filling form...")
        if mode == "email":
            self.current_page.locator("button[class='Button_buttonBase__0QP_m Button_flat__1hj0f undefined']").click()
            self.current_page.fill("input[type='email']", email)
        else:
            self.current_page.fill("input[type='tel']", phone)

        logger.debug("Clicking send verification code button...")
        with self.current_page.expect_response(self.gql_api_url) as response_info:
            self.current_page.locator("button[class='Button_buttonBase__0QP_m Button_primary__pIDjn undefined']").click()
        self.api_req_context_headers = response_info.value.request.headers
        response = response_info.value.json()

        if response.get("data") is not None:
            error_message = response.get("data").get(
                "sendVerificationCode").get("errorMessage")
            status = response.get("data").get(
                "sendVerificationCode").get("status")
            if error_message is not None:
                raise PoeAuthException(
                    f"Error while sending verification code: {error_message}")
            if status == "success":
                return response_info.value.headers.get("set-cookie").split(";")[0].split("=")[1]
            return status
        raise PoeAuthException(
            f"Error while sending verification code: {response}")

    def __login_or_signup(
        self, action: str, verification_code: str, mode: str
    ) -> str:

        if mode not in ("email", "phone"):
            raise ValueError("Invalid mode. Must be 'email' or 'phone'.")

        logger.debug("Filling form using verification code...")
        self.current_page.fill("input[class='VerificationCodeInput_verificationCodeInput__YD3KV']", verification_code)
        with self.current_page.expect_response(self.gql_api_url) as response_info:
            logger.debug("Clicking verify button...")
            self.current_page.locator("button[class='Button_buttonBase__0QP_m Button_primary__pIDjn undefined']").click()
        response = response_info.value.json()

        if response.get("data") is not None:
            status = response.get("data").get(
                "loginWithVerificationCode" if action == "login"
                else "signupWithVerificationCode").get("status")

            if status != "success":
                raise PoeAuthException(
                    f"Error while login in using verification code: {status}")
            return response_info.value.headers.get("set-cookie").split(";")[0].split("=")[1]
        raise PoeAuthException(
            f"Error while login in using verification code: {response}")

    def signup_using_verification_code(
        self, verification_code: str, mode: str
    ) -> str:
        return self.__login_or_signup("signup", verification_code, mode)

    def login_using_verification_code(
        self, verification_code: str, mode: str
    ) -> str:
        return self.__login_or_signup("login", verification_code, mode)
