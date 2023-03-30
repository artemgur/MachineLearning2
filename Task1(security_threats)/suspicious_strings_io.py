import constants as const


def load():
    with open(const.suspicious_strings_file_path) as file:
        return [line.rstrip() for line in file]


def save(suspicious_strings):
    with open(const.suspicious_strings_file_path, 'w') as file:
        file.write('\n'.join(suspicious_strings))
