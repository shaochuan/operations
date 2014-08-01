#!/usr/bin/python

import sys
import json
import argparse
from ops import launch_spot_instance, wait_for_spot, set_public_ip
import boto.ec2.connection


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Automation of amazon instance launch')
  parser.add_argument('-n', dest='count', type=int, default=1, help='The number of machine to be launched')
  parser.add_argument('-c', '--conf', dest='conf', help='Config json file containing aws keys.')
  args = parser.parse_args()

  if not args.conf:
    parser.print_help()
    sys.exit(0)

  with open(args.conf) as confd:
    conf = json.load(confd)
  aws_access_key_id = conf['aws_access_key_id']
  aws_secret_access_key = conf['aws_secret_access_key']
  polling_interval = conf.get('polling_interval', 10)
  conn = boto.ec2.connection.EC2Connection(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

  try:
    requests = launch_spot_instance(conn,
      ami=conf['ami'],
      key_name=conf['key_name'],
      security_group_ids=conf['security_group_ids'],
      instance_type=conf['instance_type'],
      count=1)
    instance_ids = wait_for_spot(conn, requests, polling_interval=polling_interval)
    addrs = set_public_ip(conn, instance_ids)
  finally:
    conn.close()
