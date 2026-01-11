from httpx_oauth.clients.google import GoogleOAuth2
from httpx_oauth.clients.github import GitHubOAuth2
from cnm_bookhub_be.settings import settings

# 1. Cấu hình Google Client
# LƯU Ý: Phần scopes này cực kỳ quan trọng. 
# Nếu thiếu, Google sẽ không trả về Email/Profile và gây lỗi GetIdEmailError.
google_oauth_client = GoogleOAuth2(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
)

# 2. Cấu hình GitHub Client
# GitHub thường không cần scopes quá phức tạp để login cơ bản.
github_oauth_client = GitHubOAuth2(
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
)