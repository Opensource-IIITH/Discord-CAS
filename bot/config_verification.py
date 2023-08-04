from configparser import ConfigParser

def read_and_validate_config(SERVER_CONFIG: ConfigParser, config_file_path):
    SERVER_CONFIG.read(config_file_path, encoding='utf-8')

    for section in SERVER_CONFIG.sections():
        section_obj = SERVER_CONFIG[section]
        req_keys = {"grantroles", "serverid"}
        all_keys = req_keys | {"deleteroles", "is_academic", "setrealname", "temproles"} #Add optional keys here

        for key in section_obj.keys():
            if key not in all_keys:
                print(f"Unknown key: {key} in section {section}")
                return False
            req_keys.discard(key)
        if len(req_keys)!= 0:
            print(f"Missing keys: {' ,'.join(req_keys)} in section {section}")
            return False
            
        print(f"{section} config is valid!")

    return True

if __name__ == "__main__":
    if not read_and_validate_config(ConfigParser(), "bot/server_config.ini"):
        exit(1)
