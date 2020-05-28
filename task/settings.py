# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 如果是 163 改成 smtp.163.com
EMAIL_PORT = 465
EMAIL_HOST_USER = '1726740187@qq.com'  # 发送邮件的邮箱帐号
EMAIL_HOST_PASSWORD = 'ToberightCarefu1'  # 授权码,各邮箱的设置中启用smtp服务时获取
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# 这样收到的邮件，收件人处就会这样显示
# DEFAULT_FROM_EMAIL = '2333<'1504703554@qq.com>'
EMAIL_USE_SSL = True   # 使用ssl
# EMAIL_USE_TLS = False # 使用tls
# EMAIL_USE_SSL 和 EMAIL_USE_TLS 是互斥的，即只能有一个为 True
# override default config