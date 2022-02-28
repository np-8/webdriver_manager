import winreg, os

roots_hives = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_PERFORMANCE_DATA": winreg.HKEY_PERFORMANCE_DATA,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
    "HKEY_DYN_DATA": winreg.HKEY_DYN_DATA
}

def parse_key(key):
    key = key.upper()
    parts = key.split('\\')
    root_hive_name = parts[0]
    root_hive = roots_hives.get(root_hive_name)
    partial_key = '\\'.join(parts[1:])

    if not root_hive:
        raise Exception('root hive "{}" was not found'.format(root_hive_name))

    return partial_key, root_hive


def get_sub_keys(key):
    partial_key, root_hive = parse_key(key)

    with winreg.ConnectRegistry(None, root_hive) as reg:
        with winreg.OpenKey(reg, partial_key) as key_object:
            sub_keys_count, values_count, last_modified = QueryInfoKey(key_object)
            try:
                for i in range(sub_keys_count):
                    sub_key_name = winreg.EnumKey(key_object, i)
                    yield sub_key_name
            except WindowsError:
                pass


def get_values(key, fields):
    partial_key, root_hive = parse_key(key)

    with winreg.ConnectRegistry(None, root_hive) as reg:
        with winreg.OpenKey(reg, partial_key) as key_object:
            data = {}
            for field in fields:
                try:
                    value, type = winreg.QueryValueEx(key_object, field)
                    data[field] = value
                except WindowsError:
                    pass

            return data


def get_value(key, field):
    values = get_values(key, [field])
    return values.get(field)


def join(path, *paths):
    path = path.strip('/\\')
    paths = map(lambda x: x.strip('/\\'), paths)
    paths = list(paths)
    result = os.path.join(path, *paths)
    result = result.replace('/', '\\')
    return result
    
def get_chrome_version():
    for key, field in (
        (r"HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\BLBeacon", "version"),
        (r"HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome", "version"),
    ):

        try:
            return get_value(key, field)
        except FileNotFoundError:
            continue
    return ''