from configparser import ConfigParser

def read_and_validate_config(SERVER_CONFIG, config_file_path):
    SERVER_CONFIG.read(config_file_path)

    req_keys = ["grantroles", "serverid"]

    for section in SERVER_CONFIG.sections():
        section_obj = SERVER_CONFIG[section]

        for key in req_keys:
            if key not in section_obj:
                print(f"Missing key: {key} in section {section}")
                return False

        print(f"{section} config is valid!")

    return True

if __name__ == "__main__":
    if not read_and_validate_config(ConfigParser(), "bot/server_config.ini"):
        exit(1)
