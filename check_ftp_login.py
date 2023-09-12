#!/usr/bin/python3
# nagios monitoring plugin for ftp (connect, login to user and list for files/dirs) - 2023 arekm
# GPLv3+

import argparse
import ftplib
import logging
import subprocess
import time

import nagiosplugin

_log = logging.getLogger('nagiosplugin')


class FTP(nagiosplugin.Resource):
    def __init__(self, args):
        self.args = args
        self.login_time = -1
        self.dir_time = -1
        self.total_time = -1
        self.dir_count = -1

    def ftp_connect(self, host, port, login, passwd, timeout, ssl=False):
        try:
            ftp = ftplib.FTP_TLS()
            if self.args.debug:
                ftp.set_debuglevel(2)

            stime = time.time()
            ftp.connect(host=host, port=port, timeout=timeout)
            ftp.login(user=login, passwd=passwd, secure=ssl)
            self.login_time = time.time() - stime

            if ssl:
                ftp.prot_p()

            dtime = time.time()
            mlsd_items = ftp.mlsd()
            dir_output = [ x for x in mlsd_items ]
            self.dir_time = time.time() - dtime
            self.dir_count = len(dir_output)

            ftp.quit()
            self.total_time = time.time() - stime
        except Exception as e:
            raise nagiosplugin.CheckError(
                'cannot check {host}:{port:d} ftp service ({etype}): {err}'.format(host=host, port=port, etype=type(e), err=e))

        return dir_output

    def probe(self):
        self.ftp_connect(host=self.args.hostname, port=self.args.port, login=self.args.username,
            passwd=self.args.password, ssl=self.args.ssl, timeout=self.args.timeout)

        return [nagiosplugin.Metric('total_time', self.total_time, min=0),
            nagiosplugin.Metric('login_time', self.login_time, min=0),
            nagiosplugin.Metric('dir_time', self.dir_time, min=0),
            nagiosplugin.Metric('dir_count', self.dir_count, min=0)]


class FTPSummary(nagiosplugin.Summary):
    def verbose(self, results):
        if 'total_time' in results:
            return 'ftp login time: {:.2f}s, dir time: {:.2f}s, total time: {:.2f}s, directory entries: {:d}'.format(results['total_time'].resource.login_time,
                results['total_time'].resource.dir_time, results['total_time'].resource.total_time, results['total_time'].resource.dir_count)
        return None

@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('-H', '--hostname', metavar='HOSTNAME',
                    required=True, help='Host name, IP Address'),
    argp.add_argument('-p', '--port', default=21,
                    help='Port number'),
    argp.add_argument('-S', '--ssl', default=True, action=argparse.BooleanOptionalAction,
                    help='Use TLS for connection'),
    argp.add_argument('-U', '--username', default="ftp",
                    help='Username'),
    argp.add_argument('-P', '--password', default="",
                    help='Password'),
    argp.add_argument('-w', '--total-warning', metavar='RANGE', default='',
                      help='return warning if total time is outside RANGE')
    argp.add_argument('-c', '--total-critical', metavar='RANGE', default='',
                      help='return critical if total time is outside RANGE')
    argp.add_argument('--fc', '--files-critical', metavar='FILES_COUNT', default='2:',
                      help='return critical if files count is outside FILES_COUNT')
    argp.add_argument('--fw', '--files-warning', '--warning', metavar='FILES_COUNT', default='0:',
                      help='return warning if files count is outside FILES_COUNT')
    argp.add_argument('-t', '--timeout', default=10,
                    help='abort execution after TIMEOUT seconds')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                    help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-D', '--debug', default=False, action=argparse.BooleanOptionalAction,
                    help='turn on debugging')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        FTP(args),
        nagiosplugin.ScalarContext('login_time', fmt_metric='Login time: {value:.2f}s'),
        nagiosplugin.ScalarContext('dir_time', fmt_metric='dir time: {value:.2f}s'),
        nagiosplugin.ScalarContext('total_time', args.total_warning, args.total_critical,
                                fmt_metric='Total time: {value:.2f}s'),
        nagiosplugin.ScalarContext('dir_count', args.fw, args.fc,
                                fmt_metric='Files and directories count: {value:d}'),
        FTPSummary())
    check.main(args.verbose, args.timeout)

if __name__ == '__main__':
    main()
