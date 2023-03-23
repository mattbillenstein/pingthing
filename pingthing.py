#!/usr/bin/env python3

import logging
import smtplib
import ssl
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from importlib import reload

import config
import checks

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(funcName)s:%(lineno)d %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
log = logging.getLogger(__name__)

results = defaultdict(list)
alerted = {}

def alert(chk):
    url = chk['url']
    now = time.time()

    fails = []
    for result in results[url][-60:]:
        if result['status'] != chk['status'] or result['elapsed'] > chk['timeout']:
            fails.append(result)

    if len(fails) < chk['fails']:
        log.info('Supressing alert for fails %s ...', url)
        return

    cnt, last_ts = alerted.get(url, (0, 0.0))
    next_ts = last_ts + cnt * 60
    if now < next_ts:
        log.info('Supressing alert for %s ...', url)
        return

    log.info('Sending alert for %s to %s ...', url, ', '.join(chk['emails']))

    alerted[url] = (cnt+1, now)

    html = ''
    txt = f'Recent:\n\n'

    for result in reversed(fails[-3:]):
        ts = time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime(result['ts']))
        txt += f'{ts} Status: {result["status"]} {result["elapsed"]:.1f}s\n'

    result = results[url][-1]
    txt += f'\nResponse:\n{result["data"]}'

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f'{url} has failed {len(fails)} time{"s" if len(fails) > 1 else ""} in the last hour'
    msg["From"] = from_email = config.smtp['from_email']
    msg["To"] = ', '.join(chk['emails'])

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    if txt:
        msg.attach(MIMEText(txt, "plain"))
    if html:
        msg.attach(MIMEText(html, "html"))

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP(config.smtp['host'], config.smtp['port']) as server:
        server.starttls(context=context)
        server.login(config.smtp['username'], config.smtp['password'])

        # raises SMTPException in some cases...
        server.sendmail(from_email, chk['emails'], msg.as_string())

def check(chk):
    log.info('Check %s', chk['url'])
    start = time.time()
    url = chk['url']
    req = urllib.request.Request(url, headers={'User-Agent': 'https://github.com/mattbillenstein/pingthing v1.0'})

    try:
        res = urllib.request.urlopen(req, timeout=chk['timeout'])
        status = res.status
        data = res.read()
    except urllib.error.HTTPError as e:
        status = e.status
        data = e.read()
    except urllib.error.URLError as e:
        log.exception(e)
        status = 400
        if isinstance(e.reason, TimeoutError):
            status = 408
        elif isinstance(e.reason, ConnectionResetError):
            status = 444

    elapsed = time.time() - start

    results[url].append({'ts': start, 'elapsed': elapsed, 'status': status, 'data': data})
    if len(results[url]) >= 200:
        results[url][:] = results[url][-100:]

    if status != chk['status'] or elapsed > chk['timeout']:
        log.error('Failure %s status:%s data:%s', url, status, data)
        alert(chk)
    else:
        log.info('Success %s status:%s elapsed:%.1f', chk['url'], status, elapsed)

def main():
    while 1:
        start = time.time()

        reload(checks)
        for chk in checks.sites:
            # defaults
            chk = dict(chk)
            for k, v in checks.DEFAULTS:
                if k not in chk:
                    chk[k] = v

            try:
                check(chk)
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.exception(e)

        elapsed = time.time() - start
        if elapsed > 60.0:
            log.warning('Checks took more than 60s...')

        time.sleep(60 - time.time() % 60)

if __name__ == '__main__':
    main()
