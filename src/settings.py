TEST = True
if TEST:
    import test.config_test as config
else:
    from src import config