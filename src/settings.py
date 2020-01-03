import configparser

TEST = False
if TEST:
    import test.config_test as config
else:
    from src import config

# setup correct .ics file path in fb2cal .ini
if True:
    configuration = configparser.ConfigParser()
    configuration.read(config.config_dir)
    configuration.set("AUTH", "ics_file_path", config.ics_file_path)
    with open(config.config_dir, "w") as f:
        configuration.write(f)
