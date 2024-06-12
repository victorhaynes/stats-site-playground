# Ex. Compare 14.11.1 to 14.5.1 and determine which patch is "larger"
def compare_latest_version_to_last_saved_version(latest_version, last_saved_version):
    # Split the 2 patch versions into parts
    latest_parts = [int(part) for part in latest_version.split('.')]
    saved_parts = [int(part) for part in last_saved_version.split('.')]
    
    # Compare the chunks one by one
    for latest_part, saved_part in zip(latest_parts, saved_parts):
        if latest_part < saved_part:
            return False  # latest_version is less than last_saved_version
        elif latest_part > saved_part:
            return True   # latest_version is greater than last_saved_version
    
    # If all compared parts are equal, check if one version has more parts
    if len(latest_parts) <= len(saved_parts):
        return False # latest_version is less than or equal to last_saved_version
    else:
        return True   # latest_version is greater than last_saved_version
