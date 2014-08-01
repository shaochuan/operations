#!/usr/bin/python
import sys
import json
import argparse
import boto.route53.connection

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Automation of dns setup')
  parser.add_argument('-c', '--conf', dest='conf', help='Config json file containing aws keys.')
  args = parser.parse_args()

  if not args.conf:
    parser.print_help()
    sys.exit(0)
  with open(args.conf) as confd:
    conf = json.load(confd)

  aws_access_key_id = conf['aws_access_key_id']
  aws_secret_access_key = conf['aws_secret_access_key']
  conn = boto.route53.connection.Route53Connection(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
