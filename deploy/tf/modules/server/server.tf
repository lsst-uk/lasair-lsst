# Create a floating IP if floating_ip is true
resource "openstack_networking_floatingip_v2" "floating_ip" {
  count = var.floating_ip ? 1 : 0
  pool = "external"
}

# Create an instance
resource "openstack_compute_instance_v2" "server" {
  name            = var.name
  flavor_id       = data.openstack_compute_flavor_v2.flavor.id
  key_pair        = var.keypair
  security_groups = var.security_groups

  # Boot from a volume
  block_device {
    uuid                  = data.openstack_images_image_v2.image.id
    source_type           = "image"
    volume_size           = var.root_vol_size
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }

  network {
    name = var.network
  }

  scheduler_hints {
    group = var.group_id
  }
}

data "openstack_networking_port_v2" "vm-port" {
  device_id  = openstack_compute_instance_v2.server.id
  network_id = openstack_compute_instance_v2.server.network.0.uuid
}

# Attach the floating IP if necessary
resource "openstack_networking_floatingip_associate_v2" "floating_ip" {
  count = var.floating_ip ? 1 : 0
  floating_ip = openstack_networking_floatingip_v2.floating_ip[0].address
  port_id     = data.openstack_networking_port_v2.vm-port.id
}

# Attach any extra networks
resource "openstack_compute_interface_attach_v2" "attachments" {
  count = length(var.extra_networks)
  instance_id = openstack_compute_instance_v2.server.id
  network_id  = data.openstack_networking_network_v2.extra_networks[count.index].id
}

# Create extra volumes	
resource "openstack_blockstorage_volume_v3" "extra_volume" {
  for_each    = var.extra_vol
  name        = each.key
  size        = each.value.size
  volume_type = each.value.type
}

# Attach the extra volume
resource "openstack_compute_volume_attach_v2" "attached" {
  for_each = "${openstack_blockstorage_volume_v3.extra_volume}" 
  instance_id = "${openstack_compute_instance_v2.server.id}"
  volume_id   = each.value.id
}

# Output the name
output "name" {
  value = var.name
}

# Output the private IP
output "private_ip" {
  value = openstack_compute_instance_v2.server.network.0.fixed_ip_v4
}

