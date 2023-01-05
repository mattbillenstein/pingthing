# rename this checks.py

DEFAULTS = (
    ('fails', 2),
    ('status', 200),
    ('timeout', 5.0),
)

sites = [
    {
        # url to get
        'url': 'https://mysite.com',

        # expected status code - default 200
        'status': 200,

        # alert timeout - default 5s
        'timeout': 2.0,

        # number of fails before sending alert - default 2
        'fails': 2,

        # emails to send alert to - use email to sms bridge here to get sms
        'emails': ['9999999999@vtext.com', 'me@gmail.com'],
    },
]
