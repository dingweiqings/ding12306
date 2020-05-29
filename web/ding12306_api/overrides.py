import os
from .settings import BASE_DIR
from .DisableCsrf import DisableCSRFCheck
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1','localhost']
REDIS_HSOT='127.0.0.1'
REDIS_DATABASE='2'
LOGIN_URL='/api/account/login/'
DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dingtest',             # 替换为自己的数据库名，请预先创建好编码为utf8mb4的数据库
        'USER': 'root',        # 数据库用户名
        'PASSWORD': '123456',  # 数据库密码
        'HOST': '10.10.10.70',        # 数据库地址
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES'
        }
    }
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['front/dist'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_admin',
    'rest_framework'
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ding12306_api.DisableCsrf.DisableCSRFCheck'
]
DEBUG_PROPAGATE_EXCEPTIONS=True
AUTH_USER_MODEL = "app_admin.Account"
LOGIN_URL = 'account/login/'
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + REDIS_HSOT + ":6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    #存储userSession
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REDIS_HSOT+":6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sms_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://" + REDIS_HSOT + ":6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# 保存 session数据到 Redis中
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "front/dist/static"),
    '/var/www/static/',
]

CORS_ORIGIN_WHITELIST = (
    "localhost:8080"
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'web.libs.utils.exception_handler'
}
USE_TZ = False