"""
Expiration warnings and deactivation for active resources 
    where a resource is a filter, watchlist, or watchmap
    Checks one or all resources for expiration nearer than DAYS days
    and if it finds them does action that can be email warning, 
    or expiration plus email confirmation.
    The action is taken of the expiration is less than DAYS in the future
    By default all resources are checked, or just one type of resource,
    or just one specific resource of given id (rid).

Usage:
    check_expire.py --action=<action> --days=<days> [--resource=<resource>] [--rid=<rid>] [--log]
    check_expire.py --list

Options:
     --list: List all the active resources
      --action=<action>: (set|warning|expiration)
        set: Choose set to set expiration for some days in the future
        warning: Choose warning to send email of upcoming expiration 
        expiration: Choose expiration to send email and deactivate
      --days=<days>: Days is number of days ahead for expiration
      --resource=<resource>: choose filter|watchlist|watchmap to run on only one kind of resource
      --rid=<rid> choose id for resource to run only on that

"""
import os, sys, math, time, smtplib, datetime, docopt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.append('../common')
import settings
sys.path.append('../common/src')
from src import db_connect

# What we should call the resource, then the database name of it, then the name of the identifier
resources = {
    'filter':    {'dbname':'myqueries',  'rid': 'mq_id'},
    'watchlist': {'dbname':'watchlists', 'rid': 'wl_id'},
    'watchmap':  {'dbname':'areas',      'rid': 'ar_id'},
}

# The emails we can send out
messages = {
'warning':
"""
Dear %s,
Your active Lasair %s will become inactive on %s without action from you, and there will be no further real-time matching of incoming alerts. This is to relieve pressure on the real-time pipeline. To keep your %s active for 180 days, go to %s then click "Settings", then "Save".  Questions to lasair-help@mlist.is.ed.ac.uk -- The Lasair Team
""",

'expiration':
"""
Dear %s,
Your active Lasair %s has recently expired and thus become inactive, and there will be no further matching of incoming alerts. To make your %s active again for 180 days, go to %s then click "Settings", "Active" or "Streaming", then "Save". Questions to lasair-help@mlist.is.ed.ac.uk -- The Lasair Team
""",
}

def log(out):
    global logfile
    if logfile:
        try:
            f = open(logfile, 'a')
        except:
            print("ERROR: Cannot open system logfile %s:%s" % (logfile, str(e)))
        f.write(out+'\n')
        f.close
    else:
        print(out)

def send_email(email, message, message_html=''):
#    print(email, message, message_html)
    msg = MIMEMultipart('alternative')

    msg['Subject'] = 'Lasair: Active resource becoming inactive'
    msg['From']    = 'lasair@lsst.ac.uk'
    msg['To']      = email

    msg.attach(MIMEText(message, 'plain'))
    if len(message_html) > 0:
        msg.attach(MIMEText(message_html, 'html'))
    s = smtplib.SMTP('localhost')
    s.sendmail('lasair@lsst.ac.uk', email, msg.as_string())
    s.quit()
    log('Email sent to %s' % email)

def list_resources(msl):
    """
    List all the active resources
    """
    global resources
    now = datetime.datetime.now()
    cursor = msl.cursor(buffered=True, dictionary=True)
    for rname,resource in resources.items():
        print('Active ', rname)
        query = 'SELECT %s as id, name, first_name, last_name, email, date_expire ' % resource['rid'] 
        query += 'FROM %s,auth_user WHERE auth_user.id=user AND active>0 ' % resource['dbname']
        query += 'ORDER BY  date_expire'
        cursor.execute(query)
        for row in cursor:
            name = '[%s %s]' % (row['first_name'], row['last_name'])
            until = row['date_expire'] - now
            print('   %5d expires %.1f days ahead %s %s' % (row['id'], until.days, name, row['name']))

