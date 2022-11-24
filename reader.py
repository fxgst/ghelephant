class Reader:
    def __init__(self, data_path):
        self.data_path = data_path

    def read_lines(self, file_name):
        with open(f'{self.data_path}/{file_name}', 'r') as f:
            for l in f:
                yield l
