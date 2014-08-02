import time


def launch_spot_instance(conn, ami, key_name, security_group_ids, instance_type, subnet_id=None, count=1):
  """
  Launch spot instances

  :type conn: :class:`boto.ec2.connection.EC2Connection`
  :param conn: The ec2 connection

  :rtype: list
  :return: A list of :class:`boto.ec2.spotinstancerequest.SpotInstanceRequest`
  """
  history = conn.get_spot_price_history(instance_type=instance_type)
  prices = [r.price for r in history]
  prices.sort()
  bid_price = prices[len(prices) / 2]
  requests = conn.request_spot_instances(price=bid_price,
    key_name=key_name,
    image_id=ami,
    count=count,
    security_group_ids=security_group_ids,
    subnet_id=subnet_id,
    instance_type=instance_type)
  return requests


def wait_for_spot(conn, requests, polling_interval=10):
  """
  Wait for spot requests to become active

  :type conn: :class:`boto.ec2.connection.EC2Connection`
  :param conn: The ec2 connection

  :type requests: list
  :param requests: A list of :class:`boto.ec2.spotinstancerequest.SpotInstanceRequest`

  :type polling_interval: int
  :param polling_interval: polling interval in seconds

  :rtype: list
  :return: a list of instance ids
  """
  print [r.state for r in requests]
  time.sleep(polling_interval)
  while any([r.state != u'active' for r in requests]):
    requests = conn.get_all_spot_instance_requests(map(lambda r: r.id, requests))
    print [r.state for r in requests]
    time.sleep(polling_interval)
  return [r.instance_id for r in requests]


def wait_for_instances(conn, instance_ids, polling_interval=10):
  """
  Wait for instances to become 'running'

  :type conn: :class:`boto.ec2.connection.EC2Connection`
  :param conn: The ec2 connection

  :type instance_ids: list
  :param instance_ids: A list of instance ids.

  :type polling_interval: int
  :param polling_interval: polling interval in seconds

  :rtype: None
  :return: None
  """
  status = conn.get_all_instance_status(instance_ids)
  print [s.instance_status.status for s in status]
  while any([s.instance_status.status != u'ok']):
    time.sleep(polling_interval)
    status = conn.get_all_instance_status(instance_ids)
    print [s.instance_status.status for s in status]


def set_public_ip(conn, instance_ids):
  """
  Setup elastic ip for created instances.

  :type conn: :class:`boto.ec2.connection.EC2Connection`
  :param conn: The ec2 connection

  :type requests: list
  :param requests: A list of instance ids
  """
  addrs = conn.get_all_addresses()
  for addr, instance_id in zip(addrs, instance_ids):
    addr.associate(instance_id)
