"""Configuration file for managing environment variables."""

import environ


@environ.config()
class AppConfig:
    """Application configuration object used for managing environment variables."""

    @environ.config
    class Log:
        """App configuration object used for managing logging settings."""

        level = environ.var("INFO")
        formatter = environ.var(
            "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
        )

    log = environ.group(Log)

    @environ.config
    class S3:
        """App configuration object used for managing s3 objects."""

        endpoint_url = environ.var(
            help="The S3 endpoint URL that bucket-helper will connect to"
        )

        @environ.config
        class Bucket:
            """App configuration object used for managing s3 bucket settings."""

            name = environ.var(
                help="The name of the bucket in the S3 instance that will be created",
            )
            public = environ.bool_var(
                False,
                help="Set the access policy for the bucket to public as a boolean value",
            )

            @environ.config
            class Topic:
                """App configuration object used for managing topic configurations for an s3 bucket."""

                name = environ.var(
                    None, help="Creates a notification topic for the bucket"
                )
                push_endpoint = environ.var(
                    None, help="The endpoint URL that the topic will push to"
                )

            topic = environ.group(Topic)

        bucket = environ.group(Bucket)

        access_key = environ.var(
            name="AWS_ACCESS_KEY_ID", help="The Access Key for the S3 instance"
        )
        secret_key = environ.var(
            name="AWS_SECRET_KEY_ID", help="The Secret Key for the S3 instance"
        )

    s3 = environ.group(S3)


if __name__ == "__main__":
    print(environ.generate_help(AppConfig, display_defaults=True))
