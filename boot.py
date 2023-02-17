import storage

storage.remount("/", readonly=False,disable_concurrent_write_protection=False)

print("Succesfully Booted")