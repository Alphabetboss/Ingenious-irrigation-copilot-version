def system_ok(sensor_status, camera_status):
    if not sensor_status:
        return False
    if not camera_status:
        return False
    return True
