class Options:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Options, cls).__new__(cls)
            cls._instance.tag = False
            # Import notebook name
            cls._instance.import_notebook_name = False
        return cls._instance