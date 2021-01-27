import environ


@environ.config()
class AppConfig:
    @environ.config
    class Log:
        level = environ.var("INFO")
        format = environ.var(
            "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
        )

    log = environ.group(Log)

    @environ.config
    class S3:
        endpoint_url = environ.var(
            help="The S3 endpoint URL that bucket-helper will connect to"
        )
        bucket = environ.var(
            help="The bucket in the S3 instance that will be created",
        )
        access_key = environ.var(
            name="AWS_ACCESS_KEY_ID", help="The Access Key for the S3 instance"
        )
        secret_key = environ.var(
            name="AWS_SECRET_KEY_ID", help="The Secret Key for the S3 instance"
        )

    s3 = environ.group(S3)


if __name__ == "__main__":
    print(environ.generate_help(AppConfig, display_defaults=True))