def set_expire(msl, resource, daysAhead, rid=None):
    """
    Set the given resource expiration dates in the future
    if the resource id (rid) is None, it does all of them
    """
    expire = datetime.datetime.now() + datetime.timedelta(days=daysAhead)
    query = 'UPDATE %s SET date_expire="%s"' % (resource['dbname'], str(expire))
    if rid:
        query += ' WHERE %s=%s' % (resource['rid'], rid)
        print('Setting %s:%s expiry %d days ahead' % (resource['dbname'], rid, daysAhead))
    else:
        print('Setting all %s expiry %d days ahead' % (resource['dbname'], daysAhead))
    cursor = msl.cursor(buffered=True, dictionary=True)
    cursor.execute(query)
    msl.commit()

def make_inactive(msl, resource, rid):
    """
    The actual teeth of the thing. Switches the given resource to inactive.
    """
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'UPDATE %s SET active=0 where %s=%s'
    query = query % (resource['dbname'], resource['rid'], rid)
    cursor.execute(query)
    msl.commit()
    log('Made %s:%s inactive' % (resource['dbname'], rid))

def nice_date(dt):
    tok = str(dt).split()
    return tok[0]

def check_and_action(msl, rname, resource, action, daysAhead, rid=None):
    """
    Check all the given resources for a warning message of for actual expiration.
    if the resource id (rid) is None, it does all of them
    """
    if rid:
        log('Checking expiration for %s with %s, rid=%s' % (rname, action, rid))
    else:
        log('Checking expiration for %s with %s, rid=All' % (rname, action))
    timelimit = datetime.datetime.now() + datetime.timedelta(days=daysAhead)
    cursor = msl.cursor(buffered=True, dictionary=True)
    query = 'SELECT %s as id, name, first_name, last_name, email, date_expire ' % resource['rid'] 
    query += 'FROM %s,auth_user WHERE auth_user.id=user AND active>0 ' % resource['dbname']
    if rid:
        query += 'AND %s=%s' % (resource['rid'], rid)
    cursor.execute(query)
    for row in cursor:
        if row['date_expire'] and row['date_expire'] < timelimit:
            rid = row['id']
            log('expiry for %s:%s is after %d days ahead'% (rname, rid, daysAhead))
            name = '%s %s' % (row['first_name'], row['last_name'])

            url      = 'https://%s/%ss/%d/' % (settings.LASAIR_URL, rname, rid)
            url_html = '<a href="%s">%s</a>' % (url, url)
            message_fmt = messages[action]

            if action == 'expiration':
                message      = message_fmt % (name, rname, rname, url)
                message_html = message_fmt % (name, rname, rname, url_html)
                make_inactive(msl, resource, rid)
                send_email(row['email'], message, message_html)

            if action == 'warning':
                niceexpire = nice_date(row['date_expire'])
                message      = message_fmt % (name, rname, niceexpire, rname, url)
                message_html = message_fmt % (name, rname, niceexpire, rname, url_html)
                send_email(row['email'], message, message_html)

if __name__ == "__main__":
    global logfile
    args = docopt.docopt(__doc__)
    action = args['--action']
    rname  = args['--resource']
    rid    = args['--rid']

    if args['--log']:
        today = datetime.datetime.today().strftime('%Y%m%d')
        logfile = settings.SERVICES_LOG +'/'+ today + '.log'
    else:
        logfile = None
    
    msl = db_connect.remote()

    if args['--list']:
        list_resources(msl)
        sys.exit()

    daysAhead   = int(args['--days'])

    if action == 'set':
        if not rname:
            for  rname,resource in resources.items():
                set_expire(msl, resource, daysAhead, rid=rid)
        elif rname in resources:
            set_expire(msl, resources[rname], daysAhead, rid=rid)
        else:
            log('Resource name %s not recognised, must be in %s' % (rname, resources.keys()))

    elif action == 'warning' or action == 'expiration':
        if not rname:
            for  rname,resource in resources.items():
                check_and_action(msl, rname, resource, action, daysAhead)
        elif rname in resources:
            check_and_action(msl, rname, resources[rname], action, daysAhead, rid)
        else:
            log('Resource name %s not recognised, must be in %s' % (rname, resources.keys()))

    else:
        log('Action %s not recognised, must be in list|set|warning|expiration' % action)
