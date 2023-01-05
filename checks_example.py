# rename this checks.py

sites = [
    {
        # url to get
        'url': 'https://mysite.com',

        # expected status code
        'status': 200,

        # alert timeout
        'timeout': 2.0,

        # number of fails before sending alert
        'fails': 2,

        # emails to send alert to - use email to sms bridge here to get sms
        'emails': ['9999999999@vtext.com', 'me@gmail.com'],
    },
]
