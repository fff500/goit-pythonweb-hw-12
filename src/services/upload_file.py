import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the UploadFileService with Cloudinary configuration.

        Args:
            cloud_name (str): The Cloudinary cloud name.
            api_key (str): The Cloudinary API key.
            api_secret (str): The Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Create an access token for the user.

        Args:
            file: The file to upload.
            username (str): The username of the user.

        Returns:
            str: The URL of the uploaded file.
        """

        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            tags=["user_avatar", f"user_{username}"],
            overwrite=True,
        )
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
