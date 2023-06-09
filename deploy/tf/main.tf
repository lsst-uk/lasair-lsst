######################################################################
# OpenStack provider

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

######################################################################
# Input variables

# base name for the deployment
variable "base_name" {
  type = string
}

# map defining the instances to deploy
variable "instances" {
  type = map(any)
}

# list of extra networks to add to all instances
variable "extra_networks" {
  type = list(string)
  default = []
}

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

variable "image_name" {
  type = string
}

######################################################################
# Data

# get share network id
data "openstack_networking_network_v2" "share_network" {
  name = var.share_network
}

######################################################################
# Top level resources

# create shared filesystem
resource "openstack_sharedfilesystem_share_v2" "share" {
  name             = "${var.base_name}"
  description      = "Lasair shared filesystem"
  share_proto      = "CEPHFS"
  size             = var.share_size
  share_type       = "default"
}

# create an access rule for the share
resource "openstack_sharedfilesystem_share_access_v2" "share_access" {
  share_id     = openstack_sharedfilesystem_share_v2.share.id
  access_type  = "cephx"
  access_to    = var.share_user
  access_level = "rw"
}

# create a default servergroup for singleton instances
resource "openstack_compute_servergroup_v2" "group" {
  name     = "${var.base_name}-default"
  policies = ["soft-affinity"]
}

######################################################################
# Instances

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
  flavor = can(each.value.flavor) ? each.value.flavor : "tiny"
  image_name = var.image_name
}

######################################################################
# Outputs

# output the export locations
output "export_locations" {
  value = openstack_sharedfilesystem_share_v2.share.export_locations
}

# output the private IPs
output "private_ips" {
  value = flatten([ for ns in module.node-set : ns.private_ips ])
}

