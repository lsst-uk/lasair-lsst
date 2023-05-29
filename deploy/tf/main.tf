# Configure the OpenStack Provider
terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
  cloud  = "openstack" # cloud defined in cloud.yml file
}

# base name for the deployment
variable "base_name" {
  type = string
}

# map defining the instances to deploy
variable "instances" {
  type = map(any)
}

# list of extra networks
variable "extra_networks" {
  type = list(string)
  default = []
}

#      name: { get_param: OS::stack_name }
#      description: "Lasair shared filesystem"
#      access_rules: [{"access_level": "rw", "access_type": "cephx", "access_to": { get_param: share_user} }]
#      size: { get_param: share_size }
#      share_protocol: "CEPHFS"
#      share_type: "default"

# size of shared filesystem
variable "share_size" {
  type = number
}

# name of the share user
variable "share_user" {
  type = string
}

# name of the cephfs network
variable "share_network" {
  type = string
}

# get share network id
data "openstack_networking_network_v2" "share_network" {
  name = var.share_network
}

# create shared filesystem
resource "openstack_sharedfilesystem_share_v2" "share" {
  name             = "cephfs_share"
  description      = "Lasair shared filesystem"
  share_proto      = "CEPHFS"
  size             = var.share_size
  share_network_id = data.openstack_networking_network_v2.share_network.id
}

# create an access rule for the share
resource "openstack_sharedfilesystem_share_access_v2" "share_access" {
  share_id     = openstack_sharedfilesystem_share_v2.share.id
  access_type  = "cephx"
  access_to    = var.share_user
  access_level = "rw"
}

# output the export path
output "export_locations" {
  value = openstack_sharedfilesystem_share_v2.share.export_locations
}

# create a default servergroup for singleton instances
resource "openstack_compute_servergroup_v2" "group" {
  name     = "${var.base_name}-default"
  policies = ["soft-affinity"]
}

# iterate over instances map
# create a node-set for each entry
module "node-set" {
  for_each = var.instances 
  source = "./modules/node-set"
  name = "${var.base_name}-${each.key}"
  number = can(each.value.number) ? each.value.number : 1
  root_vol_size = can(each.value.root_volume_size) ? each.value.root_volume_size : 25
  extra_vol = can(each.value.extra_volumes) ? each.value.extra_volumes : {}
  default_group_id = openstack_compute_servergroup_v2.group.id
  floating_ip = can(each.value.floating_ip) ? each.value.floating_ip : false
  extra_networks = var.extra_networks
#  extra_vol = {
#    tmp = {
#      size = 5
#      type = "ceph-ssd"
#    },
#    db = {
#      size = each.value.volume_size
#      type = "ceph-hdd"
#    }
#  }
}

