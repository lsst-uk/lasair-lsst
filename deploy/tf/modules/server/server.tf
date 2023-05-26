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
