locals {
  group = "foo-default"
}

resource "openstack_compute_servergroup_v2" "group" {
  name     = local.group
  policies = ["soft-affinity"]
}

module "server" {
  source    = "../server"
  count     = var.number
  name      = (var.number > 1) ? "${var.name}-${count.index}" : var.name
  root_vol_size = var.root_vol_size
  extra_vol = var.extra_vol
  group_id  = openstack_compute_servergroup_v2.group.id
}
